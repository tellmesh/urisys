from __future__ import annotations


class RouteManager:
    def __init__(self, runtime) -> None:
        self.runtime = runtime

    def explain(self, uri: str) -> dict:
        return self.runtime.registry.explain(uri)

    def list_routes(self) -> list[dict]:
        return [
            {
                "manifest_id": r.manifest_id,
                "scheme": r.scheme,
                "pattern": r.pattern,
                "kind": r.kind,
                "operation": r.operation,
                "approval": r.approval,
                "side_effects": r.side_effects,
            }
            for r in self.runtime.registry.routes
        ]
