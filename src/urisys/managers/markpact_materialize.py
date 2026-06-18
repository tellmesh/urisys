"""Materialize compiled Markpact artifacts to a stable ``.markpact/{id}/`` tree."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .markpact_manager import MarkpactManager
from ..markpact.models import CompiledMarkpact, safe_identifier


def default_materialize_root() -> Path:
    return Path(".markpact")


def materialize_markpact(
    path: str | Path,
    *,
    root: str | Path | None = None,
    manager: MarkpactManager | None = None,
    force: bool = False,
    platforms: list[str] | tuple[str, ...] | None = None,
    export_platforms: bool = True,
) -> dict[str, Any]:
    """Compile *path* and copy cache output to ``.markpact/{package_id}/``."""
    mgr = manager or MarkpactManager()
    compiled = mgr.compile(path, force=force)
    base = Path(root) if root is not None else default_materialize_root()
    dest = base / safe_identifier(compiled.package_id)
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    for item in compiled.cache_dir.iterdir():
        target = dest / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, dest / item.name)
    index = {
        "package_id": compiled.package_id,
        "source_path": str(compiled.source_path),
        "source_hash": compiled.source_hash,
        "materialized_dir": str(dest.resolve()),
        "manifest_path": str((dest / "manifest.yaml").resolve()),
        "flow_ids": list(compiled.flow_ids),
    }
    (dest / "materialize.json").write_text(json.dumps(index, indent=2), encoding="utf-8")

    platform_index = None
    if export_platforms and compiled.flow_ids:
        from ..markpact.platform_export import export_platform_artifacts

        platform_index = export_platform_artifacts(
            path,
            out_dir=dest / "generated",
            platforms=platforms,
            materialized_dir=dest,
        )
    return {
        "ok": True,
        "materialized": index,
        "platform_export": platform_index,
        "compiled": compiled.to_dict(),
    }


__all__ = ["default_materialize_root", "materialize_markpact"]
