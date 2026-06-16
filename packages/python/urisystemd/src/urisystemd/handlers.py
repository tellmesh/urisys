from __future__ import annotations

from typing import Any

from .common import run_command, var


def status(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    unit = var(context, "unit")
    return run_command(["systemctl", "show", unit, "--no-page"], context)


def start(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return run_command(["systemctl", "start", var(context, "unit")], context)


def stop(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return run_command(["systemctl", "stop", var(context, "unit")], context)


def restart(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return run_command(["systemctl", "restart", var(context, "unit")], context)


def logs(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    unit = var(context, "unit")
    lines = str(payload.get("lines") or "50")
    return run_command(["journalctl", "-u", unit, "-n", lines, "--no-pager"], context)
