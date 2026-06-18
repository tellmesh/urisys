"""UriPack metadata helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import MarkpactError, scheme_from_uri
from .blocks import read_blocks, yaml_blocks


def load_pack_block(path: str | Path) -> dict[str, Any]:
    source_path = Path(path)
    pack_blocks = yaml_blocks(read_blocks(source_path), "pack")
    if len(pack_blocks) != 1:
        raise MarkpactError(
            f"{path}: expected exactly one ```yaml markpact:pack``` block, found {len(pack_blocks)}."
        )
    data = yaml.safe_load(pack_blocks[0].content) or {}
    if not isinstance(data, dict):
        raise MarkpactError(f"{path}: markpact:pack block must contain a YAML mapping.")
    return data


def package_id(pack: dict[str, Any], path: Path) -> str:
    metadata = pack.get("metadata") or {}
    value = pack.get("id") or metadata.get("id") or path.stem.replace(".markpact", "")
    value = str(value).strip()
    if not value:
        raise MarkpactError(f"{path}: package id is required.")
    return value


def capabilities(pack: dict[str, Any]) -> list[dict[str, Any]]:
    raw = pack.get("uri_patterns") or pack.get("capabilities") or []
    if not isinstance(raw, list):
        raise MarkpactError("capabilities/uri_patterns must be a list.")
    return [item for item in raw if isinstance(item, dict)]


def scheme_for_pack(pack: dict[str, Any], caps: list[dict[str, Any]]) -> str:
    if pack.get("scheme"):
        return str(pack["scheme"])
    schemes = pack.get("schemes") or []
    if isinstance(schemes, list) and schemes:
        return str(schemes[0])
    if caps:
        return scheme_from_uri(str(caps[0].get("pattern") or caps[0].get("uri") or ""))
    raise MarkpactError("Cannot infer scheme from Markpact.")


__all__ = ["capabilities", "load_pack_block", "package_id", "scheme_for_pack"]
