"""urisys control-plane HTTP server.

The transport plumbing (JSON I/O, CORS, OPTIONS, threading, ``/uri/call``) is the
shared ``uri_control.edge.http`` implementation. urisys-specific views that return a
richer shape than the edge contract (full route dicts, explain, events) are
supplied as endpoint overrides, so nothing is duplicated and the wire contract
is preserved exactly.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from uri_control.edge.http import make_uri_handler

from .controllers.uri_controller import UriController
from .defaults import DEFAULT_ENVIRONMENT, DEFAULT_EVENTS_PATH
from .managers.event_manager import EventManager


class _ControllerRuntime:
    """Adapt UriController to the duck-typed runtime the shared transport calls.

    The transport invokes ``call(uri, payload, context)``; the controller takes a
    richer keyword signature, so we unpack the well-known context flags here.
    """

    def __init__(self, controller: UriController) -> None:
        self._controller = controller

    def call(self, uri: str, payload: dict, context: dict) -> dict:
        context = context or {}
        return self._controller.call(
            uri,
            payload or {},
            approved=bool(context.get("approved")),
            dry_run=bool(context.get("dry_run")),
            allow_real=bool(context.get("allow_real")),
            environment=str(context.get("environment", DEFAULT_ENVIRONMENT)),
            context=context,
        )


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length") or 0)
    if not length:
        return {}
    return json.loads(handler.rfile.read(length).decode("utf-8"))


def create_server(host: str, port: int, *, packs="all", markpacts=None, events_path=DEFAULT_EVENTS_PATH) -> ThreadingHTTPServer:
    controller = UriController(packs=packs, markpacts=markpacts, events_path=events_path)
    runtime = _ControllerRuntime(controller)

    def _health(handler, _runtime):
        handler._json(200, {"ok": True, "service": "urisys"})

    def _routes(handler, _runtime):
        handler._json(200, {"ok": True, "routes": controller.routes()})

    def _events(handler, _runtime):
        handler._json(200, {"ok": True, "events": EventManager(events_path).list_events()})

    def _explain(handler, _runtime):
        body = _read_json(handler)
        handler._json(200, {"ok": True, "explain": controller.explain(body["uri"])})

    extensions = {
        "GET /health": _health,
        "GET /uri/routes": _routes,
        "GET /uri/events": _events,
        "POST /uri/explain": _explain,
    }
    handler_cls = make_uri_handler(runtime, service="urisys", cors=True, extensions=extensions)
    return ThreadingHTTPServer((host, port), handler_cls)
