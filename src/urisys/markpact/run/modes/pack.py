from __future__ import annotations

from ..context import RunContext
from ..runtime_build import build_runtime, routes_summary


class PackMode:
    name = "pack"

    def run(self, ctx: RunContext) -> dict[str, Any]:
        rt = build_runtime(
            ctx.compiled,
            events_path=ctx.events_path,
            config=ctx.config,
            source_anchor=ctx.compiled.source_path,
            config_anchor=ctx.config_anchor,
        )
        return {**ctx.base, "routes": routes_summary(rt)}
