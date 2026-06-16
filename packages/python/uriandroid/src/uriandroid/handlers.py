from __future__ import annotations

from typing import Any

from .common import fake_png_data_url, mock_result, run_command, var


def _adb_prefix(context: dict[str, Any]) -> list[str]:
    device = var(context, "device", "default")
    if device and device != "default":
        return ["adb", "-s", device]
    return ["adb"]


def status(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    result = run_command(_adb_prefix(context) + ["get-state"], context)
    result.setdefault("device", var(context, "device", "default"))
    return result


def tap(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    x = int(payload.get("x") or 0)
    y = int(payload.get("y") or 0)
    return run_command(_adb_prefix(context) + ["shell", "input", "tap", str(x), str(y)], context)


def open_url(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    url = str(payload.get("url") or "about:blank")
    return run_command(_adb_prefix(context) + ["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url], context)


def screenshot(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return mock_result(
        "android.screenshot",
        context,
        device=var(context, "device", "default"),
        image_data_url=fake_png_data_url("android"),
    )
