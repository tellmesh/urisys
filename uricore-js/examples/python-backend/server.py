#!/usr/bin/env python3
"""Minimal Python-compatible URI backend.

This uses the same /uri/call envelope as uricore-js. In a real project,
replace the small dispatch below with the Python uricore runtime created
in ../uricore/core/python/uri_control.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
import uuid

EVENTS = []


def append_event(event):
    event.setdefault("event_id", f"evt_{uuid.uuid4().hex[:12]}")
    event.setdefault("occurred_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    EVENTS.append(event)
    return event


class Handler(BaseHTTPRequestHandler):
    def _json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._json(200, {"ok": True})

    def do_GET(self):
        if self.path.startswith("/health"):
            self._json(200, {"ok": True, "service": "uricore-python-compatible"})
            return
        if self.path.startswith("/uri/events"):
            self._json(200, {"ok": True, "events": EVENTS})
            return
        self._json(404, {"ok": False, "error": "not_found"})

    def do_POST(self):
        if self.path != "/uri/call":
            self._json(404, {"ok": False, "error": "not_found"})
            return

        length = int(self.headers.get("content-length", "0"))
        body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        uri = body.get("uri")
        payload = body.get("payload") or {}
        command_id = f"cmd_{uuid.uuid4().hex[:12]}"

        append_event({
            "event_type": "uricore.command.accepted",
            "source_uri": uri,
            "command_id": command_id,
            "payload": payload,
        })

        if uri == "py://math/add":
            result = {"sum": float(payload.get("a", 0)) + float(payload.get("b", 0)), "backend": "python"}
            event = append_event({
                "event_type": "py.math.add.completed",
                "source_uri": uri,
                "command_id": command_id,
                "payload": result,
            })
            self._json(200, {"ok": True, "uri": uri, "result": result, "event": event})
            return

        event = append_event({
            "event_type": "uricore.operation.failed",
            "source_uri": uri,
            "command_id": command_id,
            "error": {"type": "not_found", "message": f"Unsupported URI: {uri}"},
        })
        self._json(400, {"ok": False, "uri": uri, "event": event})


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8090), Handler)
    print("uricore Python-compatible backend on http://127.0.0.1:8090")
    server.serve_forever()
