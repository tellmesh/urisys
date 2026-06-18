from __future__ import annotations

from pathlib import Path
from typing import Any

from ...managers.markpact_manager import MarkpactManager
from ..models import MarkpactError
from .config import load_run_config, read_run_config
from .context import RunContext
from .modes import RUN_MODES

DEFAULT_OUT = ".markpact"


def run_markpact(
    path: str | Path,
    *,
    mode: str | None = None,
    flow_id: str | None = None,
    out: str | Path = DEFAULT_OUT,
    host: str = "0.0.0.0",
    port: int | None = None,
    config_path: str | None = None,
    approve: bool = False,
    dry_run: bool = False,
    auto_install: bool = False,
    serve_fn=None,
) -> dict[str, Any]:
    manager = MarkpactManager(cache_root=out)
    compiled = manager.compile(path, force=True)
    run_cfg = read_run_config(path)

    modes = run_cfg.get("modes") or ["pack", "service", "flow", "interface", "adapter"]
    mode = mode or run_cfg.get("default") or "pack"
    if mode not in modes:
        raise MarkpactError(f"Mode {mode!r} not in declared modes {modes}.")

    handler = RUN_MODES.get(mode)
    if handler is None:
        raise MarkpactError(f"Unknown run mode {mode!r}.")

    events_path = str(Path(compiled.cache_dir) / "events.jsonl")
    config, config_anchor = load_run_config(config_path)
    base = {"ok": True, "mode": mode, "package_id": compiled.package_id, "cache_dir": str(compiled.cache_dir)}

    ctx = RunContext(
        compiled=compiled,
        path=Path(path),
        run_cfg=run_cfg,
        base=base,
        events_path=events_path,
        config=config,
        config_anchor=config_anchor,
        approve=approve,
        dry_run=dry_run,
        auto_install=auto_install,
        host=host,
        port=port,
        flow_id=flow_id,
        serve_fn=serve_fn,
        scheme=run_cfg.get("scheme"),
    )
    return handler.run(ctx)


__all__ = ["DEFAULT_OUT", "read_run_config", "run_markpact"]
