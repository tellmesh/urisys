from __future__ import annotations

import importlib
import json
import re
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import unquote


def _result_ok(result: Any) -> bool:
    if isinstance(result, dict):
        if result.get("ok") is False:
            return False
        exit_code = result.get("exit_code")
        if exit_code is not None and exit_code != 0:
            return False
    return True


@dataclass
class Route:
    pattern: str
    kind: str
    operation: str
    handler_ref: str
    approval: str = "not_required"
    side_effects: bool = False
    _regex: re.Pattern | None = None

    def compile(self) -> "Route":
        parts: list[str] = []
        i = 0
        while i < len(self.pattern):
            if self.pattern[i] == "{":
                j = self.pattern.index("}", i)
                name = self.pattern[i + 1 : j]
                parts.append(f"(?P<{name}>[^/]+)")
                i = j + 1
            else:
                parts.append(re.escape(self.pattern[i]))
                i += 1
        self._regex = re.compile("^" + "".join(parts) + "$")
        return self

    def match(self, uri: str) -> dict[str, str] | None:
        if self._regex is None:
            self.compile()
        assert self._regex is not None
        m = self._regex.match(uri)
        if not m:
            return None
        return {k: unquote(v) for k, v in m.groupdict().items()}


class JsonlEventStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")


class Runtime:
    def __init__(self, events_path: str | Path = "data/events.jsonl", config: dict[str, Any] | None = None):
        self.routes: list[Route] = []
        self.events = JsonlEventStore(events_path)
        self.config = config or {}
        self.state: dict[str, Any] = {}

    def register(
        self,
        pattern: str,
        handler: str,
        *,
        kind: str = "command",
        operation: str | None = None,
        approval: str = "not_required",
        side_effects: bool = False,
    ) -> None:
        op = operation or pattern.rsplit("/", 1)[-1]
        self.routes.append(Route(pattern, kind, op, handler, approval, side_effects).compile())

    def resolve(self, uri: str) -> tuple[Route, dict[str, str]]:
        for route in self.routes:
            params = route.match(uri)
            if params is not None:
                return route, params
        raise KeyError(f"No route for URI: {uri}")

    def _load_handler(self, ref: str) -> Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]:
        if ref.startswith("python://"):
            ref = ref[len("python://") :]
        module_name, func_name = ref.split(":", 1)
        mod = importlib.import_module(module_name)
        return getattr(mod, func_name)

    def call(self, uri: str, payload: dict[str, Any] | None = None, context: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        context = context or {}
        try:
            route, params = self.resolve(uri)
        except Exception as exc:
            return {"ok": False, "uri": uri, "type": "route_not_found", "error": str(exc)}

        approved = bool(context.get("approved"))
        if route.side_effects and route.approval == "required" and not approved:
            return {"ok": False, "uri": uri, "type": "policy_denied", "reason": "approval required"}

        ctx = dict(context)
        ctx.update(
            {
                "uri": uri,
                "params": params,
                "config": self.config,
                "runtime": self,
                "state": self.state,
                "event_store": self.events,
            }
        )
        event_base = {
            "event_id": str(uuid.uuid4()),
            "source_uri": uri,
            "operation": route.operation,
            "kind": route.kind,
            "params": params,
            "occurred_at_unix_ms": int(time.time() * 1000),
        }
        self.events.append({**event_base, "event_type": "operation.accepted", "payload": payload})
        try:
            handler = self._load_handler(route.handler_ref)
            result = handler(payload, ctx)
            ok = _result_ok(result)
            event = {
                **event_base,
                "event_id": str(uuid.uuid4()),
                "event_type": f"{route.operation}.completed",
                "result": result,
            }
            self.events.append(event)
            return {"ok": ok, "uri": uri, "operation": route.operation, "params": params, "result": result, "event": event}
        except Exception as exc:
            event = {
                **event_base,
                "event_id": str(uuid.uuid4()),
                "event_type": f"{route.operation}.failed",
                "error": str(exc),
            }
            self.events.append(event)
            return {"ok": False, "uri": uri, "operation": route.operation, "error": str(exc), "event": event}


def load_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))
