from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .controllers.uri_controller import UriController
from .managers.event_manager import EventManager


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length") or 0)
    if not length:
        return {}
    return json.loads(handler.rfile.read(length).decode("utf-8"))


def _send(handler: BaseHTTPRequestHandler, status: int, data: dict) -> None:
    raw = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type,Authorization")
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


def create_server(host: str, port: int, *, packs="all", markpacts=None, events_path="output/urisys-events.jsonl") -> ThreadingHTTPServer:
    controller = UriController(packs=packs, markpacts=markpacts, events_path=events_path)

    class Handler(BaseHTTPRequestHandler):
        def do_OPTIONS(self):
            _send(self, 204, {})

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/health":
                _send(self, 200, {"ok": True, "service": "urisys"})
                return
            if path == "/uri/routes":
                _send(self, 200, {"ok": True, "routes": controller.routes()})
                return
            if path == "/uri/events":
                _send(self, 200, {"ok": True, "events": EventManager(events_path).list_events()})
                return
            _send(self, 404, {"ok": False, "error": "not_found", "path": path})

        def do_POST(self):
            path = urlparse(self.path).path
            try:
                body = _read_json(self)
                if path == "/uri/call":
                    context = body.get("context") or {}
                    result = controller.call(
                        body["uri"],
                        body.get("payload") or {},
                        approved=bool(context.get("approved")),
                        dry_run=bool(context.get("dry_run")),
                        allow_real=bool(context.get("allow_real")),
                        environment=str(context.get("environment", "mock")),
                        context=context,
                    )
                    _send(self, 200 if result.get("ok") else 400, result)
                    return
                if path == "/uri/explain":
                    _send(self, 200, {"ok": True, "explain": controller.explain(body["uri"])})
                    return
                _send(self, 404, {"ok": False, "error": "not_found", "path": path})
            except Exception as exc:
                _send(self, 500, {"ok": False, "error": str(exc)})

        def log_message(self, format, *args):
            return

    return ThreadingHTTPServer((host, port), Handler)
