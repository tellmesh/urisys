from __future__ import annotations

from pathlib import Path

from ..flow import iter_steps, load_flow
from .uri_controller import UriController


class FlowController:
    def __init__(self, packs="all", *, markpacts=None, events_path: str | None = None) -> None:
        self.uri_controller = UriController(packs=packs, markpacts=markpacts, events_path=events_path)

    def run(self, path: str | Path, *, approved=False, dry_run=False, allow_real=False, environment="mock") -> dict:
        flow = load_flow(path)
        defaults = flow.get("defaults") or {}
        results = []
        for uri, payload in iter_steps(flow):
            result = self.uri_controller.call(
                uri,
                payload,
                approved=bool(defaults.get("approved", approved)),
                dry_run=bool(defaults.get("dry_run", dry_run)),
                allow_real=bool(defaults.get("allow_real", allow_real)),
                environment=str(defaults.get("environment", environment)),
            )
            results.append(result)
            if not result.get("ok") and not bool(defaults.get("continue_on_error")):
                break
        return {"ok": all(r.get("ok") for r in results), "flow": flow.get("flow", {}), "results": results}

    def close(self) -> None:
        self.uri_controller.close()
