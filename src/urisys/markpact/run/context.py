from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


@dataclass
class RunContext:
    compiled: Any
    path: Path
    run_cfg: dict[str, Any]
    base: dict[str, Any]
    events_path: str
    config: dict[str, Any]
    config_anchor: Path | None
    approve: bool = False
    dry_run: bool = False
    auto_install: bool = False
    host: str = "0.0.0.0"
    port: int | None = None
    flow_id: str | None = None
    serve_fn: Callable[..., Any] | None = None
    scheme: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)
