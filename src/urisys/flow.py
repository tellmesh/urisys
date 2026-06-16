from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_flow(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError("Flow must be a YAML mapping.")
    return data


def iter_steps(flow: dict[str, Any]):
    for item in flow.get("do", []) or []:
        if isinstance(item, str):
            yield item, {}
        elif isinstance(item, dict) and len(item) == 1:
            uri, payload = next(iter(item.items()))
            yield uri, payload or {}
        else:
            raise ValueError(f"Invalid flow step: {item!r}")
