from __future__ import annotations

from ..context import RunContext
from ..runtime_build import build_runtime


class ServiceMode:
    name = "service"

    def run(self, ctx: RunContext) -> dict[str, Any]:
        rt = build_runtime(
            ctx.compiled,
            events_path=ctx.events_path,
            config=ctx.config,
            source_anchor=ctx.compiled.source_path,
            config_anchor=ctx.config_anchor,
        )
        serve = ctx.serve_fn
        if serve is None:
            from uri_control.edge.http import serve as serve  # noqa: PLW0127
        run_cfg = ctx.run_cfg
        eff_port = ctx.port or (run_cfg.get("service") or {}).get("port") or 8790
        serve(rt, ctx.host, int(eff_port), service=str(ctx.scheme or ctx.compiled.package_id))
        return {**ctx.base, "served": True, "host": ctx.host, "port": int(eff_port)}
