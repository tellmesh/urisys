from __future__ import annotations

from typing import Any

from .common import fake_png_data_url, mock_result, var


def status(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return mock_result("camera.status", context, device=var(context, "device"), online=True, resolution="1280x720")


def frame(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return mock_result("camera.frame", context, device=var(context, "device"), image_data_url=fake_png_data_url("camera-frame"))


def capture(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return mock_result("camera.capture", context, device=var(context, "device"), artifact="mock-camera-capture.png", image_data_url=fake_png_data_url("camera-capture"))
