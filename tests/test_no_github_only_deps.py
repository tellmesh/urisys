"""Guard: tellmesh (GitHub-only) packages must never be in a [real]/[vision] backend extra.

Backend extras must stay pip-resolvable; a tellmesh pack there breaks uv/pip resolution
(regression: urikvm[real] -> uriscreen -> urisys[kvm] unsatisfiable).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from check_no_github_only_deps import dep_name, find_violations

_ROOT = Path(__file__).resolve().parents[2]  # tellmesh workspace root


def _write(tmp_path, name, toml):
    d = tmp_path / name
    d.mkdir()
    (d / "pyproject.toml").write_text(toml, encoding="utf-8")


def test_dep_name_strips_spec():
    assert dep_name('uriscreen>=0.1.0') == "uriscreen"
    assert dep_name('urikvm[real]>=0.1.0 ; sys_platform=="linux"') == "urikvm"
    assert dep_name("mss>=9.0") == "mss"


def test_flags_tellmesh_pack_in_real_extra(tmp_path):
    _write(tmp_path, "urifoo",
           '[project]\nname="urifoo"\n[project.optional-dependencies]\n'
           'real = ["mss>=9.0", "uriscreen>=0.1.0"]\n')
    assert ("urifoo", "real", "uriscreen") in find_violations(tmp_path)


def test_allows_plain_pip_libs_in_real(tmp_path):
    _write(tmp_path, "uribar",
           '[project]\nname="uribar"\n[project.optional-dependencies]\n'
           'real = ["mss>=9.0", "Pillow>=10.0", "pyautogui>=0.9"]\n')
    assert find_violations(tmp_path) == []


def test_ignores_composition_deps_outside_backend_extras(tmp_path):
    # tellmesh packs in dev/kvm composition extras are intentional (resolved via uv.sources)
    _write(tmp_path, "uribaz",
           '[project]\nname="uribaz"\n[project.optional-dependencies]\n'
           'dev = ["urikvm>=0.1.0"]\nkvm = ["urihim>=0.1.0"]\n')
    assert find_violations(tmp_path) == []


def test_monorepo_has_no_violations():
    if not (_ROOT / "urikvm" / "pyproject.toml").exists():
        pytest.skip("sibling tellmesh packs not present")
    violations = find_violations(_ROOT)
    assert violations == [], f"tellmesh packages in backend extras: {violations}"
