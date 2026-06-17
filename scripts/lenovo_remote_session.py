#!/usr/bin/env python3
"""Run remote URI flow suites from urisys-examples, save responses, write session report.

Flows live in ``../urisys-examples/`` (override with ``URISYS_EXAMPLES_ROOT`` or ``--examples-root``).

  python3 scripts/lenovo_remote_session.py
  python3 scripts/lenovo_remote_session.py --wait 120 --build-wheels
  python3 scripts/lenovo_remote_session.py --flows lenovo-remote/08-kvm-linkedin.uri.flow.yaml

Single step via Python CLI (no bash scripts):

  python3 -m urisysnode.remote call "kv://lenovo/runtime/query/discover"
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
NODE_ROOT = ROOT.parent / "urisys-node"
SCRIPTS_DIR = Path(__file__).resolve().parent
for _p in (str(NODE_ROOT), str(SCRIPTS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from session_core import (  # noqa: E402
    backfill_session_images,
    default_examples_root,
    expand_step_wheels,
    extract_step_screenshots,
    now_iso,
    resolve_flow_ref,
    save_json,
    step_ok,
)

EXAMPLES_ROOT = default_examples_root(urisys_root=ROOT)
DEFAULT_MANIFEST = EXAMPLES_ROOT / "lenovo-remote" / "session.manifest.yaml"
from urisysnode.remote import (  # noqa: E402
    call_uri,
    default_endpoint,
    default_route_map,
    health as remote_health,
    schedule_restart,
    wait_health,
)

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

# Wheel server on the dev host (192.168.188.212) serving locally-built wheels to
# the lenovo slave; overridable per-session via manifest `wheel_server:`.
DEFAULT_WHEEL_SERVER = "http://192.168.188.212:8765"


def load_yaml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    # minimal fallback: only for manifest listing — flows need pyyaml
    raise RuntimeError("PyYAML required: pip install pyyaml")


def http_get(endpoint: str, path: str, *, timeout: float = 30.0) -> dict[str, Any]:
    url = endpoint.rstrip("/") + path
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                data = {"raw": body}
            return {"ok": True, "url": url, "status": resp.status, "body": data}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "url": url, "status": exc.code, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "url": url, "error": str(exc)}


def run_step(
    step: dict[str, Any],
    *,
    endpoint: str,
    route_map: str,
    defaults: dict[str, Any],
) -> dict[str, Any]:
    step_id = str(step.get("id") or "step")
    kind = step.get("kind")
    started = now_iso()
    out: dict[str, Any] = {"id": step_id, "started_at": started, "note": step.get("note")}

    try:
        if kind == "http_get":
            out["kind"] = "http_get"
            out["response"] = http_get(endpoint, str(step.get("path") or "/health"))
        elif kind == "host_sleep":
            seconds = float(step.get("seconds") or step.get("sleep") or 5)
            out["kind"] = "host_sleep"
            out["seconds"] = seconds
            time.sleep(seconds)
            out["response"] = {"ok": True, "slept": seconds}
        elif kind == "host_restart_and_wait":
            timeout = float(step.get("timeout") or step.get("seconds") or 90)
            expect = step.get("expect") if isinstance(step.get("expect"), dict) else {}
            settle_s = float(step.get("settle_s") or 3)
            out["kind"] = "host_restart_and_wait"
            out["timeout"] = timeout
            if expect:
                out["expect"] = expect
            baseline_id = None
            try:
                baseline = remote_health(endpoint=endpoint)
                baseline_id = baseline.get("instance_id")
                out["baseline_instance_id"] = baseline_id
            except Exception as exc:
                out["baseline_error"] = str(exc)
            try:
                out["restart"] = schedule_restart(endpoint=endpoint, route_map=route_map)
            except Exception as exc:
                msg = str(exc)
                if "Remote end closed connection" not in msg and "Connection reset" not in msg:
                    out["error"] = msg
                    out["response"] = {"ok": False, "error": msg}
                    out["finished_at"] = now_iso()
                    out["ok"] = False
                    return out
                out["restart"] = {"ok": True, "note": "connection closed during takeover", "error": msg}
            time.sleep(settle_s)
            deadline = time.time() + timeout
            last: dict[str, Any] = {"ok": False, "error": "unreachable"}
            while time.time() < deadline:
                try:
                    last = remote_health(endpoint=endpoint)
                except Exception as exc:
                    last = {"ok": False, "error": str(exc)}
                    time.sleep(2.0)
                    continue
                if not last.get("ok"):
                    time.sleep(2.0)
                    continue
                if expect and not all(last.get(k) == v for k, v in expect.items()):
                    time.sleep(2.0)
                    continue
                new_id = last.get("instance_id")
                if baseline_id and new_id == baseline_id:
                    time.sleep(2.0)
                    continue
                out["response"] = last
                break
            else:
                out["error"] = (
                    f"restart wait failed after {timeout}s expect={expect!r} "
                    f"baseline={baseline_id!r} last={last!r}"
                )
                out["response"] = last
        elif kind == "host_schedule_restart":
            out["kind"] = "host_schedule_restart"
            try:
                out["response"] = schedule_restart(
                    endpoint=endpoint,
                    route_map=route_map,
                )
            except Exception as exc:
                msg = str(exc)
                if "Remote end closed connection" in msg or "Connection reset" in msg:
                    out["response"] = {"ok": True, "note": "connection closed during takeover", "error": msg}
                else:
                    out["error"] = msg
                    out["response"] = {"ok": False, "error": msg}
        elif kind == "host_wait_health":
            timeout = float(step.get("timeout") or step.get("seconds") or 60)
            expect = step.get("expect") if isinstance(step.get("expect"), dict) else {}
            out["kind"] = "host_wait_health"
            out["timeout"] = timeout
            if expect:
                out["expect"] = expect
            deadline = time.time() + timeout
            last: dict[str, Any] = {"ok": False, "error": "unreachable"}
            try:
                while time.time() < deadline:
                    try:
                        last = remote_health(endpoint=endpoint)
                    except Exception as exc:
                        last = {"ok": False, "error": str(exc)}
                        time.sleep(2.0)
                        continue
                    if last.get("ok") and all(last.get(k) == v for k, v in expect.items()):
                        out["response"] = last
                        break
                    time.sleep(2.0)
                else:
                    out["error"] = f"health expect not met after {timeout}s: {expect!r} last={last!r}"
                    out["response"] = last
            except TimeoutError as exc:
                out["error"] = str(exc)
                out["response"] = {"ok": False, "error": str(exc)}
        else:
            uri = str(step.get("uri") or "")
            if not uri:
                raise ValueError("step requires uri or kind:http_get")
            payload = dict(step.get("payload") or {})
            ctx = {
                "approved": bool(defaults.get("approved", True)),
                "dry_run": bool(defaults.get("dry_run", False)),
                "allow_real": bool(defaults.get("allow_real", True)),
            }
            for key in ("approved", "dry_run", "allow_real"):
                if key in step:
                    ctx[key] = bool(step[key])
            out["kind"] = "uri_call"
            out["uri"] = uri
            out["payload"] = payload
            out["context"] = ctx
            out["response"] = call_uri(
                uri,
                payload=payload,
                approved=ctx["approved"],
                dry_run=ctx["dry_run"],
                allow_real=ctx["allow_real"],
                route_map=route_map,
            )
    except Exception as exc:
        out["error"] = str(exc)
        out["response"] = {"ok": False, "error": str(exc)}

    out["finished_at"] = now_iso()
    out["ok"] = step_ok(out)
    return out


def run_flow(
    flow_path: Path,
    *,
    endpoint: str,
    route_map: str,
    session_dir: Path,
    wheel_server: str,
    wheel_deploy_dir: Path,
    examples_root: Path,
) -> dict[str, Any]:
    data = load_yaml(flow_path)
    flow = data.get("flow") or {}
    flow_id = str(flow.get("id") or flow_path.stem)
    defaults = dict(data.get("defaults") or {})
    steps_raw = data.get("do") or []

    record: dict[str, Any] = {
        "flow_id": flow_id,
        "flow_path": str(flow_path.relative_to(examples_root) if flow_path.is_relative_to(examples_root) else flow_path),
        "description": flow.get("description"),
        "started_at": now_iso(),
        "steps": [],
    }

    for raw in steps_raw:
        if isinstance(raw, str):
            step = {"id": raw.split("://", 1)[0], "uri": raw}
        elif isinstance(raw, dict) and len(raw) == 1 and not raw.get("id"):
            uri, payload = next(iter(raw.items()))
            step = {"id": uri.replace("://", "-").replace("/", "-")[:40], "uri": uri}
            if isinstance(payload, dict):
                step["payload"] = payload
        else:
            step = dict(raw)
        step = expand_step_wheels(step, wheel_server=wheel_server, deploy_dir=wheel_deploy_dir)
        result = run_step(step, endpoint=endpoint, route_map=route_map, defaults=defaults)
        extract_step_screenshots(result, session_dir=session_dir, flow_id=flow_id)
        record["steps"].append(result)
        save_json(session_dir / "responses" / f"{flow_id}__{result['id']}.json", result)

    record["finished_at"] = now_iso()
    record["ok"] = all(s.get("ok") for s in record["steps"]) if record["steps"] else False
    save_json(session_dir / "flows" / f"{flow_id}.json", record)
    return record


def append_log(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(line.rstrip() + "\n")


def build_wheels(deploy_dir: Path) -> None:
    deploy_dir.mkdir(parents=True, exist_ok=True)
    tellmesh = ROOT.parent
    for pkg in ("urikv", "uribrowser", "urioffice", "urimail", "uriimg2nl", "urivql", "urisys-node"):
        pkg_dir = tellmesh / pkg
        if pkg_dir.is_dir():
            subprocess.run(
                [sys.executable, "-m", "pip", "wheel", "-w", str(deploy_dir), str(pkg_dir), "-q"],
                check=False,
            )
    profile = tellmesh / "urisys-node" / "config" / "node-profile.lenovo.json"
    if profile.is_file():
        shutil.copy2(profile, deploy_dir / "node-profile.lenovo.json")


def start_wheel_server(deploy_dir: Path, host: str, port: int) -> subprocess.Popen[Any] | None:
    try:
        urllib.request.urlopen(f"http://{host}:{port}/", timeout=1)
        return None
    except Exception:
        pass
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", host, "--directory", str(deploy_dir)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    return proc


def write_session_md(session_dir: Path, meta: dict[str, Any], flow_records: list[dict[str, Any]]) -> None:
    lines = [
        "# Lenovo remote session",
        "",
        f"- **Session ID:** `{meta['session_id']}`",
        f"- **Started:** {meta['started_at']}",
        f"- **Host (dev):** {meta['host']}",
        f"- **Target:** {meta['endpoint']}",
        f"- **Node reachable at start:** {meta.get('node_reachable')}",
        "",
        "## Replay",
        "",
        "```bash",
        f"cd {ROOT}",
        "python3 scripts/lenovo_remote_session.py --session-dir " + str(session_dir.relative_to(ROOT)),
        "```",
        "",
        "Or single URI:",
        "",
        "```bash",
        "cd " + str(NODE_ROOT),
        'python3 -m urisysnode.remote call "kv://lenovo/runtime/query/discover"',
        "```",
        "",
        "## Flow results",
        "",
        "| Flow | OK | Steps pass | Notes |",
        "|------|-----|------------|-------|",
    ]
    for fr in flow_records:
        passed = sum(1 for s in fr.get("steps", []) if s.get("ok"))
        total = len(fr.get("steps", []))
        note = fr.get("description") or ""
        lines.append(
            f"| `{fr['flow_id']}` | {'✅' if fr.get('ok') else '❌'} | {passed}/{total} | {note[:60]} |"
        )

    lines.extend(["", "## Step detail", ""])
    for fr in flow_records:
        lines.append(f"### {fr['flow_id']}")
        lines.append("")
        for step in fr.get("steps", []):
            icon = "✅" if step.get("ok") else "❌"
            uri = step.get("uri") or step.get("response", {}).get("url") or step.get("kind")
            err = step.get("error") or (step.get("response") or {}).get("error")
            lines.append(f"- {icon} **{step['id']}** — `{uri}`")
            if err:
                lines.append(f"  - error: `{err}`")
            if step.get("note"):
                lines.append(f"  - note: {step['note']}")
            for shot in step.get("screenshots") or []:
                lines.append(f"  - screenshot: `{shot}`")
        lines.append("")

    lines.extend([
        "## Lessons",
        "",
    ])
    if not meta.get("node_reachable"):
        lines.append("- Node was **down** at session start — start on lenovo: `source ~/venv/bin/activate && urisys node serve --host 0.0.0.0 --port 8790`")
    failed = [s for fr in flow_records for s in fr.get("steps", []) if not s.get("ok")]
    if failed:
        lines.append(f"- **{len(failed)}** step(s) failed — see `responses/*.json`")
    else:
        lines.append("- All steps passed.")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    lines.append(f"- Flow copies: `{session_dir.relative_to(ROOT)}/flows/`")
    lines.append(f"- Responses: `{session_dir.relative_to(ROOT)}/responses/`")
    lines.append(f"- Screenshots: `{session_dir.relative_to(ROOT)}/screenshots/` (extracted from base64)")
    lines.append(f"- Manifest: `{meta.get('manifest_path', 'session.manifest.yaml')}`")
    lines.append("")

    (session_dir / "SESSION.md").write_text("\n".join(lines), encoding="utf-8")


def resolve_flow_paths(
    manifest_path: Path,
    explicit: list[str] | None,
    *,
    examples_root: Path,
) -> list[Path]:
    suite_dir = manifest_path.parent.resolve()
    if explicit:
        return [resolve_flow_ref(p, suite_dir=suite_dir, examples_root=examples_root) for p in explicit]
    data = load_yaml(manifest_path)
    flows = data.get("flows") or []
    return [resolve_flow_ref(f, suite_dir=suite_dir, examples_root=examples_root) for f in flows]


def resolve_route_map(manifest_path: Path, cli_route_map: str | None) -> str:
    if cli_route_map and cli_route_map != default_route_map():
        return cli_route_map
    data = load_yaml(manifest_path)
    session = data.get("session") if isinstance(data.get("session"), dict) else {}
    rel = session.get("route_map")
    if isinstance(rel, str) and rel.strip():
        candidate = (manifest_path.parent / rel).resolve()
        if candidate.is_file():
            return str(candidate)
    return cli_route_map or default_route_map()


def load_manifest_session(manifest_path: Path) -> dict[str, Any]:
    data = load_yaml(manifest_path)
    return data.get("session") if isinstance(data.get("session"), dict) else {}


UPGRADE_PLAYWRIGHT_FLOW = EXAMPLES_ROOT / "lenovo-remote/_upgrade-playwright.uri.flow.yaml"
UPGRADE_KVM_FLOW = EXAMPLES_ROOT / "lenovo-remote/_upgrade-kvm.uri.flow.yaml"
UPGRADE_NODE_FLOW = EXAMPLES_ROOT / "lenovo-remote/_upgrade-node.uri.flow.yaml"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lenovo remote session runner (flow-based, Python only).")
    parser.add_argument("--endpoint", default=os.environ.get("URISYS_LENOVO_ENDPOINT", default_endpoint()))
    parser.add_argument("--route-map", default=None, help="Route map YAML (default: manifest session.route_map)")
    parser.add_argument(
        "--examples-root",
        default=str(EXAMPLES_ROOT),
        help="Root of urisys-examples (or URISYS_EXAMPLES_ROOT)",
    )
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="Session manifest YAML")
    parser.add_argument(
        "--flows",
        nargs="*",
        help="Flow files relative to examples root or suite dir (default: all from manifest)",
    )
    parser.add_argument("--wait", type=float, default=0, help="Wait up to N seconds for node /health")
    parser.add_argument("--build-wheels", action="store_true", help="Build pack wheels to /tmp/urisys-deploy")
    parser.add_argument("--serve-wheels", action="store_true", help="Start python -m http.server for wheels")
    parser.add_argument("--session-dir", default="", help="Reuse existing session dir (replay doc only)")
    parser.add_argument("--run-id", default="")
    parser.add_argument(
        "--extract-images",
        metavar="SESSION_DIR",
        help="Extract base64 images from existing session responses to screenshots/ (no flows run)",
    )
    args = parser.parse_args(argv)

    if args.extract_images:
        session_dir = Path(args.extract_images)
        if not session_dir.is_dir():
            print(json.dumps({"ok": False, "error": f"not a directory: {session_dir}"}), file=sys.stderr)
            return 2
        saved = backfill_session_images(session_dir)
        print(json.dumps({"ok": True, "session_dir": str(session_dir), "screenshots": saved}, indent=2))
        return 0

    if yaml is None:
        print("ERROR: pip install pyyaml", file=sys.stderr)
        return 2

    run_id = args.run_id or datetime.now(timezone.utc).strftime("lenovo-remote-%Y%m%d-%H%M%S")
    session_dir = Path(args.session_dir) if args.session_dir else ROOT / "output" / "test-sessions" / run_id
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "responses").mkdir(exist_ok=True)
    (session_dir / "flows").mkdir(exist_ok=True)
    log_path = session_dir / "session.log"

    manifest_path = Path(args.manifest).resolve()
    examples_root = Path(args.examples_root).expanduser().resolve()
    if not manifest_path.is_file():
        print(json.dumps({"ok": False, "error": f"manifest not found: {manifest_path}"}), file=sys.stderr)
        return 2

    route_map = resolve_route_map(manifest_path, args.route_map or os.environ.get("URISYS_ROUTE_MAP"))
    session_cfg = load_manifest_session(manifest_path)
    wheel_server = str(session_cfg.get("wheel_server") or DEFAULT_WHEEL_SERVER)
    wheel_deploy_dir = Path(str(session_cfg.get("wheel_deploy_dir") or "/tmp/urisys-deploy"))

    wheel_proc = None
    if args.build_wheels:
        build_wheels(wheel_deploy_dir)
    if args.serve_wheels:
        parsed_ws = urllib.parse.urlparse(wheel_server)
        default_ws = urllib.parse.urlparse(DEFAULT_WHEEL_SERVER)
        host = parsed_ws.hostname or default_ws.hostname
        port = parsed_ws.port or default_ws.port
        wheel_proc = start_wheel_server(wheel_deploy_dir, host, port)

    node_reachable = False
    health_data: dict[str, Any] = {}
    append_log(log_path, f"[{now_iso()}] session start target={args.endpoint}")

    if args.wait > 0:
        append_log(log_path, f"waiting up to {args.wait}s for node")
        try:
            health_data = wait_health(endpoint=args.endpoint, timeout_s=args.wait)
            node_reachable = bool(health_data.get("ok"))
        except TimeoutError as exc:
            append_log(log_path, f"wait failed: {exc}")
    else:
        try:
            health_data = remote_health(endpoint=args.endpoint)
            node_reachable = bool(health_data.get("ok"))
        except Exception as exc:
            append_log(log_path, f"health failed: {exc}")
            health_data = {"ok": False, "error": str(exc)}

    save_json(session_dir / "responses" / "_00_preflight_health.json", health_data)

    flow_paths = resolve_flow_paths(manifest_path, args.flows, examples_root=examples_root)
    flows_copy = session_dir / "flow-sources"
    flows_copy.mkdir(exist_ok=True)
    for fp in flow_paths:
        if fp.exists():
            shutil.copy2(fp, flows_copy / fp.name)
    shutil.copy2(manifest_path, session_dir / "session.manifest.yaml")

    meta = {
        "session_id": run_id,
        "session_name": session_cfg.get("id") or "lenovo-remote",
        "suite": "remote-node-flows",
        "started_at": now_iso(),
        "host": os.uname().nodename,
        "endpoint": args.endpoint,
        "route_map": route_map,
        "examples_root": str(examples_root),
        "manifest_path": str(manifest_path),
        "node_reachable": node_reachable,
        "flow_files": [
            str(p.relative_to(examples_root) if p.is_relative_to(examples_root) else p) for p in flow_paths
        ],
    }
    save_json(session_dir / "meta.json", meta)

    flow_records: list[dict[str, Any]] = []
    upgrade_ran = False
    kvm_upgrade_ran = False
    node_upgrade_ran = False

    def _needs_node_upgrade(flow_paths: list[Path]) -> bool:
        names = {p.name for p in flow_paths}
        return bool(
            names
            & {
                "02-install-packs.uri.flow.yaml",
                "07-playwright-linkedin.uri.flow.yaml",
            }
            or any("install-packs" in p.name for p in flow_paths)
        )

    def _run_one(fp: Path) -> dict[str, Any]:
        return run_flow(
            fp,
            endpoint=args.endpoint,
            route_map=route_map,
            session_dir=session_dir,
            wheel_server=wheel_server,
            wheel_deploy_dir=wheel_deploy_dir,
            examples_root=examples_root,
        )

    for fp in flow_paths:
        append_log(log_path, f"flow {fp.name} start")
        if not fp.exists():
            rec = {"flow_id": fp.stem, "ok": False, "error": "flow file missing", "steps": []}
            flow_records.append(rec)
            continue
        if fp.name != "01-health-probe.uri.flow.yaml":
            try:
                health_data = remote_health(endpoint=args.endpoint)
                node_reachable = bool(health_data.get("ok"))
                if node_reachable:
                    meta["node_reachable"] = True
                    save_json(session_dir / "responses" / "_00_preflight_health.json", health_data)
            except Exception as exc:
                node_reachable = False
                append_log(log_path, f"health re-check failed: {exc}")
        if not node_reachable and fp.name != "01-health-probe.uri.flow.yaml":
            rec = {
                "flow_id": load_yaml(fp).get("flow", {}).get("id", fp.stem),
                "flow_path": str(
                    fp.relative_to(examples_root) if fp.is_relative_to(examples_root) else fp
                ),
                "ok": False,
                "skipped": True,
                "reason": "node unreachable (see 01-health-probe)",
                "steps": [],
            }
            flow_records.append(rec)
            save_json(session_dir / "flows" / f"{rec['flow_id']}.json", rec)
            append_log(log_path, f"flow {fp.name} skipped (node down)")
            continue
        if (
            not node_upgrade_ran
            and UPGRADE_NODE_FLOW.exists()
            and _needs_node_upgrade(flow_paths)
            and fp.name != "01-health-probe.uri.flow.yaml"
        ):
            append_log(log_path, f"flow {UPGRADE_NODE_FLOW.name} start (urisys-node wheel)")
            node_rec = _run_one(UPGRADE_NODE_FLOW)
            flow_records.append(node_rec)
            node_upgrade_ran = True
            append_log(log_path, f"flow {UPGRADE_NODE_FLOW.name} ok={node_rec.get('ok')}")
            if not node_rec.get("ok"):
                append_log(log_path, f"flow {fp.name} skipped (node upgrade failed)")
                continue
            node_reachable = True
            meta["node_reachable"] = True
        if (
            fp.name == "08-kvm-linkedin.uri.flow.yaml"
            and UPGRADE_KVM_FLOW.exists()
            and not kvm_upgrade_ran
        ):
            append_log(log_path, f"flow {UPGRADE_KVM_FLOW.name} start (pre-08 kvm upgrade)")
            kvm_rec = _run_one(UPGRADE_KVM_FLOW)
            flow_records.append(kvm_rec)
            kvm_upgrade_ran = True
            append_log(log_path, f"flow {UPGRADE_KVM_FLOW.name} ok={kvm_rec.get('ok')}")
            if not kvm_rec.get("ok"):
                append_log(log_path, f"flow {fp.name} skipped (kvm upgrade failed)")
                continue
        if (
            fp.name == "07-playwright-linkedin.uri.flow.yaml"
            and UPGRADE_PLAYWRIGHT_FLOW.exists()
            and not upgrade_ran
        ):
            append_log(log_path, f"flow {UPGRADE_PLAYWRIGHT_FLOW.name} start (pre-07 upgrade)")
            up_rec = _run_one(UPGRADE_PLAYWRIGHT_FLOW)
            flow_records.append(up_rec)
            upgrade_ran = True
            append_log(log_path, f"flow {UPGRADE_PLAYWRIGHT_FLOW.name} ok={up_rec.get('ok')}")
            if not up_rec.get("ok"):
                append_log(log_path, f"flow {fp.name} skipped (upgrade failed)")
                continue
            node_reachable = True
            meta["node_reachable"] = True
        rec = _run_one(fp)
        flow_records.append(rec)
        append_log(log_path, f"flow {fp.name} ok={rec.get('ok')}")

    meta["steps"] = [
        {
            "name": f"{rec.get('flow_id', 'flow')}__{s['id']}",
            "status": "pass" if s.get("ok") else "fail",
            "uri": s.get("uri"),
            "response_file": f"responses/{rec.get('flow_id', 'flow')}__{s['id']}.json",
            "screenshot": (s.get("screenshots") or [None])[0],
            "detail": "" if s.get("ok") else str(s.get("error") or "not ok")[:300],
        }
        for rec in flow_records
        for s in rec.get("steps") or []
    ]

    meta["finished_at"] = now_iso()
    meta["flows_ok"] = sum(1 for r in flow_records if r.get("ok"))
    meta["flows_total"] = len(flow_records)
    save_json(session_dir / "meta.json", meta)
    write_session_md(session_dir, meta, flow_records)

    report_script = ROOT / "scripts" / "session_report.py"
    if report_script.exists():
        subprocess.run([sys.executable, str(report_script), "generate", str(session_dir)], check=False)

    if wheel_proc:
        wheel_proc.terminate()

    append_log(log_path, f"session done dir={session_dir}")
    print(json.dumps({"session_dir": str(session_dir), "node_reachable": node_reachable, "meta": meta}, indent=2))
    return 0 if node_reachable and all(r.get("ok") for r in flow_records if not r.get("skipped")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
