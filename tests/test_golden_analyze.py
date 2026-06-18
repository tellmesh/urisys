"""Golden snapshots for ``analyze_markpact`` on reference contracts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from urisys.markpact.analyzer import analyze_markpact

TELLMESH = Path(__file__).resolve().parents[2]
PACKS = TELLMESH / "markpact-contracts" / "packs"
GOLDEN = Path(__file__).resolve().parent / "golden"

_GOLDEN_CASES = (
    ("machine-cycle-process.markpact.md", "machine-cycle-process.analyze.json"),
    ("desktop-automation-processes.markpact.md", "desktop-automation-processes.analyze.json"),
    ("uristepper.markpact.md", "uristepper.analyze.json"),
)


def _analyze_snapshot(path: Path) -> dict[str, Any]:
    result = analyze_markpact(path)
    snapshot: dict[str, Any] = {
        "package_id": result["package_id"],
        "scheme": result["scheme"],
        "ok": result["ok"],
        "capabilities": result["capabilities"],
        "flow_count": len(result["flows"]),
        "issue_codes": sorted({i["code"] for i in result["profile"]["issues"]}),
        "error_count": len(result["errors"]),
        "warning_count": len(result["warnings"]),
    }
    if result["scheme"] == "process":
        snapshot["use_cases"] = result["use_cases"]
        snapshot["integrations"] = result["integrations"]
        snapshot["undeclared_uses"] = result["undeclared_uses"]
    return snapshot


@pytest.mark.parametrize("markpact_name,golden_name", _GOLDEN_CASES)
def test_analyze_golden_snapshot(markpact_name: str, golden_name: str):
    markpact_path = PACKS / markpact_name
    golden_path = GOLDEN / golden_name
    if not markpact_path.is_file():
        pytest.skip(f"missing contract: {markpact_path}")
    expected = json.loads(golden_path.read_text(encoding="utf-8"))
    assert _analyze_snapshot(markpact_path) == expected
