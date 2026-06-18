"""Capability pack analyze + dry-run conformance matrix (Sprint 6 / 13)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from urisys.managers.markpact_manager import MarkpactManager
from urisys.managers.markpact_run import run_markpact
from urisys.markpact.analyzer import analyze_markpact

TELLMESH = Path(__file__).resolve().parents[2]
PACKS = TELLMESH / "markpact-contracts" / "packs"

# scheme, minimum capabilities, must have zero analyze errors
CAPABILITY_MATRIX = [
    ("uristepper.markpact.md", "stepper", 5),
    ("urikvm.markpact.md", "kvm", 3),
    ("urihim.markpact.md", "him", 2),
    ("uriocr.markpact.md", "ocr", 2),
    ("urillm.markpact.md", "llm", 2),
    ("urishell.markpact.md", "shell", 1),
    ("uriscreen.markpact.md", "screen", 2),
    ("urienv.markpact.md", "env", 1),
    ("urirdp.markpact.md", "rdp", 2),
    ("uribrowser.markpact.md", "browser", 2),
]

# Embedded smoke flows (`markpact:flow`) — dry-run via `run_markpact --as flow`.
CAPABILITY_DRY_RUN_FLOWS = [
    ("uristepper.markpact.md", "stepper-smoke"),
    ("urikvm.markpact.md", "kvm-smoke"),
    ("urihim.markpact.md", "him-smoke"),
    ("uriocr.markpact.md", "ocr-smoke"),
    ("urillm.markpact.md", "llm-smoke"),
    ("urishell.markpact.md", "shell-smoke"),
    ("uriscreen.markpact.md", "screen-smoke"),
    ("urienv.markpact.md", "env-smoke"),
    ("urirdp.markpact.md", "rdp-smoke"),
]

# Packs without `markpact:flow` — dry-run via embedded `markpact:tests`.
CAPABILITY_DRY_RUN_TESTS = [
    "uribrowser.markpact.md",
]


@pytest.mark.parametrize("markpact_file,expected_scheme,min_caps", CAPABILITY_MATRIX)
def test_capability_pack_analyze_conformance(markpact_file: str, expected_scheme: str, min_caps: int):
    path = PACKS / markpact_file
    if not path.is_file():
        pytest.skip(f"missing pack contract: {markpact_file}")

    result = analyze_markpact(path)
    assert result["scheme"] == expected_scheme, result
    assert result["capabilities"] >= min_caps, result
    assert result["ok"] is True, result.get("errors") or result.get("warnings")
    assert not result["errors"], result["errors"]


@pytest.mark.parametrize("markpact_file,flow_id", CAPABILITY_DRY_RUN_FLOWS)
@pytest.mark.skipif(not os.environ.get("TELLMESH_ROOT"), reason="needs TELLMESH_ROOT")
def test_capability_pack_flow_dry_run_conformance(
    markpact_file: str,
    flow_id: str,
    tmp_path,
    monkeypatch,
):
    path = PACKS / markpact_file
    if not path.is_file():
        pytest.skip(f"missing pack contract: {markpact_file}")

    monkeypatch.setenv("TELLMESH_ROOT", os.environ["TELLMESH_ROOT"])
    result = run_markpact(
        path,
        mode="flow",
        flow_id=flow_id,
        approve=True,
        dry_run=True,
        out=tmp_path / f"{flow_id}-out",
    )
    assert result["ok"] is True, result


@pytest.mark.parametrize("markpact_file", CAPABILITY_DRY_RUN_TESTS)
@pytest.mark.skipif(not os.environ.get("TELLMESH_ROOT"), reason="needs TELLMESH_ROOT")
def test_capability_pack_embedded_tests_conformance(
    markpact_file: str,
    tmp_path,
    monkeypatch,
):
    path = PACKS / markpact_file
    if not path.is_file():
        pytest.skip(f"missing pack contract: {markpact_file}")

    monkeypatch.setenv("TELLMESH_ROOT", os.environ["TELLMESH_ROOT"])
    result = MarkpactManager(cache_root=tmp_path / ".markpact").run_tests(path)
    assert result["ok"] is True, result
