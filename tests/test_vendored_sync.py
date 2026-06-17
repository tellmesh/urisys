"""Drift guard: vendored packs in urisys vs tellmesh sibling repos."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TELLMESH = ROOT.parent

# F0 existing repos + F1 office packs (after init-repo)
SYNC_PACKS = (
    "urisysedge",
    "urikvm",
    "urihim",
    "uriocr",
    "urillm",
    "urimail",
    "urioffice",
    "urivql",
)


def _run_check(packs: list[str]) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(ROOT / "scripts" / "pack_sync.py"), "check", *packs]
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def test_pack_sync_script_exists():
    assert (ROOT / "scripts" / "pack_sync.py").is_file()
    assert (ROOT / "scripts" / "sync-vendored-pack.sh").is_file()


def test_vendored_kvm_packs_have_pyproject():
    for name in ("urikvm", "urihim", "uriocr", "urillm", "urimail", "urioffice", "urivql"):
        path = ROOT / "urikvm-docker" / "packages" / "python" / name / "pyproject.toml"
        assert path.is_file(), f"missing {path}"


def test_sibling_repos_exist_for_sync_set():
    missing = [p for p in SYNC_PACKS if not (TELLMESH / p).is_dir()]
    assert not missing, f"run: bash scripts/sync-vendored-pack.sh --init {' '.join(missing)}"


def test_no_drift_monorepo_to_tellmesh():
    """Fail CI when vendored code diverges from tellmesh/* canonical repos."""
    proc = _run_check(list(SYNC_PACKS))
    if proc.returncode != 0:
        raise AssertionError(proc.stdout + proc.stderr)
    assert "OK:" in proc.stdout
