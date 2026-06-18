"""Tests for tellmesh uriresolver install helper."""

from __future__ import annotations

from urisys.uriresolver_install import diagnose_uriresolver, wheel_url


def test_wheel_url_default():
    url = wheel_url()
    assert url.startswith("https://github.com/tellmesh/uriresolver/releases/download/v")
    assert url.endswith("-py3-none-any.whl")


def test_diagnose_includes_wheel_url():
    diag = diagnose_uriresolver()
    assert "wheel_url" in diag
    assert "uri_resolver_importable" in diag
