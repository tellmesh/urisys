"""Tests for tellmesh uriguard install helper (legacy name: urirouter_install)."""

from __future__ import annotations

from urisys.urirouter_install import diagnose_urirouter, wheel_url


def test_wheel_url_default():
    url = wheel_url()
    assert url.startswith("https://github.com/tellmesh/uriguard/releases/download/v")
    assert url.endswith("-py3-none-any.whl")


def test_diagnose_includes_wheel_url():
    diag = diagnose_urirouter()
    assert "wheel_url" in diag
    assert "uri_guard_importable" in diag
