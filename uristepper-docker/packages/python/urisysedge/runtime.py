from __future__ import annotations

import json
import os
import re
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional
from urllib.parse import urlparse


class UriError(Exception):
    pass


class PolicyDenied(UriError):
    pass


@dataclass
class Route:
    pattern: str
    operation: str
    kind: str
    handler: Callable[[dict, dict], dict]
    requires_approval: bool = False
    side_effects: bool = False
    regex: Optional[re.Pattern] = None

    def compile(self) -> "Route":
        # Convert stepper://{device}/axis/{axis}/command/move-relative to regex.
        escaped = re.escape(self.pattern)
        escaped = escaped.replace(re.escape("{device}"), r"(?P<device>[^/]+)")
        escaped = escaped.replace(re.escape("{axis}"), r"(?P<axis>[^/]+)")
        self.regex = re.compile("^" + escaped + "$")
        return self

    def match(self, uri: str) -> Optional[dict]:
        if self.regex is None:
            self.compile()
        m = self.regex.match(uri)
        return m.groupdict() if m else None


class JsonlEventStore:
    def __init__(self, path: str | os.PathLike[str]):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: dict) -> None:
        event = dict(event)
        event.setdefault("event_id", str(uuid.uuid4()))
        event.setdefault("occurred_at_unix_ms", int(time.time() * 1000))
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    def tail(self, limit: int = 100) -> list[dict]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()[-limit:]
        out = []
        for line in lines:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
        return out


class StepperRuntime:
    def __init__(self, routes: list[Route], device_profile: dict | None = None, event_store: JsonlEventStore | None = None):
        self.routes = [r.compile() for r in routes]
        self.device_profile = device_profile or {}
        self.event_store = event_store or JsonlEventStore(os.environ.get("URISYS_EVENTS_PATH", "/tmp/urisys-events.jsonl"))

    def explain(self, uri: str) -> dict:
        route, params = self._match(uri)
        return {
            "ok": True,
            "uri": uri,
            "operation": route.operation,
            "kind": route.kind,
            "params": params,
            "requires_approval": route.requires_approval,
            "side_effects": route.side_effects,
            "device_profile_id": self.device_profile.get("metadata", {}).get("id"),
        }

    def list_routes(self) -> list[dict]:
        return [
            {
                "pattern": r.pattern,
                "operation": r.operation,
                "kind": r.kind,
                "requires_approval": r.requires_approval,
                "side_effects": r.side_effects,
            }
            for r in self.routes
        ]

    def call(self, uri: str, payload: dict | None = None, context: dict | None = None) -> dict:
        payload = payload or {}
        context = context or {}
        route, params = self._match(uri)
        command_id = str(uuid.uuid4())

        if route.requires_approval and not context.get("approved"):
            event = {
                "event_type": "policy.denied",
                "source_uri": uri,
                "operation": route.operation,
                "reason": "approval_required",
                "command_id": command_id,
            }
            self.event_store.append(event)
            return {"ok": False, "type": "policy_denied", "reason": "approval_required", "uri": uri, "event": event}

        # Attach route params and device config to handler context.
        effective_context = dict(context)
        effective_context["params"] = params
        effective_context["device_profile"] = self.device_profile
        effective_context["command_id"] = command_id
        effective_context["uri"] = uri

        self.event_store.append({
            "event_type": "command.accepted",
            "source_uri": uri,
            "operation": route.operation,
            "command_id": command_id,
            "payload": payload,
            "params": params,
            "device_profile_id": self.device_profile.get("metadata", {}).get("id"),
        })

        try:
            result = route.handler(payload, effective_context)
            event = {
                "event_type": f"stepper.{route.operation}.completed",
                "source_uri": uri,
                "operation": route.operation,
                "command_id": command_id,
                "payload": result,
                "params": params,
                "device_profile_id": self.device_profile.get("metadata", {}).get("id"),
                "implementation_id": self.device_profile.get("runtime", {}).get("implementation"),
            }
            self.event_store.append(event)
            return {"ok": True, "uri": uri, "operation": route.operation, "result": result, "event": event}
        except Exception as exc:
            event = {
                "event_type": f"stepper.{route.operation}.failed",
                "source_uri": uri,
                "operation": route.operation,
                "command_id": command_id,
                "error": str(exc),
            }
            self.event_store.append(event)
            return {"ok": False, "uri": uri, "operation": route.operation, "error": str(exc), "event": event}

    def _match(self, uri: str) -> tuple[Route, dict]:
        parsed = urlparse(uri)
        if parsed.scheme != "stepper":
            raise UriError(f"Unsupported scheme: {parsed.scheme}")
        for route in self.routes:
            params = route.match(uri)
            if params is not None:
                return route, params
        raise UriError(f"No route matched URI: {uri}")


def load_json(path: str | os.PathLike[str]) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_runtime(device_profile_path: str | None = None, events_path: str | None = None) -> StepperRuntime:
    from uristepper import handlers

    profile_path = device_profile_path or os.environ.get("URISYS_DEVICE_PROFILE") or "config/device-profile.json"
    profile = load_json(profile_path) if profile_path and Path(profile_path).exists() else {}
    store = JsonlEventStore(events_path or os.environ.get("URISYS_EVENTS_PATH", "/tmp/urisys-events.jsonl"))

    routes = [
        Route("stepper://{device}/axis/{axis}/query/status", "status", "query", handlers.status, False, False),
        Route("stepper://{device}/axis/{axis}/command/enable", "enable", "command", handlers.enable, True, True),
        Route("stepper://{device}/axis/{axis}/command/disable", "disable", "command", handlers.disable, True, True),
        Route("stepper://{device}/axis/{axis}/command/stop", "stop", "command", handlers.stop, True, True),
        Route("stepper://{device}/axis/{axis}/command/home", "home", "command", handlers.home, True, True),
        Route("stepper://{device}/axis/{axis}/command/move-relative", "move_relative", "command", handlers.move_relative, True, True),
        Route("stepper://{device}/axis/{axis}/command/move-absolute", "move_absolute", "command", handlers.move_absolute, True, True),
    ]
    return StepperRuntime(routes, device_profile=profile, event_store=store)
