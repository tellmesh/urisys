"""Shared, side-effect-light primitives for test-session runners.

Both session runners (``run_test_sessions.py`` and ``lenovo_remote_session.py``)
need the same handful of pure helpers: timestamps, JSON dumping, the
pass/fail predicate for a recorded step, and base64-image extraction from URI
responses. They were duplicated; this is the single home so the two runners can
converge on one implementation.
"""

from __future__ import annotations

import base64
import json
import platform
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PACK_TO_WHEEL: dict[str, str] = {
    "kv": "urikv",
    "browser": "uribrowser",
    "office": "urioffice",
    "mail": "urimail",
    "uriimg2nl": "uriimg2nl",
    "urisys_node": "urisys_node",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def host_id() -> str:
    return f"{socket.gethostname()} ({platform.system()} {platform.machine()})"


def run_id(prefix: str = "", *, utc: bool = False) -> str:
    """Timestamped session id, e.g. '20260617-141828' or 'lenovo-remote-…' (utc)."""
    now = datetime.now(timezone.utc) if utc else datetime.now()
    return f"{prefix}{now.strftime('%Y%m%d-%H%M%S')}"


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def step_ok(result: dict[str, Any]) -> bool:
    """Whether a recorded step succeeded: no transport error and no inner ok=False."""
    if result.get("error"):
        return False
    if result.get("kind") == "http_get":
        return bool(result.get("response", {}).get("ok"))
    if result.get("kind") == "host_wait_health":
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


def image_ext(mime: str) -> str:
    mime = (mime or "image/png").lower()
    if "jpeg" in mime or "jpg" in mime:
        return "jpg"
    if "webp" in mime:
        return "webp"
    return "png"


def write_base64_image(b64: str, dest: Path) -> int:
    raw = base64.b64decode(b64)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    return len(raw)


def extract_images_from_dict(
    obj: dict[str, Any],
    *,
    session_dir: Path,
    filename: str,
    strip_base64: bool,
) -> list[str]:
    """Extract a base64 image (and nested shots[]) from a dict into screenshots/."""
    saved: list[str] = []
    b64 = obj.get("base64")
    if isinstance(b64, str) and len(b64) > 100:
        rel = f"screenshots/{filename}.{image_ext(str(obj.get('mime') or ''))}"
        size = write_base64_image(b64, session_dir / rel)
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
                    extract_images_from_dict(
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
    """Write embedded base64 from a URI-response step into session_dir/screenshots/."""
    resp = step.get("response")
    if not isinstance(resp, dict):
        return []
    result = resp.get("result")
    if not isinstance(result, dict):
        return []
    step_id = str(step.get("id") or "step")
    saved = extract_images_from_dict(
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
        flow_id, _, step_id = path.stem.partition("__")
        if not step_id:
            continue
        data["id"] = step_id
        saved = extract_step_screenshots(
            data, session_dir=session_dir, flow_id=flow_id, strip_base64=strip_base64
        )
        if saved:
            save_json(path, data)
            all_saved.extend(saved)
    return all_saved


def find_wheel_file(deploy_dir: Path, prefix: str) -> Path | None:
    candidates = sorted(deploy_dir.glob(f"{prefix}-*.whl"), reverse=True)
    return candidates[0] if candidates else None


def wheel_url(wheel_server: str, wheel_path: Path) -> str:
    return f"{wheel_server.rstrip('/')}/{wheel_path.name}"


def expand_step_wheels(
    step: dict[str, Any],
    *,
    wheel_server: str,
    deploy_dir: Path,
) -> dict[str, Any]:
    """Resolve ``wheel:`` / ``{wheel:pkg}`` placeholders to concrete wheel URLs."""
    step = dict(step)
    wheel_name = step.pop("wheel", None)
    payload = dict(step.get("payload") or {})

    if not wheel_name:
        pack = payload.get("pack")
        if (
            isinstance(pack, str)
            and pack in PACK_TO_WHEEL
            and not payload.get("specs")
            and payload.get("install")
        ):
            wheel_name = PACK_TO_WHEEL[pack]

    if wheel_name:
        whl = find_wheel_file(deploy_dir, str(wheel_name))
        if whl:
            specs = list(payload.get("specs") or [])
            if not specs:
                specs = ["urisysedge>=0.1.0", wheel_url(wheel_server, whl)]
            payload["specs"] = specs
            step["payload"] = payload

    payload = step.get("payload")
    if isinstance(payload, dict) and isinstance(payload.get("args"), list):
        new_args: list[Any] = []
        for arg in payload["args"]:
            if isinstance(arg, str) and arg.startswith("{wheel:") and arg.endswith("}"):
                name = arg[7:-1]
                whl = find_wheel_file(deploy_dir, name)
                new_args.append(wheel_url(wheel_server, whl) if whl else arg)
            else:
                new_args.append(arg)
        payload = dict(payload)
        payload["args"] = new_args
        step["payload"] = payload

    return step
