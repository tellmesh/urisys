from __future__ import annotations

import os
import subprocess
from typing import Any

from urirdp_kvm.display import allow_real, detect_display


def _mock(command: str, payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    args = payload.get("args") or []
    return {
        "driver": "mock",
        "command": command,
        "args": args,
        "display": detect_display(context),
    }


def shell_run(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    params = context.get("params") or {}
    command = str(params.get("command") or payload.get("command") or "")
    args = [str(a) for a in (payload.get("args") or [])]
    if not command:
        raise ValueError("shell command required")

    if context.get("dry_run") or not allow_real(context):
        return _mock(command, payload, context)

    env = os.environ.copy()
    display = detect_display(context)
    if display:
        env["DISPLAY"] = display
    xauth = context.get("xauthority")
    if xauth:
        env["XAUTHORITY"] = str(xauth)

    proc = subprocess.run(
        [command, *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=float(payload.get("timeout_s") or 120),
    )
    return {
        "driver": "subprocess",
        "command": command,
        "args": args,
        "exit_code": proc.returncode,
        "stdout": (proc.stdout or "")[-4000:],
        "stderr": (proc.stderr or "")[-2000:],
        "ok": proc.returncode == 0,
    }
