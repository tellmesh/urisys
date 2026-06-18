"""Write/read embedded flows, protos, and module trees."""

from __future__ import annotations

from pathlib import Path

from ..managers.markpact_models import MarkpactBlock, safe_identifier
from ..managers.markpact_flows import extract_flows, extract_modules, extract_protos


def write_modules(cache_dir: Path, blocks: list[MarkpactBlock]) -> tuple[str, ...]:
    modules = extract_modules(blocks)
    written: list[str] = []
    for rel, content in modules:
        target = cache_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(rel)
    return tuple(written)


def flows_from_cache(cache_dir: Path, blocks: list[MarkpactBlock]) -> tuple[Path | None, tuple[str, ...]]:
    flows_dir = cache_dir / "flows"
    if not flows_dir.is_dir():
        return None, ()
    flows = extract_flows(blocks)
    return flows_dir, tuple(f["id"] for f in flows)


def protos_from_cache(cache_dir: Path, blocks: list[MarkpactBlock]) -> tuple[Path | None, tuple[str, ...]]:
    proto_dir = cache_dir / "proto"
    if not proto_dir.is_dir():
        return None, ()
    return proto_dir, tuple(name for name, _ in extract_protos(blocks))


def modules_from_cache(cache_dir: Path, blocks: list[MarkpactBlock]) -> tuple[str, ...]:
    modules = extract_modules(blocks)
    if not modules:
        return ()
    return tuple(rel for rel, _ in modules if (cache_dir / rel).is_file())


def write_flows(cache_dir: Path, blocks: list[MarkpactBlock]) -> tuple[Path | None, tuple[str, ...]]:
    flows = extract_flows(blocks)
    if not flows:
        return None, ()
    flows_dir = cache_dir / "flows"
    flows_dir.mkdir(parents=True, exist_ok=True)
    ids: list[str] = []
    for flow in flows:
        fid = safe_identifier(flow["id"], fallback="flow")
        (flows_dir / f"{fid}.uri.flow.yaml").write_text(flow["raw"], encoding="utf-8")
        ids.append(flow["id"])
    return flows_dir, tuple(ids)


def write_protos(cache_dir: Path, blocks: list[MarkpactBlock]) -> tuple[Path | None, tuple[str, ...]]:
    protos = extract_protos(blocks)
    if not protos:
        return None, ()
    proto_dir = cache_dir / "proto"
    proto_dir.mkdir(parents=True, exist_ok=True)
    names: list[str] = []
    for name, content in protos:
        target = proto_dir / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        names.append(name)
    return proto_dir, tuple(names)


__all__ = [
    "flows_from_cache",
    "modules_from_cache",
    "protos_from_cache",
    "write_flows",
    "write_modules",
    "write_protos",
]
