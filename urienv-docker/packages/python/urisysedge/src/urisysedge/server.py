from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from .runtime import build_runtime, load_device_config, load_env_config, result_to_dict

def serve(*, host: str, port: int, packs: list[str], device_config_path: str | None = None, env_config_path: str | None = None, allow_real: bool = False):
    runtime = build_runtime(packs); device_config = load_device_config(device_config_path); env_config = load_env_config(env_config_path)
    class Handler(BaseHTTPRequestHandler):
        def _json(self, status: int, data: dict[str, Any]):
            body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
        def do_GET(self):
            if self.path == "/health": return self._json(200, {"ok": True, "runtime": "urisys-edge", "packs": packs})
            if self.path == "/routes": return self._json(200, {"ok": True, "routes": [r.__dict__ for r in runtime.registry.routes]})
            return self._json(404, {"ok": False, "error": "not found"})
        def do_POST(self):
            if self.path != "/uri/call": return self._json(404, {"ok": False, "error": "not found"})
            try:
                length = int(self.headers.get("Content-Length", "0")); body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
                context = body.get("context") or {}; context.setdefault("device_config", device_config); context.setdefault("env_config", env_config); context.setdefault("allow_real", allow_real)
                result = runtime.call(body["uri"], body.get("payload") or {}, context)
                return self._json(200 if result.ok else 400, result_to_dict(result))
            except Exception as exc: return self._json(500, {"ok": False, "error": str(exc)})
        def log_message(self, fmt, *args): print(f"{self.address_string()} - {fmt % args}")
    httpd = ThreadingHTTPServer((host, port), Handler); print(f"urisys-edge listening on http://{host}:{port} packs={packs}"); httpd.serve_forever()
