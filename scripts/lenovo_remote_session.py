#!/usr/bin/env python3
"""Run lenovo remote test flows, save responses, write session report.

All tasks are defined as *.uri.flow.yaml under flows/lenovo-remote/ — replay with:

  python3 scripts/lenovo_remote_session.py
  python3 scripts/lenovo_remote_session.py --wait 120
  python3 scripts/lenovo_remote_session.py --flows flows/lenovo-remote/01-health-probe.uri.flow.yaml

Single step via Python CLI (no bash scripts):

  python3 -m urisysnode.remote call "kv://lenovo/runtime/query/discover"
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
NODE_ROOT = ROOT.parent / "urisys-node"
if str(NODE_ROOT) not in sys.path:
    sys.path.insert(0, str(NODE_ROOT))

from urisysnode.remote import (  # noqa: E402
    call_uri,
    default_endpoint,
    default_route_map,
    health as remote_health,
    wait_health,
)

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def step_ok(result: dict[str, Any]) -> bool:
    if result.get("error"):
        return False
    if result.get("kind") == "http_get":
        return bool(result.get("response", {}).get("ok"))
    resp = result.get("response")
    if isinstance(resp, dict):
        if resp.get("ok") is False:
            return False
        inner = resp.get("result")
        if isinstance(inner, dict) and inner.get("ok") is False:
            return False
        if isinstance(inner, dict) and inner.get("loaded") is False:
            return False
    return True


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
) -> dict[str, Any]:
    data = load_yaml(flow_path)
    flow = data.get("flow") or {}
    flow_id = str(flow.get("id") or flow_path.stem)
    defaults = dict(data.get("defaults") or {})
    steps_raw = data.get("do") or []

    record: dict[str, Any] = {
        "flow_id": flow_id,
        "flow_path": str(flow_path.relative_to(ROOT)),
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
        result = run_step(step, endpoint=endpoint, route_map=route_map, defaults=defaults)
        extract_step_screenshots(result, session_dir=session_dir, flow_id=flow_id)
        record["steps"].append(result)
        save_json(session_dir / "responses" / f"{flow_id}__{result['id']}.json", result)

    record["finished_at"] = now_iso()
    record["ok"] = all(s.get("ok") for s in record["steps"]) if record["steps"] else False
    save_json(session_dir / "flows" / f"{flow_id}.json", record)
    return record


def _image_ext(mime: str) -> str:
    mime = (mime or "image/png").lower()
    if "jpeg" in mime or "jpg" in mime:
        return "jpg"
    if "webp" in mime:
        return "webp"
    return "png"


def _write_base64_image(b64: str, dest: Path) -> int:
    raw = base64.b64decode(b64)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    return len(raw)


def _extract_images_from_dict(
    obj: dict[str, Any],
    *,
    session_dir: Path,
    filename: str,
    strip_base64: bool,
) -> list[str]:
    """Extract base64 image from dict (and nested shots[]) to screenshots/."""
    saved: list[str] = []
    b64 = obj.get("base64")
    if isinstance(b64, str) and len(b64) > 100:
        ext = _image_ext(str(obj.get("mime") or ""))
        rel = f"screenshots/{filename}.{ext}"
        size = _write_base64_image(b64, session_dir / rel)
        saved.append(rel)
        if strip_base64:
            obj.pop("base64", None)
            obj["screenshot_file"] = rel
            obj["screenshot_bytes"] = size

    shots = obj.get("shots")
    if isinstance(shots, list):
        for i, shot in enumerate(shots):
            if isinstance(shot, dict):
                saved.extend(
                    _extract_images_from_dict(
                        shot,
                        session_dir=session_dir,
                        filename=f"{filename}_shot{i}",
                        strip_base64=strip_base64,
                    )
                )
    return saved


def extract_step_screenshots(
    step: dict[str, Any],
    *,
    session_dir: Path,
    flow_id: str,
    strip_base64: bool = True,
) -> list[str]:
    """Write embedded base64 from URI response to session_dir/screenshots/."""
    resp = step.get("response")
    if not isinstance(resp, dict):
        return []
    result = resp.get("result")
    if not isinstance(result, dict):
        return []
    step_id = str(step.get("id") or "step")
    saved = _extract_images_from_dict(
        result,
        session_dir=session_dir,
        filename=f"{flow_id}__{step_id}",
        strip_base64=strip_base64,
    )
    if saved:
        step["screenshots"] = saved
    return saved


def backfill_session_images(session_dir: Path, *, strip_base64: bool = True) -> list[str]:
    """Extract images from all response JSON files (also for past sessions)."""
    responses = session_dir / "responses"
    if not responses.is_dir():
        return []
    all_saved: list[str] = []
    for path in sorted(responses.glob("*.json")):
        if path.name.startswith("_"):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        stem = path.stem
        flow_id, _, step_id = stem.partition("__")
        if not step_id:
            continue
        data["id"] = step_id
        saved = extract_step_screenshots(
            data,
            session_dir=session_dir,
            flow_id=flow_id,
            strip_base64=strip_base64,
        )
        if saved:
            save_json(path, data)
            all_saved.extend(saved)
    return all_saved


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_log(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(line.rstrip() + "\n")


def build_wheels(deploy_dir: Path) -> None:
    deploy_dir.mkdir(parents=True, exist_ok=True)
    tellmesh = ROOT.parent
    for pkg in ("urikv", "uribrowser", "urioffice", "urimail", "urisys-node"):
        pkg_dir = tellmesh / pkg
        if pkg_dir.is_dir():
            subprocess.run(
                [sys.executable, "-m", "pip", "wheel", "-w", str(deploy_dir), str(pkg_dir), "-q"],
                check=False,
            )


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
    lines.append(f"- Manifest: `flows/lenovo-remote/session.manifest.yaml`")
    lines.append("")

    (session_dir / "SESSION.md").write_text("\n".join(lines), encoding="utf-8")


def resolve_flow_paths(manifest_path: Path, explicit: list[str] | None) -> list[Path]:
    if explicit:
        return [ROOT / p if not Path(p).is_absolute() else Path(p) for p in explicit]
    data = load_yaml(manifest_path)
    flows = data.get("flows") or []
    return [ROOT / f for f in flows]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lenovo remote session runner (flow-based, Python only).")
    parser.add_argument("--endpoint", default=os.environ.get("URISYS_LENOVO_ENDPOINT", default_endpoint()))
    parser.add_argument("--route-map", default=os.environ.get("URISYS_ROUTE_MAP", default_route_map()))
    parser.add_argument("--manifest", default=str(ROOT / "flows/lenovo-remote/session.manifest.yaml"))
    parser.add_argument("--flows", nargs="*", help="Specific flow files (default: all from manifest)")
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

    wheel_proc = None
    if args.build_wheels:
        build_wheels(Path("/tmp/urisys-deploy"))
    if args.serve_wheels:
        wheel_proc = start_wheel_server(Path("/tmp/urisys-deploy"), "192.168.188.212", 8765)

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

    manifest_path = Path(args.manifest)
    flow_paths = resolve_flow_paths(manifest_path, args.flows)
    flows_copy = session_dir / "flow-sources"
    flows_copy.mkdir(exist_ok=True)
    for fp in flow_paths:
        if fp.exists():
            shutil.copy2(fp, flows_copy / fp.name)
    shutil.copy2(manifest_path, session_dir / "session.manifest.yaml")

    meta = {
        "session_id": run_id,
        "session_name": "lenovo-remote",
        "suite": "remote-node-flows",
        "started_at": now_iso(),
        "host": os.uname().nodename,
        "endpoint": args.endpoint,
        "route_map": args.route_map,
        "node_reachable": node_reachable,
        "flow_files": [str(p.relative_to(ROOT)) for p in flow_paths],
    }
    save_json(session_dir / "meta.json", meta)

    flow_records: list[dict[str, Any]] = []
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
                "flow_path": str(fp.relative_to(ROOT)),
                "ok": False,
                "skipped": True,
                "reason": "node unreachable (see 01-health-probe)",
                "steps": [],
            }
            flow_records.append(rec)
            save_json(session_dir / "flows" / f"{rec['flow_id']}.json", rec)
            append_log(log_path, f"flow {fp.name} skipped (node down)")
            continue
        rec = run_flow(fp, endpoint=args.endpoint, route_map=args.route_map, session_dir=session_dir)
        flow_records.append(rec)
        append_log(log_path, f"flow {fp.name} ok={rec.get('ok')}")

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
