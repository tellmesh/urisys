from __future__ import annotations

from typing import Any

from ..context import RunContext
from ..runtime_build import build_runtime, routes_summary


class AdapterMode:
    name = "adapter"

    def run(self, ctx: RunContext) -> dict[str, Any]:
        run_cfg = ctx.run_cfg
        return {
            **ctx.base,
            "scheme": run_cfg.get("scheme"),
            "routes": routes_summary(
                build_runtime(
                    ctx.compiled,
                    events_path=ctx.events_path,
                    config=ctx.config,
                    source_anchor=ctx.compiled.source_path,
                    config_anchor=ctx.config_anchor,
                )
            ),
            "uses": run_cfg.get("uses") or [],
            "wire": (run_cfg.get("adapter") or {"call": "POST /uri/call", "events": "GET /events"}),
        }
