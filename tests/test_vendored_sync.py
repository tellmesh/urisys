"""Drift guard: capability packs live in tellmesh sibling repos (not vendored in urisys)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TELLMESH = ROOT.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from pack_registry import all_promoted_packs, pack_specs, sibling_repo_names  # noqa: E402

PROMOTED_PACKS = tuple(sorted(all_promoted_packs()))
SIBLING_REPOS = tuple(sorted(sibling_repo_names()))


def _run_check(packs: list[str]) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPTS / "pack_sync.py"), "check", *packs]
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def test_pack_sync_script_exists():
    assert (SCRIPTS / "pack_sync.py").is_file()
    assert (SCRIPTS / "pack_registry.py").is_file()
    assert (ROOT / "scripts" / "sync-vendored-pack.sh").is_file()


def test_sibling_repos_exist():
    missing = [r for r in SIBLING_REPOS if not (TELLMESH / r).is_dir()]
    assert not missing, f"missing tellmesh repos: {missing}"


def test_promoted_packs_not_vendored_in_monorepo():
    specs = pack_specs()
    still_vendored = []
    for name in PROMOTED_PACKS:
        spec = specs[name]
        if spec.vendored is not None and spec.vendored.is_dir():
            still_vendored.append(str(spec.vendored))
    assert not still_vendored, f"run: python3 scripts/pack_sync.py promote --all\n{still_vendored}"


def test_sibling_repos_have_pyproject():
    for repo in SIBLING_REPOS:
        path = TELLMESH / repo / "pyproject.toml"
        assert path.is_file(), f"missing {path}"


def test_no_drift_promoted_packs():
    """Sibling repos must exist and vendored copies must be gone."""
    proc = _run_check(list(PROMOTED_PACKS))
    if proc.returncode != 0:
        raise AssertionError(proc.stdout + proc.stderr)
    assert "OK:" in proc.stdout
