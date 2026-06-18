from __future__ import annotations

from ..context import RunContext
from ..runtime_build import build_runtime


class InterfaceMode:
    name = "interface"

    def run(self, ctx: RunContext) -> dict[str, Any]:
        rt = build_runtime(
            ctx.compiled,
            events_path=ctx.events_path,
            config=ctx.config,
            source_anchor=ctx.compiled.source_path,
            config_anchor=ctx.config_anchor,
        )
        explained = [
            {
                "uri": r.pattern,
                "kind": r.kind,
                "operation": r.operation,
                "requires_approval": r.approval == "required",
                "side_effects": r.side_effects,
            }
            for r in rt.routes
        ]
        return {**ctx.base, "scheme": ctx.scheme, "interface": explained}
