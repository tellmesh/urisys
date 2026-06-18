from __future__ import annotations

import yaml

from ....managers.markpact_models import MarkpactError, safe_identifier
from ....managers.markpact_run_flow import packs_for_flow, pick_flow_id
from ...pack import capabilities, load_pack_block, scheme_for_pack
from ..context import RunContext
from ..runtime_build import apply_resolver_config, build_runtime


def _resolve_flow_ids(compiled, run_cfg):
    flow_id = run_cfg.get("_flow_id")
    ids = (run_cfg.get("flow") or {}).get("ids") or list(compiled.flow_ids)
    if flow_id:
        return [pick_flow_id(compiled, flow_id)]
    return list(ids) if ids else []


def _resolve_flow_uses(compiled, ids, path):
    pack = load_pack_block(path)
    pack_scheme = scheme_for_pack(pack, capabilities(pack))
    flow_uses: set[str] = set()
    flow_dir = compiled.flows_dir
    for fid in ids:
        fpath = flow_dir / f"{safe_identifier(fid, fallback='flow')}.uri.flow.yaml"
        if not fpath.exists():
            continue
        flow_data = yaml.safe_load(fpath.read_text(encoding="utf-8")) or {}
        uses, undeclared = packs_for_flow(pack, flow_data, pack_scheme=pack_scheme)
        if undeclared:
            raise MarkpactError(f"Flow {fid!r} uses schemes not declared in pack uses: {undeclared}")
        flow_uses.update(uses)
    return flow_uses


def _build_flow_runtime(ctx: RunContext, flow_uses):
    if flow_uses:
        from uri_control.edge.compose import build_runtime as compose_build_runtime

        from ....managers.markpact_pack_deps import ensure_flow_packs

        ensure_flow_packs(sorted(flow_uses), anchor=ctx.compiled.source_path, auto_install=ctx.auto_install)
        rt = compose_build_runtime(
            packs=",".join(sorted(flow_uses)),
            manifests=[str(ctx.compiled.manifest_path)],
            events_path=ctx.events_path,
            config=ctx.config,
        )
        apply_resolver_config(rt, ctx.config, config_anchor=ctx.config_anchor)
        return rt
    return build_runtime(
        ctx.compiled,
        events_path=ctx.events_path,
        config=ctx.config,
        source_anchor=ctx.compiled.source_path,
        config_anchor=ctx.config_anchor,
    )


class FlowMode:
    name = "flow"

    def run(self, ctx: RunContext) -> dict[str, Any]:
        from uri_control.edge.runtime import run_flow

        run_cfg = dict(ctx.run_cfg)
        if ctx.flow_id:
            run_cfg["_flow_id"] = ctx.flow_id
        ids = _resolve_flow_ids(ctx.compiled, run_cfg)
        flow_dir = ctx.compiled.flows_dir
        if not flow_dir or not ids:
            return {**ctx.base, "flows": [], "message": "No embedded flows."}

        context = {"approved": ctx.approve, "dry_run": ctx.dry_run}
        flow_uses = _resolve_flow_uses(ctx.compiled, ids, ctx.path)
        rt = _build_flow_runtime(ctx, flow_uses)

        results = []
        for fid in ids:
            fpath = flow_dir / f"{safe_identifier(fid, fallback='flow')}.uri.flow.yaml"
            if not fpath.exists():
                continue
            res = run_flow(rt, str(fpath), context)
            results.append({"id": fid, "ok": all(r.get("ok") for r in res), "results": res})
        return {**ctx.base, "ok": all(f["ok"] for f in results) if results else True, "flows": results}
