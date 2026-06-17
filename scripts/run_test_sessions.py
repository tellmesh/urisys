#!/usr/bin/env python3
"""Run urisys Docker/RDP test sessions with screenshots, logs, and per-session reports.

Usage:
  python3 scripts/run_test_sessions.py
  python3 scripts/run_test_sessions.py --sessions urirdp-mock,urirdp-real
  python3 scripts/run_test_sessions.py --output output/test-sessions

Implementation split: scripts/test_sessions/ (see project/analysis.toon.yaml).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

from test_sessions import (
    ROOT,
    REPORT_SCRIPT,
    compose_cmd,
    copy_container_file,
    copy_host_screenshot,
    docker_logs,
    evaluate_expectations,
    finalize_session,
    flow_expectations,
    host_id,
    http_json,
    now_iso,
    prepare_urirdp_data,
    run_cmd,
    run_id,
    save_json,
    session_lab_10_flows,
    sleep_ports,
    wait_health,
    write_meta,
)

# Backward-compatible re-exports for tests
_flow_expectations = flow_expectations
_now_iso = now_iso
_run_id = run_id
_host_id = host_id
_http_json = http_json
_wait_health = wait_health
_compose_cmd = compose_cmd
_prepare_urirdp_data = prepare_urirdp_data
_sleep_ports = sleep_ports
_save_json = save_json
_run_cmd = run_cmd
_write_meta = write_meta
_finalize_session = finalize_session
_docker_logs = docker_logs
_copy_container_file = copy_container_file


def session_pytest_urirdp(session_dir: Path) -> int:
    started = now_iso()
    write_meta(
        session_dir,
        session_id=session_dir.name,
        session_name="pytest-urirdp",
        suite="unit",
        started_at=started,
        host=host_id(),
    )
    log = session_dir / "session.log"
    pkg = ROOT / "urirdp-docker"
    proc = run_cmd([sys.executable, "-m", "pytest", "-q"], cwd=pkg, log_file=log)
    steps = [{"name": "pytest", "status": "pass" if proc.returncode == 0 else "fail", "detail": proc.stderr[-500:] if proc.returncode else ""}]
    return finalize_session(session_dir, started, proc.returncode, steps)


def session_pytest_urisys(session_dir: Path) -> int:
    started = now_iso()
    write_meta(session_dir, session_id=session_dir.name, session_name="pytest-urisys", suite="unit", started_at=started, host=host_id())
    log = session_dir / "session.log"
    proc = run_cmd([sys.executable, "-m", "pytest", "tests/", "-q"], cwd=ROOT, log_file=log)
    steps = [{"name": "pytest", "status": "pass" if proc.returncode == 0 else "fail"}]
    return finalize_session(session_dir, started, proc.returncode, steps)


def session_pytest_urisys_node(session_dir: Path) -> int:
    started = now_iso()
    write_meta(session_dir, session_id=session_dir.name, session_name="pytest-urisys-node", suite="unit", started_at=started, host=host_id())
    log = session_dir / "session.log"
    pkg = ROOT / "urisys-node"
    proc = run_cmd([sys.executable, "-m", "pytest", "-q"], cwd=pkg, log_file=log)
    steps = [{"name": "pytest", "status": "pass" if proc.returncode == 0 else "fail"}]
    return finalize_session(session_dir, started, proc.returncode, steps)


def session_urirdp_mock_docker(session_dir: Path) -> int:
    started = now_iso()
    port = 8795
    pkg = ROOT / "urirdp-docker"
    write_meta(
        session_dir,
        session_id=session_dir.name,
        session_name="urirdp-mock-docker",
        suite="docker-smoke",
        started_at=started,
        host=host_id(),
        ports={"uri": port},
    )
    log = session_dir / "session.log"
    steps: list[dict[str, Any]] = []
    code = 0

    prepare_urirdp_data(pkg)
    sleep_ports()
    run_cmd(compose_cmd("down", "-v"), cwd=pkg, log_file=log)
    up = run_cmd(compose_cmd("up", "-d", "--build", "urirdp"), cwd=pkg, log_file=log)
    if up.returncode != 0:
        steps.append({"name": "compose-up", "status": "fail"})
        docker_logs("urirdp", None, pkg, session_dir / "docker-logs.txt")
        return finalize_session(session_dir, started, up.returncode, steps)

    try:
        health = wait_health(f"http://127.0.0.1:{port}/health")
        save_json(session_dir / "responses" / "01-health.json", health)
        steps.append({"name": "health", "status": "pass", "uri": f"http://127.0.0.1:{port}/health"})
        time.sleep(3)

        routes = http_json("GET", f"http://127.0.0.1:{port}/uri/routes")
        save_json(session_dir / "responses" / "02-routes.json", routes)
        steps.append({"name": "routes", "status": "pass"})

        click = http_json(
            "POST",
            f"http://127.0.0.1:{port}/uri/call",
            {
                "uri": "kvm://local/task/command/click-text",
                "payload": {"text": "OK"},
                "context": {"approved": True, "dry_run": True},
            },
        )
        save_json(session_dir / "responses" / "03-click-dry-run.json", click)
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
        docker_logs("urirdp", None, pkg, session_dir / "docker-logs.txt")
        copy_container_file("urirdp-gui", "/opt/urirdp/data/events.jsonl", session_dir / "events.jsonl")
        run_cmd(compose_cmd("down", "-v"), cwd=pkg, log_file=log)

    return finalize_session(session_dir, started, code, steps)


def session_urirdp_real_docker(session_dir: Path) -> int:
    started = now_iso()
    port = 8795
    pkg = ROOT / "urirdp-docker"
    container = "urirdp-gui"
    write_meta(
        session_dir,
        session_id=session_dir.name,
        session_name="urirdp-real-docker",
        suite="docker-real",
        started_at=started,
        host=host_id(),
        ports={"uri": port, "rdp": 3389},
    )
    log = session_dir / "session.log"
    steps: list[dict[str, Any]] = []
    code = 0
    display = ":10"
    xauth = ""

    env = {"URISYS_ALLOW_REAL": "1"}
    prepare_urirdp_data(pkg)
    sleep_ports()
    run_cmd(compose_cmd("down", "-v"), cwd=pkg, log_file=log, env=env)
    up = run_cmd(compose_cmd("up", "-d", "--build", "urirdp"), cwd=pkg, log_file=log, env=env)
    if up.returncode != 0:
        steps.append({"name": "compose-up", "status": "fail"})
        return finalize_session(session_dir, started, up.returncode, steps)

    try:
        health = wait_health(f"http://127.0.0.1:{port}/health")
        save_json(session_dir / "responses" / "01-health.json", health)
        steps.append({"name": "health", "status": "pass"})
        time.sleep(5)

        boot = run_cmd(
            ["docker", "exec", container, "bash", "/opt/urirdp/docker/bootstrap-rdp-session.sh"],
            log_file=log,
        )
        steps.append({"name": "bootstrap-rdp", "status": "pass" if boot.returncode == 0 else "fail"})
        if boot.returncode != 0:
            raise RuntimeError("bootstrap-rdp-session failed")

        disp_proc = run_cmd(
            ["docker", "exec", container, "bash", "-lc", "grep ^DISPLAY= /tmp/urirdp-display.env | cut -d= -f2"],
        )
        display = (disp_proc.stdout or ":10").strip() or ":10"
        xauth_proc = run_cmd(
            ["docker", "exec", container, "bash", "-lc", "grep ^XAUTHORITY= /tmp/urirdp-display.env | cut -d= -f2"],
        )
        xauth = (xauth_proc.stdout or "").strip()
        write_meta(session_dir, display=display, xauthority=xauth)

        ctx = {"approved": True, "allow_real": True, "display": display, "xauthority": xauth}

        shot = http_json(
            "POST",
            f"http://127.0.0.1:{port}/uri/call",
            {"uri": "kvm://local/monitor/primary/query/screenshot", "payload": {}, "context": ctx},
        )
        save_json(session_dir / "responses" / "02-screenshot.json", shot)
        copy_container_file(container, "/opt/urirdp/data/screenshots/latest.png", session_dir / "screenshots" / "02-screenshot.png")
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

        ocr = http_json(
            "POST",
            f"http://127.0.0.1:{port}/uri/call",
            {"uri": "ocr://local/image/latest/query/text", "payload": {}, "context": ctx},
        )
        save_json(session_dir / "responses" / "03-ocr.json", ocr)
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

        click = http_json(
            "POST",
            f"http://127.0.0.1:{port}/uri/call",
            {
                "uri": "kvm://local/task/command/click-text",
                "payload": {"text": "OK"},
                "context": ctx,
            },
            timeout=180.0,
        )
        save_json(session_dir / "responses" / "04-click-text.json", click)
        copy_container_file(container, "/opt/urirdp/data/screenshots/latest.png", session_dir / "screenshots" / "04-after-click.png")
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

        flow = run_cmd(
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
        save_json(session_dir / "responses" / "05-flow.json", flow_steps)
        flow_ok = flow.returncode == 0 and all(s.get("ok") for s in flow_steps)
        steps.append({"name": "flow", "status": "pass" if flow_ok else "fail", "metrics": {"steps": len(flow_steps)}})

        if any(s["status"] == "fail" for s in steps):
            code = 1
    except Exception as exc:
        steps.append({"name": "real-docker", "status": "fail", "detail": str(exc)})
        code = 1
    finally:
        docker_logs("urirdp", None, pkg, session_dir / "docker-logs.txt")
        copy_container_file(container, "/opt/urirdp/data/events.jsonl", session_dir / "events.jsonl")
        run_cmd(compose_cmd("down", "-v"), cwd=pkg, log_file=log)

    return finalize_session(session_dir, started, code, steps)


def session_urirdp_rdp_e2e(session_dir: Path) -> int:
    started = now_iso()
    pkg = ROOT / "urirdp-docker"
    compose = pkg / "docker-compose.rdp-e2e.yml"
    write_meta(
        session_dir,
        session_id=session_dir.name,
        session_name="urirdp-rdp-e2e",
        suite="docker-e2e",
        started_at=started,
        host=host_id(),
        ports={"uri": 8795, "rdp": 3389},
    )
    log = session_dir / "session.log"
    steps: list[dict[str, Any]] = []

    prepare_urirdp_data(pkg)
    sleep_ports()
    run_cmd(compose_cmd("down", "-v", compose_file=compose), cwd=pkg, log_file=log)
    proc = run_cmd(
        compose_cmd(
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
    docker_logs("urirdp", compose, pkg, session_dir / "docker-logs-urirdp.txt")
    docker_logs("rdp-client", compose, pkg, session_dir / "docker-logs-rdp-client.txt")
    copy_container_file("urirdp-real", "/opt/urirdp/data/events.jsonl", session_dir / "events.jsonl")
    copy_container_file("urirdp-real", "/opt/urirdp/data/screenshots/latest.png", session_dir / "screenshots" / "e2e-latest.png")

    if "ALL PASSED" in (proc.stdout or "") + (proc.stderr or ""):
        steps.append({"name": "e2e-rdp-real", "status": "pass"})
    else:
        steps.append({"name": "e2e-rdp-real", "status": "fail", "detail": (proc.stderr or proc.stdout)[-500:]})

    run_cmd(compose_cmd("down", "-v", compose_file=compose), cwd=pkg, log_file=log)
    sleep_ports()
    return finalize_session(session_dir, started, proc.returncode, steps)


def session_automation_lab(session_dir: Path, *, use_existing: bool = False) -> int:
    started = now_iso()
    lab = ROOT / "urisys-automation-lab"
    lab_port = 8099
    rdp_port = 8795
    write_meta(
        session_dir,
        session_id=session_dir.name,
        session_name="automation-lab",
        suite="lab-stack",
        started_at=started,
        host=host_id(),
        ports={"lab": lab_port, "uri": rdp_port},
    )
    log = session_dir / "session.log"
    steps: list[dict[str, Any]] = []
    code = 0

    if not use_existing:
        sleep_ports()
        run_cmd(["bash", "scripts/docker-down.sh"], cwd=lab, log_file=log)
        up = run_cmd(["bash", "scripts/docker-up.sh"], cwd=lab, log_file=log, timeout=600.0)
        if up.returncode != 0:
            steps.append({"name": "lab-up", "status": "fail"})
            return finalize_session(session_dir, started, up.returncode, steps)

    try:
        lab_health = wait_health(f"http://127.0.0.1:{lab_port}/health", attempts=60)
        save_json(session_dir / "responses" / "01-lab-health.json", lab_health)
        steps.append({"name": "lab-health", "status": "pass"})

        rdp_health = wait_health(f"http://127.0.0.1:{rdp_port}/health", attempts=60)
        save_json(session_dir / "responses" / "02-rdp-health.json", rdp_health)
        steps.append({"name": "rdp-health", "status": "pass"})

        stt = http_json(
            "POST",
            f"http://127.0.0.1:{lab_port}/uri/call",
            {
                "uri": "stt://local/session/main/query/transcript",
                "payload": {"text": "kliknij OK"},
                "context": {"approved": True},
            },
        )
        save_json(session_dir / "responses" / "03-stt.json", stt)
        steps.append({"name": "stt-mock", "status": "pass" if stt.get("ok") else "fail", "uri": stt.get("uri")})

        chat_dry = http_json(
            "POST",
            f"http://127.0.0.1:{lab_port}/uri/call",
            {
                "uri": "chat://local/uri/command/execute",
                "payload": {"transcript": "kliknij OK", "dry_run": True, "approved": True},
                "context": {"approved": True, "dry_run": True},
            },
        )
        save_json(session_dir / "responses" / "04-chat-dry-run.json", chat_dry)
        steps.append({"name": "chat-dry-run", "status": "pass" if chat_dry.get("ok") else "fail"})

        boot = run_cmd(
            ["docker", "exec", "urisys-lab-urirdp", "bash", "/opt/urirdp/docker/bootstrap-rdp-session.sh"],
            log_file=log,
        )
        steps.append({"name": "bootstrap-rdp", "status": "pass" if boot.returncode == 0 else "fail"})

        chat_real = http_json(
            "POST",
            f"http://127.0.0.1:{lab_port}/uri/call",
            {
                "uri": "chat://local/uri/command/execute",
                "payload": {"transcript": "kliknij OK", "approved": True},
                "context": {"approved": True, "allow_real": True},
            },
            timeout=180.0,
        )
        save_json(session_dir / "responses" / "05-chat-real.json", chat_real)
        copy_container_file("urisys-lab-urirdp", "/opt/urirdp/data/screenshots/latest.png", session_dir / "screenshots" / "05-lab-real-click.png")
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
        docker_logs("urirdp", lab / "docker-compose.lab.yml", lab, session_dir / "docker-logs-urirdp.txt")
        docker_logs("automation-lab", lab / "docker-compose.lab.yml", lab, session_dir / "docker-logs-lab.txt")
        copy_container_file("urisys-lab-urirdp", "/opt/urirdp/data/events.jsonl", session_dir / "events-urirdp.jsonl")
        lab_events = lab / "data" / "events.jsonl"
        if lab_events.is_file():
            shutil.copy2(lab_events, session_dir / "events-lab.jsonl")

    return finalize_session(session_dir, started, code, steps)


def _monorepo_root() -> Path | None:
    candidate = ROOT.parent
    if (candidate / "uricore").is_dir() and (ROOT / "urisys-automation-lab").is_dir():
        return candidate
    if (ROOT / "uricore").is_dir():
        return ROOT
    return None


def session_urisys_node_docker_gui(session_dir: Path) -> int:
    started = now_iso()
    port = int(os.environ.get("URISYS_NODE_HOST_PORT", "8790"))
    write_meta(
        session_dir,
        session_id=session_dir.name,
        session_name="urisys-node-docker-gui",
        suite="docker-gui",
        started_at=started,
        host=host_id(),
        ports={"node": port},
    )
    log = session_dir / "session.log"
    steps: list[dict[str, Any]] = []
    code = 0

    if _monorepo_root() is None:
        steps.append(
            {
                "name": "preflight-monorepo",
                "status": "fail",
                "detail": "uricore sibling missing — run from tellmesh checkout (urisys + uricore)",
            }
        )
        return finalize_session(session_dir, started, 1, steps)

    env = os.environ.copy()
    env["URISYS_NODE_E2E_KEEP"] = "0"
    env["URISYS_NODE_SESSION_DIR"] = str(session_dir)
    proc = run_cmd(
        ["bash", "scripts/run-urisys-node-docker-e2e.sh"],
        cwd=ROOT,
        log_file=log,
        timeout=600.0,
        env=env,
    )
    steps.append(
        {
            "name": "host-control-e2e",
            "status": "pass" if proc.returncode == 0 else "fail",
            "detail": "" if proc.returncode == 0 else (proc.stderr or proc.stdout or "")[-500:],
        }
    )
    if proc.returncode != 0:
        code = 1
    return finalize_session(session_dir, started, code, steps)


def session_office_simulate(session_dir: Path) -> int:
    started = now_iso()
    port = int(os.environ.get("URISYS_NODE_HOST_PORT", "8790"))
    write_meta(
        session_dir,
        session_id=session_dir.name,
        session_name="office-simulate",
        suite="docker-gui",
        started_at=started,
        host=host_id(),
        ports={"node": port},
    )
    log = session_dir / "session.log"
    steps: list[dict[str, Any]] = []
    code = 0

    if _monorepo_root() is None:
        steps.append(
            {
                "name": "preflight-monorepo",
                "status": "fail",
                "detail": "uricore sibling missing — run from tellmesh checkout",
            }
        )
        return finalize_session(session_dir, started, 1, steps)

    env = os.environ.copy()
    env["URISYS_OFFICE_E2E_KEEP"] = "0"
    env["URISYS_OFFICE_SESSION_DIR"] = str(session_dir)
    proc = run_cmd(
        ["bash", "scripts/run-office-simulate-e2e.sh"],
        cwd=ROOT,
        log_file=log,
        timeout=900.0,
        env=env,
    )
    steps.append(
        {
            "name": "office-simulate-e2e",
            "status": "pass" if proc.returncode == 0 else "fail",
            "detail": "" if proc.returncode == 0 else (proc.stderr or proc.stdout or "")[-800:],
        }
    )
    if proc.returncode != 0:
        code = 1
    return finalize_session(session_dir, started, code, steps)


def session_office_simulate_lenovo(session_dir: Path) -> int:
    started = now_iso()
    base = os.environ.get("LENOVO", "http://192.168.188.201:8790")
    write_meta(
        session_dir,
        session_id=session_dir.name,
        session_name="office-simulate-lenovo",
        suite="remote-node",
        started_at=started,
        host=host_id(),
        ports={"node": base.rsplit(":", 1)[-1] if ":" in base else "8790"},
        extra={"target": base},
    )
    log = session_dir / "session.log"
    steps: list[dict[str, Any]] = []
    env = os.environ.copy()
    env["OFFICE_LENOVO_SESSION_DIR"] = str(session_dir)
    env["LENOVO"] = base
    proc = run_cmd(
        ["bash", "scripts/run-office-simulate-lenovo.sh"],
        cwd=ROOT,
        log_file=log,
        timeout=900.0,
        env=env,
    )
    steps.append(
        {
            "name": "office-simulate-lenovo",
            "status": "pass" if proc.returncode == 0 else "fail",
            "detail": "" if proc.returncode == 0 else (proc.stderr or proc.stdout or "")[-800:],
        }
    )
    return finalize_session(session_dir, started, proc.returncode, steps)


SESSIONS: dict[str, Callable[[Path], int]] = {
    "pytest-urirdp": session_pytest_urirdp,
    "pytest-urisys": session_pytest_urisys,
    "pytest-urisys-node": session_pytest_urisys_node,
    "urirdp-mock-docker": session_urirdp_mock_docker,
    "urirdp-real-docker": session_urirdp_real_docker,
    "urirdp-rdp-e2e": session_urirdp_rdp_e2e,
    "automation-lab": session_automation_lab,
    "lab-10-flows": session_lab_10_flows,
    "urisys-node-docker-gui": session_urisys_node_docker_gui,
    "office-simulate": session_office_simulate,
    "office-simulate-lenovo": session_office_simulate_lenovo,
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

    run_dir = args.output / (args.run_id or run_id())
    run_dir.mkdir(parents=True, exist_ok=True)

    names = [s.strip() for s in args.sessions.split(",") if s.strip()] or DEFAULT_ORDER
    manifest = {"run_id": run_dir.name, "started_at": now_iso(), "host": host_id(), "sessions": names}
    save_json(run_dir / "manifest.json", manifest)

    if any(n in names for n in ("urirdp-mock-docker", "urirdp-real-docker", "urirdp-rdp-e2e")):
        lab = ROOT / "urisys-automation-lab"
        run_cmd(["bash", "scripts/docker-down.sh"], cwd=lab, log_file=run_dir / "preflight.log")

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

    manifest["finished_at"] = now_iso()
    manifest["results"] = results
    save_json(run_dir / "manifest.json", manifest)

    subprocess.run([sys.executable, str(REPORT_SCRIPT), "analyze", str(run_dir)], check=False)
    print(f"\nRun directory: {run_dir}")
    print(f"Analysis: {run_dir / 'analysis.md'}")
    return 0 if all(rc == 0 for rc in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
