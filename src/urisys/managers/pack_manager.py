from __future__ import annotations

import warnings
from contextlib import ExitStack
from importlib import import_module
from importlib.resources import as_file, files
from pathlib import Path
from typing import Iterable

import yaml
from uri_control import CapabilityRegistry

from ..defaults import DEFAULT_PACKAGES
from .markpact_manager import MarkpactManager
from .markpact_pack_deps import extend_tellmesh_paths, tellmesh_root
from .source_manager import SourceManager


def _repo_for_package(package_name: str, root: Path) -> Path:
    if package_name in ("uribrowserdocker", "uribrowseredge"):
        return root / "uribrowser"
    return root / package_name


def _sibling_manifest_path(package_name: str) -> Path | None:
    root = tellmesh_root()
    if root is None:
        return None
    repo = _repo_for_package(package_name, root)
    if not repo.is_dir():
        return None
    candidates = [
        repo / package_name / "manifest.yaml",
        repo / package_name / package_name / "manifest.yaml",
        repo / "manifest.yaml",
    ]
    for path in candidates:
        if path.is_file():
            return path
    for path in sorted(repo.glob("*/manifest.yaml")):
        if path.is_file() and path.parent.name == package_name:
            return path
    return None


def _manifest_is_loadable(path: Path) -> bool:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except OSError:
        return False
    if not isinstance(data, dict):
        return False
    return bool(str(data.get("scheme") or "").strip())


class PackManager:
    """Loads separate uri* packages, plain manifest.yaml files and UriPack Markpacts."""

    def __init__(self, packs: Iterable[str] | str | None = None, *, markpacts: Iterable[str] | str | None = None) -> None:
        self.expanded_all = self._is_all(packs)
        self.pack_specs = self.parse_packs(packs)
        self.markpact_specs = self.parse_markpacts(markpacts)
        self._stack = ExitStack()
        self._manifest_paths: list[Path] = []
        self.markpact_manager = MarkpactManager()
        self.source_manager = SourceManager()

    @staticmethod
    def _split_specs(value: Iterable[str] | str | None) -> list[str]:
        """Normalize a comma string or iterable into a clean list of specs."""
        if value is None or value == "":
            return []
        items = value.split(",") if isinstance(value, str) else value
        return [str(p).strip() for p in items if str(p).strip()]

    @staticmethod
    def _is_all(packs: Iterable[str] | str | None) -> bool:
        """True when the default ('all') package set is requested, so missing
        optional uri* packages are skipped with a warning instead of crashing."""
        if packs is None or packs == "" or packs == "all":
            return True
        return "all" in PackManager._split_specs(packs)

    @staticmethod
    def parse_packs(packs: Iterable[str] | str | None) -> list[str]:
        if packs is None or packs == "" or packs == "all":
            return list(DEFAULT_PACKAGES)
        parts = PackManager._split_specs(packs)
        if "all" in parts:
            return list(DEFAULT_PACKAGES)
        if "none" in parts:
            return [p for p in parts if p != "none"]
        return parts

    @staticmethod
    def parse_markpacts(markpacts: Iterable[str] | str | None) -> list[str]:
        return PackManager._split_specs(markpacts)

    def resolve_package_name(self, spec: str) -> str:
        return DEFAULT_PACKAGES.get(spec, spec)

    def _is_markpact_path(self, spec: str) -> bool:
        if spec.endswith(".markpact.md") or spec.endswith(".markpact"):
            return True
        return self.source_manager.is_remote_source(spec)

    def _is_manifest_path(self, spec: str) -> bool:
        return spec.endswith(".yaml") or spec.endswith(".yml") or "/" in spec or "\\" in spec

    def manifest_paths(self) -> list[Path]:
        if self._manifest_paths:
            return self._manifest_paths
        extend_tellmesh_paths()
        paths: list[Path] = []
        for spec in self.pack_specs:
            if self._is_markpact_path(spec):
                local = self.source_manager.resolve(spec)
                paths.append(self.markpact_manager.manifest_path_for(local))
                continue
            if self._is_manifest_path(spec):
                paths.append(Path(spec))
                continue
            package_name = self.resolve_package_name(spec)
            manifest_path: Path | None = None
            try:
                import_module(package_name)
            except ModuleNotFoundError as exc:
                if exc.name != package_name:
                    raise
            else:
                manifest = files(package_name).joinpath("manifest.yaml")
                if manifest.is_file():
                    manifest_path = Path(self._stack.enter_context(as_file(manifest)))

            if manifest_path is None:
                manifest_path = _sibling_manifest_path(package_name)

            if manifest_path is not None and not _manifest_is_loadable(manifest_path):
                if self.expanded_all:
                    warnings.warn(
                        f"Skipping uri pack '{spec}': manifest {manifest_path} "
                        f"has no single scheme (multi-scheme bundles need split manifests).",
                        stacklevel=2,
                    )
                    continue
                raise ModuleNotFoundError(
                    f"uri pack '{spec}' manifest {manifest_path} is not loadable "
                    f"(expected a single scheme: field)."
                )

            if manifest_path is None:
                if self.expanded_all:
                    warnings.warn(
                        f"Skipping uri pack '{spec}': package '{package_name}' "
                        f"is not installed and no sibling manifest was found "
                        f"(pip install {package_name} or set TELLMESH_ROOT).",
                        stacklevel=2,
                    )
                    continue
                raise ModuleNotFoundError(
                    f"uri pack '{spec}' requires package '{package_name}' with manifest.yaml, "
                    f"but none was found (pip install {package_name} or set TELLMESH_ROOT)."
                )
            paths.append(manifest_path)
        for spec in self.markpact_specs:
            local = self.source_manager.resolve(spec)
            paths.append(self.markpact_manager.manifest_path_for(local))
        self._manifest_paths = paths
        return paths

    def create_registry(self) -> CapabilityRegistry:
        return CapabilityRegistry.from_manifest_files(self.manifest_paths())

    def capabilities(self) -> list[dict]:
        registry = self.create_registry()
        return [manifest.raw for manifest in registry.manifests]

    def close(self) -> None:
        self._stack.close()

    def __enter__(self) -> "PackManager":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
