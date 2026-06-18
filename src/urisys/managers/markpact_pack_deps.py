"""Resolve optional flow pack dependencies for ``markpact run-flow``."""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

from uri_control.edge.compose import resolve_pack_module

from .markpact_models import MarkpactError


def tellmesh_root(*, anchor: Path | None = None) -> Path | None:
    env = os.environ.get("TELLMESH_ROOT", "").strip()
    if env:
        root = Path(env)
        if root.is_dir():
            return root
    start = (anchor or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "urisys").is_dir() and (candidate / "uricore").is_dir():
            return candidate
    return None


def _is_capability_pack_repo(child: Path) -> bool:
    name = child.name
    if (child / name / "manifest.yaml").is_file():
        return True
    if (child / "manifest.yaml").is_file() and (child / "routes.py").is_file():
        return True
    return False


def _register_flat_pack(root: Path, name: str) -> bool:
    """Import a flat-layout pack (``package-dir = {{name = \".\"}}``) from source."""
    init = root / "__init__.py"
    if not init.is_file():
        return False
    spec = importlib.util.spec_from_file_location(name, init, submodule_search_locations=[str(root)])
    if spec is None or spec.loader is None:
        return False
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return True


def _is_flat_pack_repo(child: Path) -> bool:
    """Repo root is the importable package (``package-dir = {{name = \".\"}}``)."""
    name = child.name
    return (
        (child / "manifest.yaml").is_file()
        and (child / "__init__.py").is_file()
        and not (child / name / "manifest.yaml").is_file()
    )


def _discover_pack_modules(child: Path) -> list[tuple[Path, str]]:
    """Return ``(repo_root_on_sys_path, import_module_name)`` for packs under *child*."""
    found: list[tuple[Path, str]] = []
    name = child.name
    nested = child / name
    if nested.is_dir() and (nested / "manifest.yaml").is_file():
        found.append((child, name))
    for sub in sorted(child.iterdir()):
        if not sub.is_dir():
            continue
        if (sub / "manifest.yaml").is_file() and ((sub / "routes.py").is_file() or (sub / "__init__.py").is_file()):
            found.append((child, sub.name))
    if (child / "manifest.yaml").is_file() and (child / "routes.py").is_file():
        if not any(mod == name for _, mod in found):
            found.append((child, name))
    return found


def _register_existing_pack(repo_path: Path, module_name: str, added: list[str], seen_paths: set[str]) -> None:
    path = str(repo_path.resolve())
    if path not in sys.path and path not in seen_paths:
        sys.path.insert(0, path)
        seen_paths.add(path)
        added.append(path)
    if module_name in sys.modules:
        return
    try:
        importlib.import_module(module_name)
    except ModuleNotFoundError:
        if _register_flat_pack(repo_path / module_name, module_name):
            added.append(f"flat:{repo_path / module_name}")


def _register_sibling_packs(root: Path, added: list[str], seen_paths: set[str]) -> None:
    for child in sorted(root.iterdir()):
        if not child.is_dir() or not child.name.startswith("uri"):
            continue
        if child.name.endswith("-docker") or child.name.endswith("edge"):
            continue
        if not _is_capability_pack_repo(child) and not _discover_pack_modules(child):
            continue
        if _is_flat_pack_repo(child):
            if child.name not in sys.modules and _register_flat_pack(child, child.name):
                added.append(f"flat:{child}")
            continue
        for repo_path, module_name in _discover_pack_modules(child):
            _register_existing_pack(repo_path, module_name, added, seen_paths)


def _register_uricore_utils(root: Path, added: list[str]) -> None:
    uricore = root / "uricore" / "core" / "python"
    if uricore.is_dir():
        path = str(uricore.resolve())
        if path not in sys.path:
            sys.path.insert(0, path)
            added.append(path)


def _register_urioperators(root: Path, added: list[str]) -> None:
    ops = root / "urioperators"
    if ops.is_dir() and (ops / "__init__.py").is_file():
        path = str(ops.resolve())
        if path not in sys.path:
            sys.path.insert(0, path)
            added.append(path)
        if "urioperators" not in sys.modules:
            try:
                importlib.import_module("urioperators")
            except ModuleNotFoundError:
                pass


def extend_tellmesh_paths(*, anchor: Path | None = None) -> list[str]:
    """Register sibling tellmesh capability packs (nested path or flat import)."""
    root = tellmesh_root(anchor=anchor)
    if root is None:
        return []
    added: list[str] = []
    seen_paths: set[str] = set()
    _register_sibling_packs(root, added, seen_paths)
    _register_uricore_utils(root, added)
    _register_urioperators(root, added)
    return added


def _pack_resolver():
    try:
        from urisysnode import pack_resolver

        return pack_resolver
    except ModuleNotFoundError:
        return None


def ensure_pack_importable(pack: str, *, auto_install: bool = False) -> dict[str, Any]:
    """Return ``{ok, pack, module}``; optionally pip-install via urisys-node resolver."""
    module_name = resolve_pack_module(pack)
    try:
        importlib.import_module(module_name)
        return {"ok": True, "pack": pack, "module": module_name}
    except ModuleNotFoundError as first_exc:
        resolver = _pack_resolver()
        if auto_install and resolver is not None:
            install = resolver.ensure_pack_pypi(pack, install=True)
            if install.get("ok"):
                importlib.import_module(module_name)
                return {"ok": True, "pack": pack, "module": module_name, "installed": install}
        raise MarkpactError(
            f"Pack {pack!r} (module {module_name!r}) is not importable: {first_exc}. "
            "Set TELLMESH_ROOT, extend PYTHONPATH, or pass --auto-install."
        ) from first_exc


def ensure_flow_packs(
    packs: list[str],
    *,
    anchor: Path | None = None,
    auto_install: bool = False,
) -> dict[str, Any]:
    extend_tellmesh_paths(anchor=anchor)
    reports: list[dict[str, Any]] = []
    for pack in packs:
        reports.append(ensure_pack_importable(pack, auto_install=auto_install))
    return {"ok": True, "packs": packs, "reports": reports}


__all__ = ["tellmesh_root", "extend_tellmesh_paths", "ensure_flow_packs", "ensure_pack_importable"]
