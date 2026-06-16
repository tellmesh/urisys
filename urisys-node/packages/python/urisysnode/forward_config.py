"""Load forward-pack definitions from node config or environment."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .serve import register_forward_pack


def _normalize_entry(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    scheme = str(raw.get("scheme") or "").strip()
    endpoint = str(raw.get("endpoint") or "").strip()
    patterns = raw.get("patterns")
    if not scheme or not endpoint or not isinstance(patterns, list) or not patterns:
        return None
    clean_patterns = [str(p).strip() for p in patterns if str(p).strip()]
    if not clean_patterns:
        return None
    return {"scheme": scheme, "endpoint": endpoint, "patterns": clean_patterns}


def load_forward_entries(*, config: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Collect forward definitions from config.forwards, env JSON, or env file path."""
    entries: list[dict[str, Any]] = []

    if config:
        for item in config.get("forwards") or []:
            norm = _normalize_entry(item)
            if norm:
                entries.append(norm)

    inline = os.environ.get("URISYS_NODE_FORWARDS", "").strip()
    if inline:
        try:
            parsed = json.loads(inline)
        except json.JSONDecodeError as exc:
            raise ValueError(f"URISYS_NODE_FORWARDS is not valid JSON: {exc}") from exc
        items = parsed if isinstance(parsed, list) else [parsed]
        for item in items:
            norm = _normalize_entry(item)
            if norm:
                entries.append(norm)

    file_path = os.environ.get("URISYS_NODE_FORWARDS_FILE", "").strip()
    if file_path:
        data = json.loads(Path(file_path).read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else [data]
        for item in items:
            norm = _normalize_entry(item)
            if norm:
                entries.append(norm)

    # de-dupe by scheme (last wins)
    by_scheme: dict[str, dict[str, Any]] = {}
    for entry in entries:
        by_scheme[entry["scheme"]] = entry
    return list(by_scheme.values())


def wire_forward_packs(runtime: Any, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for entry in entries:
        results.append(
            register_forward_pack(
                runtime,
                entry["scheme"],
                entry["endpoint"],
                entry["patterns"],
            )
        )
    return results
