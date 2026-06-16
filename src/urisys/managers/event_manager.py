from __future__ import annotations

from pathlib import Path

from uri_control.event_store import JsonlEventStore, dump_events


class EventManager:
    def __init__(self, path: str) -> None:
        self.store = JsonlEventStore(Path(path))

    def list_events(self) -> list[dict]:
        return dump_events(self.store.read_all())
