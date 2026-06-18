"""analyze --strict and urioperators on TELLMESH_ROOT path."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from urisys.managers.markpact_manager import MarkpactManager

TELLMESH = Path(__file__).resolve().parents[2]
MACHINE_CYCLE = TELLMESH / "markpact-contracts" / "packs" / "machine-cycle-process.markpact.md"


def _analyze_strict(path: Path) -> dict:
    result = MarkpactManager().analyze(path)
    if result.get("warnings"):
        result = {
            **result,
            "ok": False,
            "strict": True,
            "errors": list(result.get("errors") or [])
            + [f"warning: {w}" for w in result.get("warnings") or []],
        }
    return result


@pytest.mark.skipif(not MACHINE_CYCLE.is_file(), reason="machine-cycle markpact missing")
def test_machine_cycle_analyze_strict_passes():
    result = _analyze_strict(MACHINE_CYCLE)
    assert result["ok"] is True, result.get("errors") or result.get("warnings")


@pytest.mark.skipif(not os.environ.get("TELLMESH_ROOT"), reason="needs TELLMESH_ROOT")
def test_extend_tellmesh_includes_urioperators():
    from urisys.managers.markpact_pack_deps import extend_tellmesh_paths

    extend_tellmesh_paths(anchor=TELLMESH / "urisys")
    import urioperators  # noqa: F401
