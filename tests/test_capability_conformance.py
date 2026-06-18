"""Capability pack analyze conformance matrix (Sprint 6)."""

from __future__ import annotations

from pathlib import Path

import pytest

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
