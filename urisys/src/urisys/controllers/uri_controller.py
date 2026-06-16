from __future__ import annotations

from ..managers.policy_manager import PolicyManager
from ..managers.route_manager import RouteManager
from ..managers.runtime_manager import RuntimeManager


class UriController:
    def __init__(self, packs="all", *, markpacts=None, events_path: str | None = None) -> None:
        self.runtime_manager = RuntimeManager(packs, markpacts=markpacts, events_path=events_path)
        self.runtime = self.runtime_manager.create_runtime()
        self.policy_manager = PolicyManager()
        self.route_manager = RouteManager(self.runtime)

    def call(self, uri: str, payload=None, *, approved=False, dry_run=False, allow_real=False, environment="mock", context=None) -> dict:
        ctx = self.policy_manager.build_context(
            approved=approved,
            dry_run=dry_run,
            allow_real=allow_real,
            environment=environment,
            extra=context or {},
        )
        return self.runtime.call(uri, payload or {}, ctx).to_dict()

    def explain(self, uri: str) -> dict:
        return self.route_manager.explain(uri)

    def routes(self) -> list[dict]:
        return self.route_manager.list_routes()

    def close(self) -> None:
        self.runtime_manager.close()
