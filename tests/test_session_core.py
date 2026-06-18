"""Characterization tests for the shared urisys_lab.core helpers."""

from __future__ import annotations

import base64
import json
from pathlib import Path

import urisys_lab.core as sc

_PNG_B64 = base64.b64encode(b"\x89PNG\r\n" + b"x" * 200).decode("ascii")


def test_step_ok_variants():
    assert sc.step_ok({"response": {"ok": True}}) is True
    assert sc.step_ok({"error": "boom"}) is False
    assert sc.step_ok({"kind": "http_get", "response": {"ok": False}}) is False
    assert sc.step_ok({"kind": "http_get", "response": {"ok": True}}) is True
    assert sc.step_ok({"response": {"ok": True, "result": {"ok": False}}}) is False
    assert sc.step_ok({"response": {"ok": True, "result": {"loaded": False}}}) is False
    assert sc.step_ok({"response": {"ok": True, "result": {"loaded": True}}}) is True


def test_image_ext():
    assert sc.image_ext("image/png") == "png"
    assert sc.image_ext("image/jpeg") == "jpg"
    assert sc.image_ext("image/webp") == "webp"
    assert sc.image_ext("") == "png"


def test_write_base64_image_roundtrip(tmp_path):
    dest = tmp_path / "shots" / "x.png"
    n = sc.write_base64_image(_PNG_B64, dest)
    assert dest.exists() and dest.stat().st_size == n
    assert dest.read_bytes() == base64.b64decode(_PNG_B64)


def test_extract_step_screenshots_strips_base64(tmp_path):
    step = {"id": "frame", "response": {"result": {"mime": "image/png", "base64": _PNG_B64}}}
    saved = sc.extract_step_screenshots(step, session_dir=tmp_path, flow_id="flowA")
    assert saved == ["screenshots/flowA__frame.png"]
    assert (tmp_path / saved[0]).exists()
    result = step["response"]["result"]
    assert "base64" not in result
    assert result["screenshot_file"] == saved[0]
    assert step["screenshots"] == saved


def test_extract_handles_nested_shots(tmp_path):
    step = {"id": "multi", "response": {"result": {"shots": [
        {"mime": "image/png", "base64": _PNG_B64},
        {"mime": "image/jpeg", "base64": _PNG_B64},
    ]}}}
    saved = sc.extract_step_screenshots(step, session_dir=tmp_path, flow_id="f")
    assert saved == ["screenshots/f__multi_shot0.png", "screenshots/f__multi_shot1.jpg"]


def test_extract_ignores_non_image_response(tmp_path):
    assert sc.extract_step_screenshots({"id": "x", "response": {"result": {"ok": True}}},
                                       session_dir=tmp_path, flow_id="f") == []


def test_backfill_session_images(tmp_path):
    resp_dir = tmp_path / "responses"
    resp_dir.mkdir()
    (resp_dir / "flowB__cap.json").write_text(
        json.dumps({"response": {"result": {"mime": "image/png", "base64": _PNG_B64}}}),
        encoding="utf-8",
    )
    saved = sc.backfill_session_images(tmp_path)
    assert saved == ["screenshots/flowB__cap.png"]
    assert (tmp_path / saved[0]).exists()
