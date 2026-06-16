from __future__ import annotations

import base64
import os
import platform
import subprocess
from typing import Any


def variables(context: dict[str, Any]) -> dict[str, Any]:
    return (context.get("variables") or context.get("params") or {}) if isinstance(context, dict) else {}


def var(context: dict[str, Any], name: str, default: Any = None) -> Any:
    return variables(context).get(name, context.get(name, default) if isinstance(context, dict) else default)


def real_mode(context: dict[str, Any]) -> bool:
    if bool(context.get("allow_real")):
        return True
    return os.environ.get("URISYS_ALLOW_REAL", "").lower() in {"1", "true", "yes", "on"}


def dry_run(context: dict[str, Any]) -> bool:
    return bool(context.get("dry_run")) or str(context.get("environment", "")).lower() in {"mock", "dry", "dry-run"}


def safe_mode(context: dict[str, Any]) -> bool:
    return dry_run(context) or not real_mode(context)


def system_info() -> dict[str, Any]:
    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "python": platform.python_version(),
    }


def mock_result(operation: str, context: dict[str, Any], **data: Any) -> dict[str, Any]:
    return {
        "ok": True,
        "mode": "mock" if safe_mode(context) else "real",
        "operation": operation,
        "variables": variables(context),
        **data,
    }


def run_command(command: list[str], context: dict[str, Any], timeout: int = 15) -> dict[str, Any]:
    if safe_mode(context):
        return {
            "ok": True,
            "mode": "mock",
            "command": command,
            "executed": False,
            "stdout": "",
            "stderr": "",
            "returncode": 0,
        }

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return {
        "ok": completed.returncode == 0,
        "mode": "real",
        "command": command,
        "executed": True,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "returncode": completed.returncode,
    }


def fake_png_data_url(label: str) -> str:
    # Tiny transparent PNG. Label is intentionally not encoded into the image; it stays in metadata.
    raw = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
    )
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")
