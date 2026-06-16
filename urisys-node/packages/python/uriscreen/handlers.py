from __future__ import annotations

import base64
import io
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any


def _screen_cfg(context: dict[str, Any]) -> dict[str, Any]:
    return context.get("config", {}).get("screen", {})


def _backend(context: dict[str, Any], payload: dict[str, Any]) -> str:
    return payload.get("backend") or _screen_cfg(context).get("default_backend", "mss")


def _output_dir(payload: dict[str, Any], context: dict[str, Any]) -> Path:
    raw = payload.get("output") or _screen_cfg(context).get("output_dir", "/tmp/urisys-screens")
    path = Path(raw)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _monitor_index(payload: dict[str, Any], context: dict[str, Any], monitor_param: str | None) -> int:
    if payload.get("monitor") is not None:
        return int(payload["monitor"])
    monitors = _screen_cfg(context).get("monitors") or {}
    if monitor_param == "primary":
        return int(monitors.get("primary", {}).get("index", 1))
    if monitor_param and monitor_param.isdigit():
        return int(monitor_param)
    return 1


def _store_latest(context: dict[str, Any], entry: dict[str, Any]) -> None:
    context.setdefault("state", {})["latest_screen"] = entry


def _mock_png(label: str) -> bytes:
    return base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
    )


def capture(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    backend = _backend(context, payload)
    monitor = _monitor_index(payload, context, context.get("params", {}).get("monitor"))
    out_dir = _output_dir(payload, context)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = out_dir / f"screen_{monitor}_{ts}.png"

    if context.get("dry_run") or backend == "mock":
        path.write_bytes(_mock_png("mock"))
        entry = {"path": str(path), "monitor": monitor, "mime": "image/png", "backend": "mock", "dry_run": bool(context.get("dry_run"))}
        _store_latest(context, entry)
        return entry

    if backend == "mss":
        if not (context.get("allow_real") or os.environ.get("URISYS_ALLOW_REAL") == "1"):
            raise PermissionError("screen capture requires allow_real=true or URISYS_ALLOW_REAL=1")
        try:
            import mss  # type: ignore
            from PIL import Image  # type: ignore
        except Exception as exc:
            raise RuntimeError("mss backend requires: pip install mss pillow") from exc
        with mss.mss() as sct:
            shot = sct.grab(sct.monitors[monitor])
            img = Image.frombytes("RGB", (shot.width, shot.height), shot.rgb)
            img.save(path, format="PNG")
        entry = {
            "path": str(path),
            "monitor": monitor,
            "mime": "image/png",
            "backend": "mss",
            "width": shot.width,
            "height": shot.height,
        }
        _store_latest(context, entry)
        return entry

    raise ValueError(f"unsupported screen backend: {backend}")


def frame(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    entry = capture(payload, context)
    raw = Path(entry["path"]).read_bytes()
    entry["base64"] = base64.b64encode(raw).decode("ascii")
    return entry


def capture_loop(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    count = int(payload.get("count", 3))
    interval = float(payload.get("interval", 1.0))
    shots = []
    for i in range(count):
        shots.append(capture({**payload, "index": i}, context))
        if interval > 0 and i < count - 1:
            time.sleep(interval)
    return {"count": len(shots), "shots": shots, "backend": _backend(context, payload)}
