#!/usr/bin/env python3
"""Run urisys Docker/RDP test sessions with screenshots, logs, and per-session reports.

Usage:
  python3 scripts/run_test_sessions.py
  python3 scripts/run_test_sessions.py --sessions urirdp-mock,urirdp-real
  python3 scripts/run_test_sessions.py --output output/test-sessions
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
REPORT_SCRIPT = ROOT / "scripts" / "session_report.py"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _run_id() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def _host_id() -> str:
    import platform

    return f"{socket.gethostname()} ({platform.system()} {platform.machine()})"


def _http_json(
    method: str,
    url: str,
    body: dict | None = None,
    timeout: float = 120.0,
    *,
    retries: int = 5,
    retry_delay: float = 2.0,
) -> dict[str, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    last_err = ""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ConnectionResetError) as exc:
            last_err = str(exc)
            if attempt + 1 < retries:
                time.sleep(retry_delay)
                continue
            raise RuntimeError(f"HTTP {method} {url} failed: {last_err}") from exc
    raise RuntimeError(f"HTTP {method} {url} failed: {last_err}")


def _wait_health(url: str, attempts: int = 90, delay: float = 1.0) -> dict[str, Any]:
    last_err = ""
    for _ in range(attempts):
        try:
            return _http_json("GET", url, retries=3, retry_delay=1.0)
        except RuntimeError as exc:
            last_err = str(exc)
            time.sleep(delay)
    raise RuntimeError(f"health timeout for {url}: {last_err}")


def _compose_cmd(*parts: str, compose_file: Path | None = None) -> list[str]:
    cmd = ["docker", "compose"]
    if compose_file:
        cmd.extend(["-f", str(compose_file)])
    cmd.extend(parts)
    if parts and parts[0] in {"up", "down"}:
        cmd.append("--remove-orphans")
    return cmd


def _prepare_urirdp_data(pkg: Path) -> None:
    data = pkg / "data"
    data.mkdir(parents=True, exist_ok=True)
    for name in ("events.jsonl", "test-events.jsonl"):
        p = data / name
        if p.is_file():
            p.write_text("", encoding="utf-8")
    shots = data / "screenshots"
    shots.mkdir(parents=True, exist_ok=True)
    for png in shots.glob("*.png"):
        png.unlink(missing_ok=True)


def _sleep_ports() -> None:
    time.sleep(3)


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _run_cmd(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    log_file: Path | None = None,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        env=merged,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as f:
            f.write(f"$ {' '.join(cmd)}\n")
            if proc.stdout:
                f.write(proc.stdout)
            if proc.stderr:
                f.write("\n--- stderr ---\n")
                f.write(proc.stderr)
            f.write(f"\n--- exit {proc.returncode} ---\n")
    return proc


def _write_meta(session_dir: Path, **kwargs: Any) -> None:
    meta_path = session_dir / "meta.json"
    meta = _read_meta(meta_path)
    meta.update(kwargs)
    _save_json(meta_path, meta)


def _read_meta(path: Path) -> dict[str, Any]:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _finalize_session(session_dir: Path, started_at: str, exit_code: int, steps: list[dict[str, Any]]) -> int:
    finished = _now_iso()
    t0 = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    t1 = datetime.fromisoformat(finished.replace("Z", "+00:00"))
    status = "pass" if exit_code == 0 and all(s.get("status") == "pass" for s in steps) else "fail"
    _write_meta(
        session_dir,
        finished_at=finished,
        duration_s=max(0.0, (t1 - t0).total_seconds()),
        exit_code=exit_code,
        status=status,
        steps=steps,
    )
    subprocess.run(
        [sys.executable, str(REPORT_SCRIPT), "generate", str(session_dir)],
        check=False,
    )
    return 0 if status == "pass" else 1


def _docker_logs(service: str, compose_file: Path | None, cwd: Path, out: Path) -> None:
    cmd = ["docker", "compose"]
    if compose_file:
        cmd.extend(["-f", str(compose_file)])
    cmd.extend(["logs", "--tail=200", service])
    proc = _run_cmd(cmd, cwd=cwd)
    out.write_text((proc.stdout or "") + (proc.stderr or ""), encoding="utf-8")


def _copy_container_file(container: str, src: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["docker", "cp", f"{container}:{src}", str(dest)],
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0 and dest.is_file()


def _copy_host_screenshot(src: Path, session_dir: Path, name: str) -> str | None:
    if not src.is_file():
        return None
    dest = session_dir / "screenshots" / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return str(dest.relative_to(session_dir))


def session_pytest_urirdp(session_dir: Path) -> int:
    started = _now_iso()
    _write_meta(
        session_dir,
        session_id=session_dir.name,
        session_name="pytest-urirdp",
        suite="unit",
        started_at=started,
        host=_host_id(),
    )
    log = session_dir / "session.log"
    pkg = ROOT / "urirdp-docker"
    proc = _run_cmd([sys.executable, "-m", "pytest", "-q"], cwd=pkg, log_file=log)
    steps = [{"name": "pytest", "status": "pass" if proc.returncode == 0 else "fail", "detail": proc.stderr[-500:] if proc.returncode else ""}]
    return _finalize_session(session_dir, started, proc.returncode, steps)


def session_pytest_urisys(session_dir: Path) -> int:
    started = _now_iso()
    _write_meta(session_dir, session_id=session_dir.name, session_name="pytest-urisys", suite="unit", started_at=started, host=_host_id())
    log = session_dir / "session.log"
    proc = _run_cmd([sys.executable, "-m", "pytest", "tests/", "-q"], cwd=ROOT, log_file=log)
    steps = [{"name": "pytest", "status": "pass" if proc.returncode == 0 else "fail"}]
    return _finalize_session(session_dir, started, proc.returncode, steps)


def session_pytest_urisys_node(session_dir: Path) -> int:
    started = _now_iso()
    _write_meta(session_dir, session_id=session_dir.name, session_name="pytest-urisys-node", suite="unit", started_at=started, host=_host_id())
    log = session_dir / "session.log"
    pkg = ROOT / "urisys-node"
    proc = _run_cmd([sys.executable, "-m", "pytest", "-q"], cwd=pkg, log_file=log)
    steps = [{"name": "pytest", "status": "pass" if proc.returncode == 0 else "fail"}]
    return _finalize_session(session_dir, started, proc.returncode, steps)


def session_urirdp_mock_docker(session_dir: Path) -> int:
    started = _now_iso()
    port = 8795
    pkg = ROOT / "urirdp-docker"
    _write_meta(
        session_dir,
        session_id=session_dir.name,
        session_name="urirdp-mock-docker",
        suite="docker-smoke",
        started_at=started,
        host=_host_id(),
        ports={"uri": port},
    )
    log = session_dir / "session.log"
    steps: list[dict[str, Any]] = []
    code = 0

    _prepare_urirdp_data(pkg)
    _sleep_ports()
    _run_cmd(_compose_cmd("down", "-v"), cwd=pkg, log_file=log)
    up = _run_cmd(_compose_cmd("up", "-d", "--build", "urirdp"), cwd=pkg, log_file=log)
    if up.returncode != 0:
        steps.append({"name": "compose-up", "status": "fail"})
        _docker_logs("urirdp", None, pkg, session_dir / "docker-logs.txt")
        return _finalize_session(session_dir, started, up.returncode, steps)

    try:
        health = _wait_health(f"http://127.0.0.1:{port}/health")
        _save_json(session_dir / "responses" / "01-health.json", health)
        steps.append({"name": "health", "status": "pass", "uri": f"http://127.0.0.1:{port}/health"})
        time.sleep(3)

        routes = _http_json("GET", f"http://127.0.0.1:{port}/uri/routes")
        _save_json(session_dir / "responses" / "02-routes.json", routes)
        steps.append({"name": "routes", "status": "pass"})

        click = _http_json(
            "POST",
            f"http://127.0.0.1:{port}/uri/call",
            {
                "uri": "kvm://local/task/command/click-text",
                "payload": {"text": "OK"},
                "context": {"approved": True, "dry_run": True},
            },
        )
        _save_json(session_dir / "responses" / "03-click-dry-run.json", click)
        steps.append(
            {
                "name": "click-dry-run",
                "status": "pass" if click.get("ok") else "fail",
                "uri": "kvm://local/task/command/click-text",
                "metrics": {"dry_run": True},
            }
        )
        if not click.get("ok"):
            code = 1
    except Exception as exc:
        steps.append({"name": "mock-smoke", "status": "fail", "detail": str(exc)})
        code = 1
    finally:
        _docker_logs("urirdp", None, pkg, session_dir / "docker-logs.txt")
        _copy_container_file("urirdp-gui", "/opt/urirdp/data/events.jsonl", session_dir / "events.jsonl")
        _run_cmd(_compose_cmd("down", "-v"), cwd=pkg, log_file=log)

    return _finalize_session(session_dir, started, code, steps)


def session_urirdp_real_docker(session_dir: Path) -> int:
    started = _now_iso()
    port = 8795
    pkg = ROOT / "urirdp-docker"
    container = "urirdp-gui"
    _write_meta(
        session_dir,
        session_id=session_dir.name,
        session_name="urirdp-real-docker",
        suite="docker-real",
        started_at=started,
        host=_host_id(),
        ports={"uri": port, "rdp": 3389},
    )
    log = session_dir / "session.log"
    steps: list[dict[str, Any]] = []
    code = 0
    display = ":10"
    xauth = ""

    env = {"URISYS_ALLOW_REAL": "1"}
    _prepare_urirdp_data(pkg)
    _sleep_ports()
    _run_cmd(_compose_cmd("down", "-v"), cwd=pkg, log_file=log, env=env)
    up = _run_cmd(_compose_cmd("up", "-d", "--build", "urirdp"), cwd=pkg, log_file=log, env=env)
    if up.returncode != 0:
        steps.append({"name": "compose-up", "status": "fail"})
        return _finalize_session(session_dir, started, up.returncode, steps)

    try:
        health = _wait_health(f"http://127.0.0.1:{port}/health")
        _save_json(session_dir / "responses" / "01-health.json", health)
        steps.append({"name": "health", "status": "pass"})
        time.sleep(5)

        boot = _run_cmd(
            ["docker", "exec", container, "bash", "/opt/urirdp/docker/bootstrap-rdp-session.sh"],
            log_file=log,
        )
        steps.append({"name": "bootstrap-rdp", "status": "pass" if boot.returncode == 0 else "fail"})
        if boot.returncode != 0:
            raise RuntimeError("bootstrap-rdp-session failed")

        disp_proc = _run_cmd(
            ["docker", "exec", container, "bash", "-lc", "grep ^DISPLAY= /tmp/urirdp-display.env | cut -d= -f2"],
        )
        display = (disp_proc.stdout or ":10").strip() or ":10"
        xauth_proc = _run_cmd(
            ["docker", "exec", container, "bash", "-lc", "grep ^XAUTHORITY= /tmp/urirdp-display.env | cut -d= -f2"],
        )
        xauth = (xauth_proc.stdout or "").strip()
        _write_meta(session_dir, display=display, xauthority=xauth)

        ctx = {"approved": True, "allow_real": True, "display": display, "xauthority": xauth}

        shot = _http_json(
            "POST",
            f"http://127.0.0.1:{port}/uri/call",
            {"uri": "kvm://local/monitor/primary/query/screenshot", "payload": {}, "context": ctx},
        )
        _save_json(session_dir / "responses" / "02-screenshot.json", shot)
        _copy_container_file(container, "/opt/urirdp/data/screenshots/latest.png", session_dir / "screenshots" / "02-screenshot.png")
        captured = (shot.get("result") or {}).get("captured")
        steps.append(
            {
                "name": "screenshot",
                "status": "pass" if shot.get("ok") and captured else "fail",
                "uri": "kvm://local/monitor/primary/query/screenshot",
                "metrics": {"captured": captured, "driver": (shot.get("result") or {}).get("driver")},
                "screenshot": "screenshots/02-screenshot.png" if captured else None,
            }
        )

        ocr = _http_json(
            "POST",
            f"http://127.0.0.1:{port}/uri/call",
            {"uri": "ocr://local/image/latest/query/text", "payload": {}, "context": ctx},
        )
        _save_json(session_dir / "responses" / "03-ocr.json", ocr)
        text = ((ocr.get("result") or {}).get("text") or "").upper()
        has_ok = "OK" in text
        steps.append(
            {
                "name": "ocr",
                "status": "pass" if ocr.get("ok") and has_ok else "fail",
                "uri": "ocr://local/image/latest/query/text",
                "metrics": {"engine": (ocr.get("result") or {}).get("engine"), "has_ok": has_ok},
            }
        )

        click = _http_json(
            "POST",
            f"http://127.0.0.1:{port}/uri/call",
            {
                "uri": "kvm://local/task/command/click-text",
                "payload": {"text": "OK"},
                "context": ctx,
            },
            timeout=180.0,
        )
        _save_json(session_dir / "responses" / "04-click-text.json", click)
        _copy_container_file(container, "/opt/urirdp/data/screenshots/latest.png", session_dir / "screenshots" / "04-after-click.png")
        result = click.get("result") or {}
        clicked = result.get("clicked")
        driver = (result.get("click") or {}).get("driver")
        steps.append(
            {
                "name": "click-text",
                "status": "pass" if click.get("ok") and clicked and driver == "xdotool" else "fail",
                "uri": "kvm://local/task/command/click-text",
                "metrics": {"clicked": clicked, "driver": driver, "reason": (result.get("llm") or {}).get("reason")},
                "screenshot": "screenshots/04-after-click.png",
            }
        )

        flow = _run_cmd(
            [
                "docker",
                "exec",
                "-e",
                "URISYS_ALLOW_REAL=1",
                container,
                "urisys-rdp",
                "--config",
                "/opt/urirdp/config/rdp-kvm-profile.json",
                "flow",
                "/opt/urirdp/flows/real-rdp-click-text.uri.flow.yaml",
                "--approve",
                "--allow-real",
                "--display",
                display,
            ],
            log_file=log,
        )
        flow_steps = json.loads(flow.stdout) if flow.stdout.strip().startswith("[") else []
        _save_json(session_dir / "responses" / "05-flow.json", flow_steps)
        flow_ok = flow.returncode == 0 and all(s.get("ok") for s in flow_steps)
        steps.append({"name": "flow", "status": "pass" if flow_ok else "fail", "metrics": {"steps": len(flow_steps)}})

        if any(s["status"] == "fail" for s in steps):
            code = 1
    except Exception as exc:
        steps.append({"name": "real-docker", "status": "fail", "detail": str(exc)})
        code = 1
    finally:
        _docker_logs("urirdp", None, pkg, session_dir / "docker-logs.txt")
        _copy_container_file(container, "/opt/urirdp/data/events.jsonl", session_dir / "events.jsonl")
        _run_cmd(_compose_cmd("down", "-v"), cwd=pkg, log_file=log)

    return _finalize_session(session_dir, started, code, steps)


def session_urirdp_rdp_e2e(session_dir: Path) -> int:
    started = _now_iso()
    pkg = ROOT / "urirdp-docker"
    compose = pkg / "docker-compose.rdp-e2e.yml"
    _write_meta(
        session_dir,
        session_id=session_dir.name,
        session_name="urirdp-rdp-e2e",
        suite="docker-e2e",
        started_at=started,
        host=_host_id(),
        ports={"uri": 8795, "rdp": 3389},
    )
    log = session_dir / "session.log"
    steps: list[dict[str, Any]] = []

    _prepare_urirdp_data(pkg)
    _sleep_ports()
    _run_cmd(_compose_cmd("down", "-v", compose_file=compose), cwd=pkg, log_file=log)
    proc = _run_cmd(
        _compose_cmd(
            "up",
            "--build",
            "--abort-on-container-exit",
            "--exit-code-from",
            "rdp-client",
            compose_file=compose,
        ),
        cwd=pkg,
        log_file=log,
        timeout=600.0,
    )
    _docker_logs("urirdp", compose, pkg, session_dir / "docker-logs-urirdp.txt")
    _docker_logs("rdp-client", compose, pkg, session_dir / "docker-logs-rdp-client.txt")
    _copy_container_file("urirdp-real", "/opt/urirdp/data/events.jsonl", session_dir / "events.jsonl")
    _copy_container_file("urirdp-real", "/opt/urirdp/data/screenshots/latest.png", session_dir / "screenshots" / "e2e-latest.png")

    # Extract last JSON result from log if present
    if "ALL PASSED" in (proc.stdout or "") + (proc.stderr or ""):
        steps.append({"name": "e2e-rdp-real", "status": "pass"})
    else:
        steps.append({"name": "e2e-rdp-real", "status": "fail", "detail": (proc.stderr or proc.stdout)[-500:]})

    _run_cmd(_compose_cmd("down", "-v", compose_file=compose), cwd=pkg, log_file=log)
    _sleep_ports()
    return _finalize_session(session_dir, started, proc.returncode, steps)


def session_automation_lab(session_dir: Path, *, use_existing: bool = False) -> int:
    started = _now_iso()
    lab = ROOT / "urisys-automation-lab"
    lab_port = 8099
    rdp_port = 8795
    _write_meta(
        session_dir,
        session_id=session_dir.name,
        session_name="automation-lab",
        suite="lab-stack",
        started_at=started,
        host=_host_id(),
        ports={"lab": lab_port, "uri": rdp_port},
    )
    log = session_dir / "session.log"
    steps: list[dict[str, Any]] = []
    code = 0

    if not use_existing:
        _sleep_ports()
        _run_cmd(["bash", "scripts/docker-down.sh"], cwd=lab, log_file=log)
        up = _run_cmd(["bash", "scripts/docker-up.sh"], cwd=lab, log_file=log, timeout=300.0)
        if up.returncode != 0:
            steps.append({"name": "lab-up", "status": "fail"})
            return _finalize_session(session_dir, started, up.returncode, steps)

    try:
        lab_health = _wait_health(f"http://127.0.0.1:{lab_port}/health", attempts=60)
        _save_json(session_dir / "responses" / "01-lab-health.json", lab_health)
        steps.append({"name": "lab-health", "status": "pass"})

        rdp_health = _wait_health(f"http://127.0.0.1:{rdp_port}/health", attempts=60)
        _save_json(session_dir / "responses" / "02-rdp-health.json", rdp_health)
        steps.append({"name": "rdp-health", "status": "pass"})

        stt = _http_json(
            "POST",
            f"http://127.0.0.1:{lab_port}/uri/call",
            {
                "uri": "stt://local/session/main/query/transcript",
                "payload": {"text": "kliknij OK"},
                "context": {"approved": True},
            },
        )
        _save_json(session_dir / "responses" / "03-stt.json", stt)
        steps.append({"name": "stt-mock", "status": "pass" if stt.get("ok") else "fail", "uri": stt.get("uri")})

        chat_dry = _http_json(
            "POST",
            f"http://127.0.0.1:{lab_port}/uri/call",
            {
                "uri": "chat://local/uri/command/execute",
                "payload": {"transcript": "kliknij OK", "dry_run": True, "approved": True},
                "context": {"approved": True, "dry_run": True},
            },
        )
        _save_json(session_dir / "responses" / "04-chat-dry-run.json", chat_dry)
        steps.append({"name": "chat-dry-run", "status": "pass" if chat_dry.get("ok") else "fail"})

        # Bootstrap X for real forward test
        boot = _run_cmd(
            ["docker", "exec", "urisys-lab-urirdp", "bash", "/opt/urirdp/docker/bootstrap-rdp-session.sh"],
            log_file=log,
        )
        steps.append({"name": "bootstrap-rdp", "status": "pass" if boot.returncode == 0 else "fail"})

        chat_real = _http_json(
            "POST",
            f"http://127.0.0.1:{lab_port}/uri/call",
            {
                "uri": "chat://local/uri/command/execute",
                "payload": {"transcript": "kliknij OK", "approved": True},
                "context": {"approved": True, "allow_real": True},
            },
            timeout=180.0,
        )
        _save_json(session_dir / "responses" / "05-chat-real.json", chat_real)
        _copy_container_file("urisys-lab-urirdp", "/opt/urirdp/data/screenshots/latest.png", session_dir / "screenshots" / "05-lab-real-click.png")
        inner = ((chat_real.get("result") or {}).get("result") or {}).get("result") or {}
        clicked = inner.get("clicked")
        steps.append(
            {
                "name": "chat-real-forward",
                "status": "pass" if chat_real.get("ok") and clicked else "fail",
                "uri": "chat://local/uri/command/execute",
                "metrics": {"clicked": clicked},
                "screenshot": "screenshots/05-lab-real-click.png" if clicked else None,
            }
        )

        if any(s["status"] == "fail" for s in steps):
            code = 1
    except Exception as exc:
        steps.append({"name": "automation-lab", "status": "fail", "detail": str(exc)})
        code = 1
    finally:
        _docker_logs("urirdp", lab / "docker-compose.lab.yml", lab, session_dir / "docker-logs-urirdp.txt")
        _docker_logs("automation-lab", lab / "docker-compose.lab.yml", lab, session_dir / "docker-logs-lab.txt")
        _copy_container_file("urisys-lab-urirdp", "/opt/urirdp/data/events.jsonl", session_dir / "events-urirdp.jsonl")
        lab_events = lab / "data" / "events.jsonl"
        if lab_events.is_file():
            shutil.copy2(lab_events, session_dir / "events-lab.jsonl")

    return _finalize_session(session_dir, started, code, steps)


def _parse_lab_flow(path: Path) -> tuple[dict[str, Any], list[tuple[str, dict[str, Any]]]]:
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    defaults = dict(data.get("defaults") or {})
    steps: list[tuple[str, dict[str, Any]]] = []
    for step in data.get("do") or []:
        if isinstance(step, str):
            steps.append((step, {}))
        elif isinstance(step, dict):
            if "uri" in step:
                steps.append((str(step["uri"]), dict(step.get("payload") or {})))
            else:
                uri, payload = next(iter(step.items()))
                steps.append((str(uri), dict(payload or {})))
    return defaults, steps


def _flow_step_context(
    defaults: dict[str, Any],
    uri: str,
    *,
    display: str,
    xauth: str,
    real_mode: bool = False,
) -> dict[str, Any]:
    scheme = uri.split("://", 1)[0] if "://" in uri else ""
    ctx: dict[str, Any] = {"approved": True, "display": display, "xauthority": xauth}
    if real_mode:
        ctx["allow_real"] = scheme not in {"webrtc", "stt"}
        ctx["dry_run"] = scheme in {"webrtc", "stt"}
        if scheme in {"kvm", "rdp", "him", "ocr", "llm", "shell", "chat"}:
            ctx["allow_real"] = True
            ctx["dry_run"] = False
        return ctx
    if scheme in {"kvm", "rdp", "him", "ocr", "llm"}:
        ctx["allow_real"] = True
        ctx["dry_run"] = False
    elif scheme in {"stt", "chat", "webrtc"}:
        ctx["dry_run"] = bool(defaults.get("dry_run", True))
        ctx["allow_real"] = False
    else:
        ctx["dry_run"] = bool(defaults.get("dry_run", True))
    return ctx


def _file_md5(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.md5(path.read_bytes()).hexdigest()


def _step_pause(uri: str, *, real_mode: bool) -> None:
    if not real_mode:
        return
    scheme = uri.split("://", 1)[0] if "://" in uri else ""
    if scheme in {"him", "kvm", "shell", "chat", "browser"}:
        time.sleep(3.0)
    elif scheme in {"rdp"}:
        time.sleep(1.0)


def _summarize_uri_response(res: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {"ok": bool(res.get("ok")), "error": res.get("error")}
    result = res.get("result") or {}
    if isinstance(result, dict):
        if result.get("mode") == "dry_run":
            out["mode"] = "dry_run"
        inner = result.get("result") or {}
        if isinstance(inner, dict):
            if "clicked" in inner:
                out["clicked"] = inner.get("clicked")
            if inner.get("result") and isinstance(inner["result"], dict):
                out["clicked"] = inner["result"].get("clicked", out.get("clicked"))
        for key in ("driver", "exit_code", "command", "hotkey", "engine"):
            if key in result:
                out[key] = result[key]
    return out


def _parse_docker_log_errors(session_dir: Path) -> dict[str, Any]:
    summary: dict[str, Any] = {"http_502": 0, "http_400": 0, "lines": []}
    for name in ("docker-logs-lab.txt", "docker-logs-urirdp.txt", "docker-logs.txt"):
        path = session_dir / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        summary["http_502"] += text.count("502")
        summary["http_400"] += text.count("400")
        for line in text.splitlines():
            if any(x in line for x in ('" 502 ', '" 400 ', "failed", "Error", "error")):
                if "health" in line.lower() and "200" in line:
                    continue
                summary["lines"].append(f"{name}: {line.strip()[:200]}")
    summary["lines"] = summary["lines"][-40:]
    return summary


def _prepare_ok_target(rdp_port: int, display: str, xauth: str) -> None:
    ctx = {"approved": True, "allow_real": True, "display": display, "xauthority": xauth}
    _http_json(
        "POST",
        f"http://127.0.0.1:{rdp_port}/uri/call",
        {
            "uri": "rdp://local/session/command/prepare-target",
            "payload": {"text": "OK"},
            "context": ctx,
        },
    )
    time.sleep(2.0)


def _capture_rdp_screenshot(
    session_dir: Path,
    *,
    rdp_port: int,
    display: str,
    xauth: str,
    container: str,
    filename: str,
) -> tuple[bool, str | None]:
    ctx = {"approved": True, "allow_real": True, "display": display, "xauthority": xauth}
    try:
        shot = _http_json(
            "POST",
            f"http://127.0.0.1:{rdp_port}/uri/call",
            {"uri": "kvm://local/monitor/primary/query/screenshot", "payload": {}, "context": ctx},
        )
        rel = f"screenshots/{filename}"
        dest = session_dir / rel
        if _copy_container_file(container, "/opt/urirdp/data/screenshots/latest.png", dest):
            return bool(shot.get("ok") and (shot.get("result") or {}).get("captured")), rel
        return False, None
    except Exception:
        return False, None


def session_lab_10_flows(session_dir: Path) -> int:
    """Run all 10 automation-lab flows; capture one RDP screenshot per flow."""
    started = _now_iso()
    lab = ROOT / "urisys-automation-lab"
    flows_dir = lab / "flows"
    lab_port = 8099
    rdp_port = 8795
    container = "urisys-lab-urirdp"
    _write_meta(
        session_dir,
        session_id=session_dir.name,
        session_name="lab-10-flows",
        suite="lab-flows",
        started_at=started,
        host=_host_id(),
        ports={"lab": lab_port, "uri": rdp_port},
        flow_count=10,
    )
    log = session_dir / "session.log"
    steps: list[dict[str, Any]] = []
    code = 0
    display = ":10"
    xauth = ""
    screenshot_hashes: dict[str, str] = {}

    _sleep_ports()
    _run_cmd(["bash", "scripts/docker-down.sh"], cwd=lab, log_file=log)
    up = _run_cmd(["bash", "scripts/docker-up.sh"], cwd=lab, log_file=log, timeout=300.0)
    if up.returncode != 0:
        steps.append({"name": "lab-up", "status": "fail"})
        return _finalize_session(session_dir, started, up.returncode, steps)

    try:
        _wait_health(f"http://127.0.0.1:{lab_port}/health", attempts=60)
        _wait_health(f"http://127.0.0.1:{rdp_port}/health", attempts=60)
        steps.append({"name": "stack-health", "status": "pass"})

        boot = _run_cmd(
            ["docker", "exec", container, "bash", "/opt/urirdp/docker/bootstrap-rdp-session.sh"],
            log_file=log,
        )
        steps.append({"name": "bootstrap-rdp", "status": "pass" if boot.returncode == 0 else "fail"})
        if boot.returncode != 0:
            raise RuntimeError("bootstrap-rdp-session failed")

        disp_proc = _run_cmd(
            ["docker", "exec", container, "bash", "-lc", "grep ^DISPLAY= /tmp/urirdp-display.env | cut -d= -f2"],
        )
        display = (disp_proc.stdout or ":10").strip() or ":10"
        xauth_proc = _run_cmd(
            ["docker", "exec", container, "bash", "-lc", "grep ^XAUTHORITY= /tmp/urirdp-display.env | cut -d= -f2"],
        )
        xauth = (xauth_proc.stdout or "").strip()
        _write_meta(session_dir, display=display, xauthority=xauth)

        baseline_png = session_dir / "screenshots" / "00-baseline.png"
        _capture_rdp_screenshot(
            session_dir,
            rdp_port=rdp_port,
            display=display,
            xauth=xauth,
            container=container,
            filename="00-baseline.png",
        )
        prev_md5 = _file_md5(baseline_png)
        screenshot_hashes: dict[str, str] = {}
        if prev_md5:
            screenshot_hashes["00-baseline"] = prev_md5

        flow_paths = sorted(flows_dir.glob("*.uri.flow.yaml"))
        if len(flow_paths) != 10:
            steps.append(
                {
                    "name": "flow-count",
                    "status": "fail",
                    "detail": f"expected 10 flows, found {len(flow_paths)}",
                }
            )
            code = 1

        for idx, flow_path in enumerate(flow_paths, start=1):
            flow_id = flow_path.stem
            defaults, flow_steps = _parse_lab_flow(flow_path)
            step_results: list[dict[str, Any]] = []
            for uri, payload in flow_steps:
                ctx = _flow_step_context(
                    defaults, uri, display=display, xauth=xauth, real_mode=True
                )
                if uri.startswith("chat://") and "execute" in uri:
                    payload = {**payload, "approved": True, "dry_run": False}
                try:
                    res = _http_json(
                        "POST",
                        f"http://127.0.0.1:{lab_port}/uri/call",
                        {"uri": uri, "payload": payload, "context": ctx},
                        timeout=180.0,
                    )
                    summary = _summarize_uri_response(res)
                    summary["uri"] = uri
                    step_results.append(summary)
                except Exception as exc:
                    step_results.append({"uri": uri, "ok": False, "error": str(exc)})
                _step_pause(uri, real_mode=True)

            png_name = f"{idx:02d}-{flow_id}.png"
            captured, shot_rel = _capture_rdp_screenshot(
                session_dir,
                rdp_port=rdp_port,
                display=display,
                xauth=xauth,
                container=container,
                filename=png_name,
            )
            png_md5 = _file_md5(session_dir / shot_rel) if shot_rel else None
            duplicate_of: str | None = None
            if png_md5:
                for label, digest in screenshot_hashes.items():
                    if digest == png_md5:
                        duplicate_of = label
                        break
                screenshot_hashes[f"{idx:02d}-{flow_id}"] = png_md5 or ""

            _save_json(
                session_dir / "responses" / f"{idx:02d}-{flow_id}.json",
                {
                    "flow": flow_id,
                    "real_mode": True,
                    "steps": step_results,
                    "screenshot": shot_rel,
                    "captured": captured,
                    "md5": png_md5,
                    "duplicate_of": duplicate_of,
                },
            )

            steps_ok = sum(1 for s in step_results if s.get("ok"))
            unique_shot = captured and duplicate_of is None
            flow_pass = steps_ok == len(flow_steps) and unique_shot
            steps.append(
                {
                    "name": flow_id,
                    "status": "pass" if flow_pass else "fail",
                    "uri": flow_path.name,
                    "metrics": {
                        "steps_ok": steps_ok,
                        "steps_total": len(flow_steps),
                        "screenshot": shot_rel,
                        "captured": captured,
                        "md5": png_md5,
                        "duplicate_of": duplicate_of,
                    },
                    "screenshot": shot_rel,
                    "detail": ""
                    if flow_pass
                    else f"{steps_ok}/{len(flow_steps)} ok, captured={captured}, dup={duplicate_of}",
                }
            )
            if not flow_pass:
                code = 1
            prev_md5 = png_md5 or prev_md5

    except Exception as exc:
        steps.append({"name": "lab-10-flows", "status": "fail", "detail": str(exc)})
        code = 1
    finally:
        _docker_logs("urirdp", lab / "docker-compose.lab.yml", lab, session_dir / "docker-logs-urirdp.txt")
        _docker_logs("automation-lab", lab / "docker-compose.lab.yml", lab, session_dir / "docker-logs-lab.txt")
        _copy_container_file(container, "/opt/urirdp/data/events.jsonl", session_dir / "events-urirdp.jsonl")
        log_errors = _parse_docker_log_errors(session_dir)
        _save_json(session_dir / "log-errors.json", log_errors)
        _write_meta(session_dir, log_errors=log_errors, screenshot_hashes=screenshot_hashes)

    return _finalize_session(session_dir, started, code, steps)


SESSIONS: dict[str, Callable[[Path], int]] = {
    "pytest-urirdp": session_pytest_urirdp,
    "pytest-urisys": session_pytest_urisys,
    "pytest-urisys-node": session_pytest_urisys_node,
    "urirdp-mock-docker": session_urirdp_mock_docker,
    "urirdp-real-docker": session_urirdp_real_docker,
    "urirdp-rdp-e2e": session_urirdp_rdp_e2e,
    "automation-lab": session_automation_lab,
    "lab-10-flows": session_lab_10_flows,
}

DEFAULT_ORDER = [
    "pytest-urisys",
    "pytest-urirdp",
    "pytest-urisys-node",
    "urirdp-mock-docker",
    "urirdp-real-docker",
    "urirdp-rdp-e2e",
    "automation-lab",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run urisys test sessions with reports")
    parser.add_argument("--output", type=Path, default=ROOT / "output" / "test-sessions")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--sessions", default="", help="Comma-separated session names")
    parser.add_argument("--keep-lab", action="store_true", help="Leave automation-lab stack running")
    args = parser.parse_args()

    run_id = args.run_id or _run_id()
    run_dir = args.output / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    names = [s.strip() for s in args.sessions.split(",") if s.strip()] or DEFAULT_ORDER
    manifest = {"run_id": run_id, "started_at": _now_iso(), "host": _host_id(), "sessions": names}
    _save_json(run_dir / "manifest.json", manifest)

    # Stop lab stack before port-conflicting sessions
    if any(n in names for n in ("urirdp-mock-docker", "urirdp-real-docker", "urirdp-rdp-e2e")):
        lab = ROOT / "urisys-automation-lab"
        _run_cmd(["bash", "scripts/docker-down.sh"], cwd=lab, log_file=run_dir / "preflight.log")

    results: dict[str, int] = {}
    for name in names:
        if name not in SESSIONS:
            print(f"unknown session: {name}", file=sys.stderr)
            results[name] = 1
            continue
        session_dir = run_dir / name
        session_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n=== session: {name} -> {session_dir} ===")
        t0 = time.time()
        if name == "automation-lab":
            rc = session_automation_lab(session_dir, use_existing=False)
        else:
            rc = SESSIONS[name](session_dir)
        results[name] = rc
        print(f"=== {name}: {'PASS' if rc == 0 else 'FAIL'} ({time.time() - t0:.1f}s) ===")

    manifest["finished_at"] = _now_iso()
    manifest["results"] = results
    _save_json(run_dir / "manifest.json", manifest)

    proc = subprocess.run([sys.executable, str(REPORT_SCRIPT), "analyze", str(run_dir)], check=False)
    print(f"\nRun directory: {run_dir}")
    print(f"Analysis: {run_dir / 'analysis.md'}")
    return 0 if all(rc == 0 for rc in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
