#!/usr/bin/env python3
from __future__ import annotations

import concurrent.futures
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from urisys.http_server import create_server  # noqa: E402


def write_mock_pack(workdir: Path) -> tuple[Path, Path]:
    package_dir = workdir / "urisys_concurrency_mock"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "handlers.py").write_text(
        textwrap.dedent(
            """
            from __future__ import annotations

            import os
            import threading
            import time
            from typing import Any


            def sleep_task(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
                delay = float(payload.get("delay", 0.25))
                time.sleep(delay)
                variables = context.get("variables") or {}
                return {
                    "adapter": "mock",
                    "delay": delay,
                    "pid": os.getpid(),
                    "task": variables.get("task"),
                    "thread": threading.get_ident(),
                    "worker": payload.get("worker"),
                }
            """
        ).lstrip(),
        encoding="utf-8",
    )
    manifest = workdir / "manifest.yaml"
    manifest.write_text(
        textwrap.dedent(
            """
            id: urisys-concurrency-mock
            version: 1
            scheme: demo

            uri_patterns:
              - pattern: demo://task/{task}/command/sleep
                kind: command
                operation: sleep_task
                command_type: demo.v1.SleepTaskCommand
                success_event_type: demo.v1.TaskSleptEvent
                side_effects: true
                approval: required

            handlers:
              python:
                sleep_task: python://urisys_concurrency_mock.handlers:sleep_task
            """
        ).lstrip(),
        encoding="utf-8",
    )
    flow = workdir / "threaded-flow.uri.flow.yaml"
    flow.write_text(
        textwrap.dedent(
            """
            flow:
              id: threaded-flow
            defaults:
              approved: true
              environment: mock
            do:
              - demo://task/flow-step-a/command/sleep:
                  delay: 0.25
                  worker: flow-a
              - demo://task/flow-step-b/command/sleep:
                  delay: 0.25
                  worker: flow-b
            """
        ).lstrip(),
        encoding="utf-8",
    )
    return manifest, flow


def post_call(port: int, worker: int, delay: float) -> dict[str, Any]:
    body = {
        "uri": f"demo://task/http-{worker}/command/sleep",
        "payload": {"delay": delay, "worker": worker},
        "context": {"approved": True, "environment": "mock"},
    }
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}/uri/call",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def run_http_thread_smoke(manifest: Path, events_path: Path) -> dict[str, Any]:
    server = create_server("127.0.0.1", 0, packs=str(manifest), events_path=str(events_path))
    port = int(server.server_address[1])
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    workers = 6
    delay = 0.35
    started = time.perf_counter()
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(lambda i: post_call(port, i, delay), range(workers)))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    elapsed = time.perf_counter() - started
    failed = [item for item in results if not item.get("ok")]
    if failed:
        raise RuntimeError(f"HTTP /uri/call failed: {failed!r}")
    threads = {item.get("result", {}).get("thread") for item in results}
    serial_floor = workers * delay
    if len(threads) < 2 or elapsed >= serial_floor * 0.9:
        raise RuntimeError(
            "HTTP smoke did not show concurrent handling "
            f"(threads={sorted(threads)}, elapsed={elapsed:.3f}s, serial_floor={serial_floor:.3f}s)"
        )
    return {
        "ok": True,
        "calls": workers,
        "handler_threads": len(threads),
        "elapsed_seconds": round(elapsed, 3),
        "serial_floor_seconds": round(serial_floor, 3),
    }


def cli_env(workdir: Path) -> dict[str, str]:
    env = os.environ.copy()
    pythonpath = [str(workdir), str(SRC)]
    if env.get("PYTHONPATH"):
        pythonpath.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)
    return env


def run_flow_process(index: int, manifest: Path, flow: Path, workdir: Path) -> dict[str, Any]:
    command = [
        sys.executable,
        "-m",
        "urisys.bootstrap",
        "--packs",
        str(manifest),
        "--events",
        str(workdir / f"flow-{index}.events.jsonl"),
        "flow",
        str(flow),
        "--approve",
        "--environment",
        "mock",
    ]
    started = time.perf_counter()
    proc = subprocess.run(
        command,
        cwd=str(ROOT),
        env=cli_env(workdir),
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    elapsed = time.perf_counter() - started
    if proc.returncode != 0:
        raise RuntimeError(
            f"flow process {index} failed with exit {proc.returncode}\n"
            f"stdout:\n{proc.stdout}\n"
            f"stderr:\n{proc.stderr}"
        )
    data = json.loads(proc.stdout)
    if not data.get("ok"):
        raise RuntimeError(f"flow process {index} returned not ok: {data!r}")
    return {
        "index": index,
        "elapsed_seconds": round(elapsed, 3),
        "steps": len(data.get("results") or []),
    }


def run_flow_process_smoke(manifest: Path, flow: Path, workdir: Path) -> dict[str, Any]:
    workers = 3
    started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda i: run_flow_process(i, manifest, flow, workdir), range(workers)))
    elapsed = time.perf_counter() - started
    summed = sum(item["elapsed_seconds"] for item in results)
    if elapsed >= summed * 0.75:
        raise RuntimeError(
            "flow process smoke did not show concurrent execution "
            f"(wall={elapsed:.3f}s, summed_process_time={summed:.3f}s)"
        )
    return {
        "ok": True,
        "processes": workers,
        "elapsed_seconds": round(elapsed, 3),
        "summed_process_seconds": round(summed, 3),
        "results": results,
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="urisys-threaded-example-") as tmp:
        workdir = Path(tmp)
        sys.path.insert(0, str(workdir))
        manifest, flow = write_mock_pack(workdir)
        summary = {
            "http_uri_calls": run_http_thread_smoke(manifest, workdir / "http.events.jsonl"),
            "cli_flow_processes": run_flow_process_smoke(manifest, flow, workdir),
        }
    print(json.dumps({"ok": True, **summary}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
