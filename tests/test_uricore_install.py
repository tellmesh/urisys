"""Tests for tellmesh uricore install/repair (PyPI name collision)."""

from __future__ import annotations

from unittest.mock import patch

from urisys.uricore_install import diagnose_uricore, is_wrong_uricore_installed, wheel_url


def test_wheel_url_default():
    url = wheel_url()
    assert url.startswith("https://github.com/tellmesh/uricore/releases/download/v")
    assert url.endswith("-py3-none-any.whl")


def test_wrong_uricore_detected_when_squatter_present():
    with patch("urisys.uricore_install._dist_top_levels", return_value={"uricore"}), patch(
        "urisys.uricore_install._module_exists", return_value=False
    ), patch("urisys.uricore_install._pkg_version", return_value="0.1.2"):
        assert is_wrong_uricore_installed() is True


def test_not_wrong_when_uri_control_present():
    with patch("urisys.uricore_install._module_exists") as exists, patch(
        "urisys.uricore_install._pkg_version", return_value="0.1.8"
    ):
        exists.side_effect = lambda name: name == "uri_control"
        assert is_wrong_uricore_installed() is False


def test_diagnose_includes_wheel_url():
    with patch("urisys.uricore_install._module_exists", return_value=True), patch(
        "urisys.uricore_install._pkg_version", return_value="0.1.8"
    ):
        diag = diagnose_uricore()
    assert diag["uri_control_importable"] is True
    assert "wheel_url" in diag
