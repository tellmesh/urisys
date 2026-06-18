"""Tests for tellmesh uriguard install helper."""

from __future__ import annotations

from urisys.uriguard_install import diagnose_uriguard, wheel_url


def test_wheel_url_default():
    url = wheel_url()
    assert url.startswith("https://github.com/tellmesh/uriguard/releases/download/v")
    assert url.endswith("-py3-none-any.whl")


def test_diagnose_includes_wheel_url():
    diag = diagnose_uriguard()
    assert "wheel_url" in diag
    assert "uri_guard_importable" in diag
