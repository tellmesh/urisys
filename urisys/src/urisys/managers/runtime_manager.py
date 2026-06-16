from __future__ import annotations

from pathlib import Path

from uri_control import JsonlEventStore, PolicyEngine, UriControlRuntime

from ..defaults import DEFAULT_EVENTS_PATH
from .pack_manager import PackManager


class RuntimeManager:
    def __init__(self, packs="all", *, markpacts=None, events_path: str | None = None, allowed_schemes: set[str] | None = None) -> None:
        self.pack_manager = PackManager(packs, markpacts=markpacts)
        self.events_path = events_path or DEFAULT_EVENTS_PATH
        self.allowed_schemes = allowed_schemes

    def create_runtime(self) -> UriControlRuntime:
        registry = self.pack_manager.create_registry()
        event_store = JsonlEventStore(Path(self.events_path))
        policy = PolicyEngine(allowed_schemes=self.allowed_schemes)
        return UriControlRuntime(registry=registry, event_store=event_store, policy_engine=policy)

    def close(self) -> None:
        self.pack_manager.close()

    def __enter__(self) -> "RuntimeManager":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
