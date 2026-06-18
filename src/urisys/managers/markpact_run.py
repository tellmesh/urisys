"""Unpack a Markpact into ``.markpact/`` and run it in a configuration-driven mode.

Modes (declared in the ``markpact:run`` block, overridable with ``--as``):

* ``pack``      — register the capabilities into a runtime and list routes (library use)
* ``service``   — serve the URIs over HTTP (``POST /uri/call``) — a ``scheme://`` process
* ``flow``      — execute the embedded ``markpact:flow`` use cases
* ``interface`` — print the human/CLI interface (explain every route)
* ``adapter``   — emit the integration contract (routes + uses + wire ABI) as JSON

The Markpact is compiled (unpacked) into ``<out>/<id>/<hash>/`` — by default
``.markpact/`` in the current directory — with manifest, handler modules, flows
and protos written to disk, and that dir placed on ``sys.path``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .markpact_manager import MarkpactManager
from .markpact_models import MarkpactError

DEFAULT_OUT = ".markpact"


def read_run_config(path: str | Path) -> dict[str, Any]:
    blocks = MarkpactManager().read_blocks(path)
    run_blocks = [b for b in blocks if b.kind == "run" and b.lang in {"yaml", "yml"}]
    if not run_blocks:
        return {}
    data = yaml.safe_load(run_blocks[0].content) or {}
    return data if isinstance(data, dict) else {}


def _apply_resolver_config(rt, config: dict[str, Any] | None, *, config_anchor: Path | None = None) -> None:
    import os

    cfg = config or {}
    resolver_path = cfg.get("resolver_path") or os.environ.get("URISYS_RESOLVER_CONFIG")
    if resolver_path:
        from uri_control.resolver import load_resolver_into_runtime

        path = Path(resolver_path)
        if not path.is_absolute() and config_anchor is not None:
            path = (config_anchor.parent / path).resolve()
        elif not path.is_absolute():
            path = (Path.cwd() / path).resolve()
        load_resolver_into_runtime(rt, path)


def _load_run_config(config_path: str | None) -> tuple[dict[str, Any], Path | None]:
    if not config_path:
        return {}, None
    anchor = Path(config_path).resolve()
    config = yaml.safe_load(anchor.read_text(encoding="utf-8")) or {}
    return (config if isinstance(config, dict) else {}), anchor


def _build_runtime(
    compiled,
    *,
    events_path: str,
    config: dict[str, Any] | None,
    source_anchor: Path | None = None,
    config_anchor: Path | None = None,
):
    from urisysedge.manifest import register_manifest_file
    from urisysedge.runtime import Runtime

    from .markpact_pack_deps import extend_tellmesh_paths

    extend_tellmesh_paths(anchor=source_anchor or compiled.source_path)
    cfg = dict(config or {})
    rt = Runtime(events_path=events_path, config=cfg)
    register_manifest_file(rt, compiled.manifest_path)

    _apply_resolver_config(rt, cfg, config_anchor=config_anchor)
    return rt


def _routes_summary(rt) -> list[dict[str, Any]]:
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

    scheme = run_cfg.get("scheme")
    events_path = str(Path(compiled.cache_dir) / "events.jsonl")
    config, config_anchor = _load_run_config(config_path)

    base = {"ok": True, "mode": mode, "package_id": compiled.package_id, "cache_dir": str(compiled.cache_dir)}

    if mode == "adapter":
        return {
            **base,
            "scheme": scheme,
            "routes": _routes_summary(
                _build_runtime(
                    compiled,
                    events_path=events_path,
                    config=config,
                    source_anchor=compiled.source_path,
                    config_anchor=config_anchor,
                )
            ),
            "uses": run_cfg.get("uses") or [],
            "wire": (run_cfg.get("adapter") or {"call": "POST /uri/call", "events": "GET /events"}),
        }

    if mode == "flow":
        from urisysedge.runtime import run_flow

        from .markpact_models import safe_identifier
        from .markpact_run_flow import packs_for_flow, pick_flow_id

        context = {"approved": approve, "dry_run": dry_run}
        results = []
        flow_dir = compiled.flows_dir
        ids = (run_cfg.get("flow") or {}).get("ids") or list(compiled.flow_ids)
        if flow_id:
            ids = [pick_flow_id(compiled, flow_id)]
        if not flow_dir or not ids:
            return {**base, "flows": [], "message": "No embedded flows."}

        mgr = MarkpactManager()
        pack = mgr.load_pack_block(path)
        pack_scheme = mgr._scheme(pack, mgr._capabilities(pack))
        flow_uses: set[str] = set()
        for fid in ids:
            fpath = flow_dir / f"{safe_identifier(fid, fallback='flow')}.uri.flow.yaml"
            if not fpath.exists():
                continue
            flow_data = yaml.safe_load(fpath.read_text(encoding="utf-8")) or {}
            uses, undeclared = packs_for_flow(pack, flow_data, pack_scheme=pack_scheme)
            if undeclared:
                raise MarkpactError(
                    f"Flow {fid!r} uses schemes not declared in pack uses: {undeclared}"
                )
            flow_uses.update(uses)

        if flow_uses:
            from urisysedge.compose import build_runtime

            from .markpact_pack_deps import ensure_flow_packs

            ensure_flow_packs(sorted(flow_uses), anchor=compiled.source_path, auto_install=auto_install)
            rt = build_runtime(
                packs=",".join(sorted(flow_uses)),
                manifests=[str(compiled.manifest_path)],
                events_path=events_path,
                config=config,
            )
            _apply_resolver_config(rt, config, config_anchor=config_anchor)
        else:
            rt = _build_runtime(
                compiled,
                events_path=events_path,
                config=config,
                source_anchor=compiled.source_path,
                config_anchor=config_anchor,
            )

        for fid in ids:
            fpath = flow_dir / f"{safe_identifier(fid, fallback='flow')}.uri.flow.yaml"
            if not fpath.exists():
                continue
            res = run_flow(rt, str(fpath), context)
            results.append({"id": fid, "ok": all(r.get("ok") for r in res), "results": res})
        return {**base, "ok": all(f["ok"] for f in results) if results else True, "flows": results}

    rt = _build_runtime(
        compiled,
        events_path=events_path,
        config=config,
        source_anchor=compiled.source_path,
        config_anchor=config_anchor,
    )

    if mode == "pack":
        return {**base, "routes": _routes_summary(rt)}

    if mode == "interface":
        explained = []
        for r in rt.routes:
            explained.append(
                {
                    "uri": r.pattern,
                    "kind": r.kind,
                    "operation": r.operation,
                    "requires_approval": r.approval == "required",
                    "side_effects": r.side_effects,
                }
            )
        return {**base, "scheme": scheme, "interface": explained}

    if mode == "service":
        serve = serve_fn
        if serve is None:
            from urisysedge.http import serve as serve  # noqa: PLW0127
        eff_port = port or (run_cfg.get("service") or {}).get("port") or 8790
        serve(rt, host, int(eff_port), service=str(scheme or compiled.package_id))
        return {**base, "served": True, "host": host, "port": int(eff_port)}

    raise MarkpactError(f"Unknown run mode {mode!r}.")
