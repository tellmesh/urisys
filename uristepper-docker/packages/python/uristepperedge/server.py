from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .runtime import UriError, build_runtime


def make_handler(runtime):
    class Handler(BaseHTTPRequestHandler):
        server_version = "uristepper-edge/0.1"

        def _json(self, status: int, data: dict):
            body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):
            self._json(200, {"ok": True})

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/health":
                return self._json(
                    200,
                    {"ok": True, "service": "uristepper-docker", "node": os.environ.get("URISYS_NODE_ID", "stepper-node")},
                )
            if path == "/routes":
                return self._json(200, {"ok": True, "routes": runtime.list_routes()})
            if path == "/events":
                return self._json(200, {"ok": True, "events": runtime.event_store.tail(100)})
            return self._json(404, {"ok": False, "error": "not_found"})

        def do_POST(self):
            path = urlparse(self.path).path
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            try:
                data = json.loads(raw or "{}")
            except Exception as exc:
                return self._json(400, {"ok": False, "error": f"invalid_json: {exc}"})

            try:
                if path == "/uri/call":
                    result = runtime.call(data.get("uri", ""), data.get("payload") or {}, data.get("context") or {})
                    return self._json(200 if result.get("ok") else 400, result)
                if path == "/uri/explain":
                    return self._json(200, runtime.explain(data.get("uri", "")))
            except UriError as exc:
                return self._json(404, {"ok": False, "error": str(exc)})
            except Exception as exc:
                return self._json(500, {"ok": False, "error": str(exc)})

            return self._json(404, {"ok": False, "error": "not_found"})

        def log_message(self, fmt, *args):
            print("[http] " + fmt % args)

    return Handler


def serve(host: str = "0.0.0.0", port: int = 8790, device_profile: str | None = None, events_path: str | None = None):
    runtime = build_runtime(device_profile, events_path)
    httpd = ThreadingHTTPServer((host, port), make_handler(runtime))
    print(f"uristepper-edge listening on http://{host}:{port}")
    httpd.serve_forever()
