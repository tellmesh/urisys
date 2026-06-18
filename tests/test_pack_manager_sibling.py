from __future__ import annotations

import os
from pathlib import Path

import pytest

from urisys.managers.pack_manager import PackManager, _sibling_manifest_path

TELLMESH = Path(__file__).resolve().parents[2]


@pytest.mark.skipif(not (TELLMESH / "urikvm").is_dir(), reason="tellmesh urikvm missing")
def test_sibling_manifest_path_finds_nested_pack(monkeypatch):
    monkeypatch.setenv("TELLMESH_ROOT", str(TELLMESH))
    path = _sibling_manifest_path("urikvm")
    assert path is not None
    assert path.name == "manifest.yaml"
    assert path.parent.name == "urikvm"


@pytest.mark.skipif(not (TELLMESH / "uribrowser").is_dir(), reason="tellmesh uribrowser missing")
def test_sibling_manifest_path_finds_browser_docker(monkeypatch):
    monkeypatch.setenv("TELLMESH_ROOT", str(TELLMESH))
    path = _sibling_manifest_path("uribrowserdocker")
    assert path is not None
    assert "uribrowserdocker" in str(path)


def test_pack_manager_all_loads_sibling_manifests(monkeypatch):
    monkeypatch.setenv("TELLMESH_ROOT", str(TELLMESH))
    if not (TELLMESH / "urishell").is_dir():
        pytest.skip("tellmesh siblings missing")
    with PackManager(packs="shell") as pm:
        paths = pm.manifest_paths()
    assert len(paths) == 1
    assert paths[0].name == "manifest.yaml"
    assert "urishell" in str(paths[0])
