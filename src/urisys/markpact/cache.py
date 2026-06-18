"""Compile cache paths and metadata."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

from ..managers.markpact_models import CompiledMarkpact, MarkpactBlock, safe_identifier, source_hash
from .artifacts import flows_from_cache, modules_from_cache, protos_from_cache
from .blocks import read_blocks
from .pack import load_pack_block, package_id


def compile_context(
    path: str | Path,
    *,
    cache_root: Path,
    out_dir: str | Path | None = None,
) -> dict[str, Any]:
    source_path = Path(path)
    blocks = read_blocks(source_path)
    pack = load_pack_block(source_path)
    digest = source_hash(source_path)
    pkg_id = package_id(pack, source_path)
    safe_package_id = safe_identifier(pkg_id)
    module_name = f"urisys_markpact_{safe_package_id}_{digest[:10]}"
    root = Path(out_dir) if out_dir else cache_root
    cache_dir = root / safe_package_id / digest[:16]
    return {
        "source_path": source_path,
        "blocks": blocks,
        "pack": pack,
        "digest": digest,
        "package_id": pkg_id,
        "module_name": module_name,
        "cache_dir": cache_dir,
        "package_dir": cache_dir / module_name,
        "manifest_path": cache_dir / "manifest.yaml",
        "tests_path": cache_dir / "tests.yaml",
        "docs_path": cache_dir / "README.generated.md",
        "metadata_path": cache_dir / "markpact.json",
    }


def compiled_from_cache(ctx: dict[str, Any], blocks: list[MarkpactBlock]) -> CompiledMarkpact:
    ensure_importable(ctx["cache_dir"])
    flows_dir, flow_ids = flows_from_cache(ctx["cache_dir"], blocks)
    proto_dir, proto_files = protos_from_cache(ctx["cache_dir"], blocks)
    module_files = modules_from_cache(ctx["cache_dir"], blocks)
    tests_path = ctx["tests_path"] if ctx["tests_path"].exists() else None
    docs_path = ctx["docs_path"] if ctx["docs_path"].exists() else None
    metadata_path = ctx["metadata_path"] if ctx["metadata_path"].exists() else None
    return CompiledMarkpact(
        source_path=ctx["source_path"],
        source_hash=ctx["digest"],
        cache_dir=ctx["cache_dir"],
        package_id=ctx["package_id"],
        module_name=ctx["module_name"],
        manifest_path=ctx["manifest_path"],
        tests_path=tests_path,
        docs_path=docs_path,
        metadata_path=metadata_path,
        flows_dir=flows_dir,
        flow_ids=flow_ids,
        proto_dir=proto_dir,
        proto_files=proto_files,
        module_files=module_files,
    )


def write_manifest_flows(manifest_path: Path, flows_dir: Path, flow_ids: list[str]) -> None:
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    manifest["urisys"] = {
        "flows_dir": str(flows_dir.resolve()),
        "flows": {
            fid: str((flows_dir / f"{safe_identifier(fid, fallback='flow')}.uri.flow.yaml").resolve())
            for fid in flow_ids
        },
    }
    manifest_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def write_compile_metadata(ctx: dict[str, Any]) -> None:
    metadata = {
        "kind": "CompiledUriPackMarkpact",
        "source_path": str(ctx["source_path"]),
        "source_hash": ctx["digest"],
        "package_id": ctx["package_id"],
        "module_name": ctx["module_name"],
        "manifest_path": str(ctx["manifest_path"]),
    }
    ctx["metadata_path"].write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (ctx["cache_dir"] / "source.markpact.md").write_text(
        ctx["source_path"].read_text(encoding="utf-8"),
        encoding="utf-8",
    )


def ensure_importable(cache_dir: Path) -> None:
    value = str(cache_dir.resolve())
    if value not in sys.path:
        sys.path.insert(0, value)


__all__ = [
    "compile_context",
    "compiled_from_cache",
    "ensure_importable",
    "write_compile_metadata",
    "write_manifest_flows",
]
