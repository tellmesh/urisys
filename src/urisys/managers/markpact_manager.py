from __future__ import annotations

from pathlib import Path
from typing import Any

from ..markpact.models import (
    CompiledMarkpact,
    MarkpactBlock,
    MarkpactError,
    source_hash as _source_hash,
)
from ..markpact.analyzer import analyze_markpact
from ..markpact.blocks import read_blocks as _read_blocks
from ..markpact.compiler import MarkpactCompiler
from ..markpact.pack import load_pack_block as _load_pack_block
from ..markpact.tests import run_tests_for_path
from ..markpact.validate_pack import validate_markpact_file

# Re-exported for backward compatibility (e.g. urisys.cli imports MarkpactError).
__all__ = ["MarkpactManager", "MarkpactBlock", "CompiledMarkpact", "MarkpactError"]


class MarkpactManager:
    """Facade over :mod:`urisys.markpact` compile/analyze pipeline.

    Markpact is an authoring/distribution format. Runtime uses a cached,
    generated manifest and extracted handler modules for speed and safety.
    """

    def __init__(self, cache_root: str | Path = ".urisys/cache/markpacts") -> None:
        self.cache_root = Path(cache_root)
        self._compiler = MarkpactCompiler(self.cache_root)

    def read_blocks(self, path: str | Path) -> list[MarkpactBlock]:
        return _read_blocks(path)

    def source_hash(self, path: str | Path) -> str:
        return _source_hash(path)

    def load_pack_block(self, path: str | Path) -> dict[str, Any]:
        return _load_pack_block(path)

    def validate(self, path: str | Path) -> dict[str, Any]:
        return validate_markpact_file(path)

    def compile(self, path: str | Path, *, out_dir: str | Path | None = None, force: bool = False) -> CompiledMarkpact:
        return self._compiler.compile(path, out_dir=out_dir, force=force, validate=self.validate)

    def analyze(self, path: str | Path) -> dict[str, Any]:
        return analyze_markpact(path)

    def manifest_path_for(self, path: str | Path) -> Path:
        return self.compile(path).manifest_path

    def run_tests(self, path: str | Path, *, events_path: str | Path | None = None) -> dict[str, Any]:
        return run_tests_for_path(
            path,
            cache_root=self.cache_root,
            events_path=events_path,
            validate=self.validate,
        )

    # Backward-compatible hooks for tests and internal callers.
    def _build_route(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        from ..markpact.manifest import build_route

        return build_route(*args, **kwargs)

    def _compile_manifest(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        from ..markpact.manifest import compile_manifest

        return compile_manifest(*args, **kwargs)
