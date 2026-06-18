"""Node boot packs (uriscreen, urishell) diagnostics and install hooks."""

from __future__ import annotations

from unittest.mock import patch

from urisys.doctor import run_doctor
from urisys.node_install import CORE_NODE_PACK_SPECS, diagnose_urisys_node, ensure_core_node_packs


def test_core_pack_specs_use_github_wheels():
    assert all("github.com/tellmesh" in s for s in CORE_NODE_PACK_SPECS)
    assert any("uriscreen" in s for s in CORE_NODE_PACK_SPECS)
    assert any("urishell" in s for s in CORE_NODE_PACK_SPECS)


def test_doctor_reports_missing_core_packs_when_node_without_screen():
    with patch("urisys.node_install.is_importable", return_value=True):
        with patch("urisys.node_install._missing_core_node_modules", return_value=[CORE_NODE_PACK_SPECS[0]]):
            out = run_doctor(min_version=None)
    core = [c for c in out["checks"] if c["id"] == "node_core_packs"]
    assert core and core[0]["status"] == "fail"
    assert "uriscreen" in core[0]["message"]


def test_ensure_core_packs_skips_when_present():
    with patch("urisys.node_install._missing_core_node_modules", return_value=[]):
        out = ensure_core_node_packs()
    assert out.get("ok") is True
    assert out.get("skipped") is True


def test_diagnose_includes_screen_flags():
    with patch("urisys.node_install.is_importable", return_value=True):
        with patch("urisys.node_install._missing_core_node_modules", return_value=[]):
            with patch("urisys.node_install.importlib.util.find_spec", return_value=object()):
                diag = diagnose_urisys_node()
    assert diag["uriscreen_importable"] is True
    assert diag["urishell_importable"] is True
    assert diag["missing_core_packs"] == []
