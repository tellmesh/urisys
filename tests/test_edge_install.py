"""Broken urisysedge metadata (dist-info without package) repair."""

from __future__ import annotations

from unittest.mock import patch

from urisys.edge_install import ensure_urisysedge, is_broken_install, repair_urisysedge


def test_repair_calls_force_reinstall_when_broken():
    with (
        patch("urisys.edge_install.is_importable", return_value=False),
        patch("urisys.edge_install._dist_version", return_value="0.1.1"),
        patch("urisys.edge_install.pip_run") as pip_run,
    ):
        pip_run.side_effect = [
            {"ok": True, "command": "uninstall", "exit_code": 0, "stdout": "", "stderr": ""},
            {"ok": True, "command": "install", "exit_code": 0, "stdout": "", "stderr": ""},
        ]
        with patch("urisys.edge_install.is_importable", side_effect=[False, False, True]):
            result = repair_urisysedge()
    assert result["ok"] is True
    assert pip_run.call_count >= 1
    assert any("--force-reinstall" in str(c) for c in pip_run.call_args_list)


def test_ensure_short_circuits_when_importable():
    with patch("urisys.edge_install.is_importable", return_value=True):
        with patch("urisys.edge_install._dist_version", return_value="0.1.1"):
            result = ensure_urisysedge()
    assert result["ok"] is True
    assert result["already"] is True
