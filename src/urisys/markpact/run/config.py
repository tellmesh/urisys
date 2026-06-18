from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ...managers.markpact_manager import MarkpactManager


def read_run_config(path: str | Path) -> dict[str, Any]:
    blocks = MarkpactManager().read_blocks(path)
    run_blocks = [b for b in blocks if b.kind == "run" and b.lang in {"yaml", "yml"}]
    if not run_blocks:
        return {}
    data = yaml.safe_load(run_blocks[0].content) or {}
    return data if isinstance(data, dict) else {}


def load_run_config(config_path: str | None) -> tuple[dict[str, Any], Path | None]:
    if not config_path:
        return {}, None
    anchor = Path(config_path).resolve()
    config = yaml.safe_load(anchor.read_text(encoding="utf-8")) or {}
    return (config if isinstance(config, dict) else {}), anchor
