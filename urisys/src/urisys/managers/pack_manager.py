from __future__ import annotations

from contextlib import ExitStack
from importlib import import_module
from importlib.resources import as_file, files
from pathlib import Path
from typing import Iterable

from uri_control import CapabilityRegistry

from ..defaults import DEFAULT_PACKAGES
from .markpact_manager import MarkpactManager


class PackManager:
    """Loads separate uri* packages, plain manifest.yaml files and UriPack Markpacts."""

    def __init__(self, packs: Iterable[str] | str | None = None, *, markpacts: Iterable[str] | str | None = None) -> None:
        self.pack_specs = self.parse_packs(packs)
        self.markpact_specs = self.parse_markpacts(markpacts)
        self._stack = ExitStack()
        self._manifest_paths: list[Path] = []
        self.markpact_manager = MarkpactManager()

    @staticmethod
    def parse_packs(packs: Iterable[str] | str | None) -> list[str]:
        if packs is None or packs == "" or packs == "all":
            return list(DEFAULT_PACKAGES)
        if isinstance(packs, str):
            parts = [p.strip() for p in packs.split(",") if p.strip()]
        else:
            parts = [str(p).strip() for p in packs if str(p).strip()]
        if any(p == "all" for p in parts):
            return list(DEFAULT_PACKAGES)
        if any(p == "none" for p in parts):
            return [p for p in parts if p != "none"]
        return parts

    @staticmethod
    def parse_markpacts(markpacts: Iterable[str] | str | None) -> list[str]:
        if markpacts is None or markpacts == "":
            return []
        if isinstance(markpacts, str):
            return [p.strip() for p in markpacts.split(",") if p.strip()]
        return [str(p).strip() for p in markpacts if str(p).strip()]

    def resolve_package_name(self, spec: str) -> str:
        return DEFAULT_PACKAGES.get(spec, spec)

    def _is_markpact_path(self, spec: str) -> bool:
        return spec.endswith(".markpact.md") or spec.endswith(".markpact")

    def _is_manifest_path(self, spec: str) -> bool:
        return spec.endswith(".yaml") or spec.endswith(".yml") or "/" in spec or "\\" in spec

    def manifest_paths(self) -> list[Path]:
        if self._manifest_paths:
            return self._manifest_paths
        paths: list[Path] = []
        for spec in self.pack_specs:
            if self._is_markpact_path(spec):
                paths.append(self.markpact_manager.manifest_path_for(spec))
                continue
            if self._is_manifest_path(spec):
                paths.append(Path(spec))
                continue
            package_name = self.resolve_package_name(spec)
            import_module(package_name)
            manifest = files(package_name).joinpath("manifest.yaml")
            path = self._stack.enter_context(as_file(manifest))
            paths.append(Path(path))
        for spec in self.markpact_specs:
            paths.append(self.markpact_manager.manifest_path_for(spec))
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
