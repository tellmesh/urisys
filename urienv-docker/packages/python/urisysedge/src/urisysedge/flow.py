from __future__ import annotations
from typing import Any
import yaml
from .runtime import result_to_dict

def run_flow(path: str, runtime, *, context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    context = context or {}
    with open(path, "r", encoding="utf-8") as f: data = yaml.safe_load(f) or {}
    defaults = data.get("defaults") or {}; results = []
    for item in data.get("do", []) or []:
        if isinstance(item, str): uri, payload = item, {}
        elif isinstance(item, dict) and len(item) == 1: uri, payload = next(iter(item.items())); payload = payload or {}
        else: raise ValueError(f"Invalid flow item: {item!r}")
        res = runtime.call(uri, payload, {**defaults, **context}); results.append(result_to_dict(res))
        if not res.ok and not defaults.get("continue_on_error"): break
    return results
