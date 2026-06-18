"""Pytest hooks for markpact test isolation.

Also puts sibling tellmesh packages on ``sys.path`` (uriresolver, uricontrol).
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

# tellmesh monorepo: module import name → path under TELLMESH_ROOT
_SIBLING_ROOTS: tuple[tuple[str, str], ...] = (
    ("uri_resolver", "uriresolver/src"),
    ("uri_control", "uricontrol/core/python"),
)


def _tellmesh_root() -> Path | None:
    env = os.environ.get("TELLMESH_ROOT", "").strip()
    if env and Path(env).is_dir():
        return Path(env)
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "urisys").is_dir() and (candidate / "uricontrol").is_dir():
            return candidate
    return None


def _module_available(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except (ModuleNotFoundError, ValueError, ImportError):
        return False


def _ensure_siblings() -> None:
    root = _tellmesh_root()
    if root is None:
        return
    for module_name, rel in _SIBLING_ROOTS:
        sibling = root / rel
        if not sibling.is_dir():
            continue
        if _module_available(module_name):
            continue
        path = str(sibling.resolve())
        if path not in sys.path:
            sys.path.insert(0, path)


_ensure_siblings()

from pack_import_isolation import reset_embedded_pack_imports


@pytest.fixture(autouse=True)
def _cleanup_markpact_embedded_imports():
    yield
    reset_embedded_pack_imports()
