"""urisys node serve pre-installs uriscreen/urishell before urisys-node boot."""

from __future__ import annotations

from unittest.mock import patch

from urisys.cli.commands.node import _prepare_node_serve


def test_prepare_node_serve_installs_core_packs():
    with patch("urisys.node_install.is_importable", return_value=True):
        with patch(
            "urisys.node_install.ensure_core_node_packs",
            return_value={"ok": True, "skipped": True},
        ) as core:
            assert _prepare_node_serve(auto_install=True) is None
    core.assert_called_once()


def test_prepare_node_serve_fails_when_core_packs_missing():
    with patch("urisys.node_install.is_importable", return_value=True):
        with patch(
            "urisys.node_install.ensure_core_node_packs",
            return_value={"ok": False, "error": "network", "specs": ["uriscreen.whl"]},
        ):
            assert _prepare_node_serve(auto_install=True) == 1


def test_prepare_node_serve_skipped_when_auto_install_off():
    with patch("urisys.node_install.ensure_core_node_packs") as core:
        assert _prepare_node_serve(auto_install=False) is None
    core.assert_not_called()
