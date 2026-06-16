from __future__ import annotations

from typing import Any

from .common import mock_result, run_command, system_info, var


def info(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    target = var(context, "target", "local")
    return mock_result("desktop.info", context, target=target, **system_info())


def notify(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    target = var(context, "target", "local")
    title = str(payload.get("title") or "URI notification")
    message = str(payload.get("message") or payload.get("body") or "")
    # Real notification is intentionally platform-dependent; return mock unless integrator enables a backend.
    return mock_result("desktop.notify", context, target=target, title=title, message=message, delivered=True)


def open_url(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    url = str(payload.get("url") or "about:blank")
    # Python stdlib webbrowser is not used here by default to avoid surprising UI side effects.
    return mock_result("desktop.open_url", context, url=url, opened=True)


def shell(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    command = payload.get("command") or []
    if isinstance(command, str):
        command = command.split()
    if not isinstance(command, list) or not command:
        return {"ok": False, "error": "payload.command must be a string or non-empty list"}
    return run_command([str(x) for x in command], context, timeout=int(payload.get("timeout") or 15))
