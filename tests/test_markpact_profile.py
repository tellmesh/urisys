"""Markpact profile v1alpha lint rules."""

from __future__ import annotations

from pathlib import Path

import pytest

from urisys.managers.markpact_manager import MarkpactManager
from urisys.managers.markpact_profile import declared_packs, declared_schemes, lint_markpact

TELLMESH = Path(__file__).resolve().parents[2]
MACHINE_CYCLE = TELLMESH / "markpact-contracts" / "packs" / "machine-cycle-process.markpact.md"
DESKTOP = TELLMESH / "markpact-contracts" / "packs" / "desktop-automation-processes.markpact.md"


def test_declared_schemes_from_requires():
    pack = {
        "requires": {"schemes": ["stepper", "screen"]},
        "uses": {"packs": ["uristepper"]},
    }
    assert declared_schemes(pack) == {"stepper", "screen"}
    assert declared_packs(pack) == ["uristepper"]


def test_declared_schemes_legacy_flat_uses():
    pack = {"uses": ["stepper", "kvm", "uristepper"]}
    assert declared_schemes(pack) == {"stepper", "kvm"}


def test_lint_rejects_query_kind_mismatch():
    result = lint_markpact(
        pack={"requires": {"schemes": ["kvm"]}},
        scheme="kvm",
        capabilities=[
            {
                "uri": "kvm://local/monitor/primary/query/screenshot",
                "kind": "command",
                "operation": "kvm.monitor.screenshot",
                "side_effects": False,
                "approval": "not_required",
            }
        ],
        flows=[],
        undeclared_schemes=[],
    )
    assert result["ok"] is False
    assert any("/query/" in e for e in result["errors"])


@pytest.mark.skipif(not MACHINE_CYCLE.is_file(), reason="machine-cycle markpact missing")
def test_machine_cycle_analyze_v1alpha_profile():
    analysis = MarkpactManager().analyze(MACHINE_CYCLE)
    assert analysis["ok"] is True
    assert analysis["declared_uses"] == ["screen", "stepper", "tts"]
    profile = analysis["profile"]
    assert profile["profile"] == "markpact-v1alpha"
    assert profile["uses_packs"] == ["uristepper", "uriscreen", "uristt-tts"]
    assert not profile["errors"]


@pytest.mark.skipif(not DESKTOP.is_file(), reason="desktop automation markpact missing")
def test_desktop_automation_analyze_has_expect_warnings_only():
    analysis = MarkpactManager().analyze(DESKTOP)
    assert analysis["ok"] is True
    assert "browser" in analysis["declared_uses"]
    # expect blocks present — no "no expect" warnings
    assert not any("no expect" in w for w in analysis.get("warnings", []))
