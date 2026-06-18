"""Resolver stub lint (RR codes) for process Markpacts."""

from __future__ import annotations

from pathlib import Path

import pytest

from urisys.markpact.analyzer import analyze_markpact
from urisys.markpact.analyzer.resolver_lint import lint_process_resolver_stubs

TELLMESH = Path(__file__).resolve().parents[2]
PACKS = TELLMESH / "markpact-contracts" / "packs"


def test_lint_process_resolver_stubs_ok():
    path = PACKS / "machine-cycle-process.markpact.md"
    if not path.is_file():
        pytest.skip(f"missing contract: {path}")
    result = lint_process_resolver_stubs(path)
    assert result.get("skipped") is not True
    assert result["ok"] is True
    assert result["issue_codes"] == []


def test_analyze_includes_resolver_for_process_pack():
    path = PACKS / "machine-cycle-process.markpact.md"
    if not path.is_file():
        pytest.skip(f"missing contract: {path}")
    result = analyze_markpact(path)
    assert result["scheme"] == "process"
    assert result["resolver"] is not None
    assert result["resolver"]["ok"] is True


def test_analyze_skips_resolver_for_capability_pack():
    path = PACKS / "uristepper.markpact.md"
    if not path.is_file():
        pytest.skip(f"missing contract: {path}")
    result = analyze_markpact(path)
    assert result["resolver"] is None
