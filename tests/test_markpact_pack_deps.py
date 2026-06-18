from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

from urisys.managers.markpact_pack_deps import extend_tellmesh_paths, tellmesh_root

TELLMESH = Path(__file__).resolve().parents[2]


def test_tellmesh_root_from_env(monkeypatch):
    monkeypatch.setenv("TELLMESH_ROOT", str(TELLMESH))
    assert tellmesh_root() == TELLMESH


def test_extend_tellmesh_paths_adds_siblings(monkeypatch):
    monkeypatch.setenv("TELLMESH_ROOT", str(TELLMESH))
    for mod in ("urikvm", "urishell", "urienv"):
        sys.modules.pop(mod, None)
    extend_tellmesh_paths(anchor=TELLMESH / "urisys")
    importlib.import_module("urikvm")
    importlib.import_module("urienv")


def test_extend_tellmesh_imports_uribrowserdocker(monkeypatch):
    monkeypatch.setenv("TELLMESH_ROOT", str(TELLMESH))
    sys.modules.pop("uribrowserdocker", None)
    extend_tellmesh_paths(anchor=TELLMESH / "urisys")
    importlib.import_module("uribrowserdocker")
