from __future__ import annotations

from typing import Any

from .common import mock_result, var


def status(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return mock_result("display.status", context, device=var(context, "device"), input="HDMI1", brightness=70)


def set_input(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    value = str(payload.get("input") or payload.get("value") or "HDMI1")
    return mock_result("display.set_input", context, device=var(context, "device"), input=value)


def set_brightness(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    value = int(payload.get("brightness") or payload.get("value") or 70)
    return mock_result("display.set_brightness", context, device=var(context, "device"), brightness=value)
