from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def apply_resolver_config(rt, config: dict[str, Any] | None, *, config_anchor: Path | None = None) -> None:
    cfg = config or {}
    resolver_path = cfg.get("resolver_path") or os.environ.get("URISYS_RESOLVER_CONFIG")
    if resolver_path:
        from uri_router.resolver import load_resolver_into_runtime

        path = Path(resolver_path)
        if not path.is_absolute() and config_anchor is not None:
            path = (config_anchor.parent / path).resolve()
        elif not path.is_absolute():
            path = (Path.cwd() / path).resolve()
        load_resolver_into_runtime(rt, path)


def build_runtime(
    compiled,
    *,
    events_path: str,
    config: dict[str, Any] | None,
    source_anchor: Path | None = None,
    config_anchor: Path | None = None,
):
    from uri_control.edge.manifest import register_manifest_file
    from uri_control.edge.runtime import Runtime

    from ...managers.markpact_pack_deps import extend_tellmesh_paths

    extend_tellmesh_paths(anchor=source_anchor or compiled.source_path)
    cfg = dict(config or {})
    rt = Runtime(events_path=events_path, config=cfg)
    register_manifest_file(rt, compiled.manifest_path)
    apply_resolver_config(rt, cfg, config_anchor=config_anchor)
    return rt


def routes_summary(rt) -> list[dict[str, Any]]:
    return [
        {
            "pattern": r.pattern,
            "kind": r.kind,
            "operation": r.operation,
            "approval": r.approval,
            "side_effects": r.side_effects,
        }
        for r in rt.routes
    ]
