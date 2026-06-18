"""Parse fenced Markpact blocks from a single ``*.markpact.md`` file."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import (
    FENCE_RE,
    MarkpactBlock,
    MarkpactError,
    parse_meta,
    source_hash,
)


def read_blocks(path: str | Path) -> list[MarkpactBlock]:
    source_path = Path(path)
    text = source_path.read_text(encoding="utf-8")
    blocks: list[MarkpactBlock] = []
    for match in FENCE_RE.finditer(text):
        blocks.append(
            MarkpactBlock(
                lang=match.group("lang"),
                kind=match.group("kind"),
                meta=parse_meta(match.group("meta") or ""),
                content=match.group("content").strip() + "\n",
            )
        )
    return blocks


def yaml_blocks(blocks: list[MarkpactBlock], kind: str) -> list[MarkpactBlock]:
    return [b for b in blocks if b.kind == kind and b.lang in {"yaml", "yml"}]


def handler_blocks(blocks: list[MarkpactBlock]) -> dict[str, MarkpactBlock]:
    result: dict[str, MarkpactBlock] = {}
    for block in blocks:
        if block.kind != "handler":
            continue
        handler_id = block.meta.get("id") or block.meta.get("name")
        if not handler_id:
            raise MarkpactError("markpact:handler block must define id=<handler_id>.")
        result[handler_id] = block
    return result


def load_yaml_blocks(blocks: list[MarkpactBlock], kind: str) -> list[dict[str, Any]]:
    parsed: list[dict[str, Any]] = []
    for block in blocks:
        if block.kind != kind or block.lang not in {"yaml", "yml"}:
            continue
        data = yaml.safe_load(block.content) or {}
        if not isinstance(data, dict):
            raise MarkpactError(f"markpact:{kind} block must contain a YAML mapping.")
        parsed.append(data)
    return parsed


__all__ = ["handler_blocks", "load_yaml_blocks", "read_blocks", "source_hash", "yaml_blocks"]
