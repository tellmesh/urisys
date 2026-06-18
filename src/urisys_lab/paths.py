"""Filesystem anchors for urisys lab runners (tellmesh monorepo layout)."""

from __future__ import annotations

from pathlib import Path

URISYS_ROOT = Path(__file__).resolve().parents[2]
TELLMESH_ROOT = URISYS_ROOT.parent
NODE_ROOT = TELLMESH_ROOT / "urisys-node"
REPORT_SCRIPT = URISYS_ROOT / "scripts" / "session_report.py"
