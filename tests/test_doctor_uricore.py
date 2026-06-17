"""Doctor checks for wrong PyPI uricore package."""

from __future__ import annotations

from unittest.mock import patch

from urisys.doctor import _check_uricore_authentic


def test_check_uricore_authentic_fails_on_squatter():
    with patch(
        "urisys.uricore_install.diagnose_uricore",
        return_value={
            "uricore_dist": "0.1.2",
            "uri_control_importable": False,
            "wrong_pypi_package": True,
            "wheel_url": "https://github.com/tellmesh/uricore/releases/download/v0.1.8/uricore-0.1.8-py3-none-any.whl",
        },
    ), patch("urisys.uricore_install.is_wrong_uricore_installed", return_value=True):
        check = _check_uricore_authentic()
    assert check is not None
    assert check.status == "fail"
    assert check.id == "uricore_source"
    assert "squatter" in check.message.lower()
    assert check.detail is not None
    assert check.detail.get("auto_fix") == "urisys init"
