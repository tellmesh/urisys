from __future__ import annotations

import argparse
import json
import mimetypes
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse

from mqtt_codec import MqttClient


class DeviceSnapshot:
    def __init__(self) -> None:
        self.lock = Lock()
        self.state: dict = {}
        self.telemetry: dict = {}
        self.events: list[dict] = []

    def update(self, kind: str, payload: bytes) -> None:
        try:
            data = json.loads(payload.decode("utf-8"))
        except json.JSONDecodeError:
            data = {"raw": payload.decode("utf-8", errors="replace")}
        with self.lock:
            if kind == "state":
                self.state = data
            elif kind == "telemetry":
                self.telemetry = data
            else:
                self.events.append(data)
                self.events = self.events[-20:]

    def to_dict(self) -> dict:
        with self.lock:
            return {
                "events": list(self.events),
                "state": dict(self.state),
                "telemetry": dict(self.telemetry),
            }


class AppState:
    def __init__(self, mqtt: MqttClient, device_id: str, snapshot: DeviceSnapshot, static_root: Path) -> None:
        self.mqtt = mqtt
        self.device_id = device_id
        self.base_topic = f"urisys/example/{device_id}"
        self.snapshot = snapshot
        self.static_root = static_root

    def topics(self) -> dict:
        return {
            "command_led": f"{self.base_topic}/command/led",
            "command_ping": f"{self.base_topic}/command/ping",
            "event": f"{self.base_topic}/event",
            "state": f"{self.base_topic}/state",
            "telemetry": f"{self.base_topic}/telemetry",
        }


class Handler(BaseHTTPRequestHandler):
    app: AppState

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self._json(200, {"ok": True, "service": "mqtt-demo-backend"})
        elif path == "/api/mqtt/topics":
            self._json(200, {"ok": True, "topics": self.app.topics()})
        elif path == "/api/device/state":
            self._json(200, {"ok": True, **self.app.snapshot.to_dict(), "topics": self.app.topics()})
        elif path == "/api/device/telemetry":
            self._json(200, {"ok": True, "telemetry": self.app.snapshot.to_dict()["telemetry"]})
        elif path == "/api/device/events":
            self._json(200, {"ok": True, "events": self.app.snapshot.to_dict()["events"]})
        else:
            self._static(path)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        body = self._read_json()
        if path == "/api/device/led":
            payload = {"on": bool(body.get("on")), "source": "frontend", "ts": time.time()}
            topic = self.app.topics()["command_led"]
            self.app.mqtt.publish(topic, json.dumps(payload))
            self._json(200, {"ok": True, "published": {"topic": topic, "payload": payload}})
        elif path == "/api/device/ping":
            payload = {"source": body.get("source") or "frontend", "ts": time.time()}
            topic = self.app.topics()["command_ping"]
            self.app.mqtt.publish(topic, json.dumps(payload))
            self._json(200, {"ok": True, "published": {"topic": topic, "payload": payload}})
        elif path == "/api/mqtt/publish":
            topic = str(body.get("topic") or "")
            payload = body.get("payload", {})
            if not topic:
                self._json(400, {"ok": False, "error": "topic is required"})
                return
            self.app.mqtt.publish(topic, json.dumps(payload))
            self._json(200, {"ok": True, "published": {"topic": topic, "payload": payload}})
        else:
            self._json(404, {"ok": False, "error": f"unknown endpoint: {path}"})

    def log_message(self, fmt: str, *args) -> None:
        return

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def _json(self, status: int, data: dict) -> None:
        raw = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _static(self, path: str) -> None:
        if path in ("", "/"):
            path = "/index.html"
        candidate = (self.app.static_root / path.lstrip("/")).resolve()
        if not str(candidate).startswith(str(self.app.static_root.resolve())) or not candidate.is_file():
            self._json(404, {"ok": False, "error": "not found"})
            return
        raw = candidate.read_bytes()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", mimetypes.guess_type(str(candidate))[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def build_server(host: str, port: int, app: AppState) -> ThreadingHTTPServer:
    handler_cls = type("MqttDemoHandler", (Handler,), {"app": app})
    return ThreadingHTTPServer((host, port), handler_cls)


def main() -> int:
    parser = argparse.ArgumentParser(description="HTTP to MQTT bridge for the urisys example.")
    parser.add_argument("--mqtt-host", default="127.0.0.1")
    parser.add_argument("--mqtt-port", type=int, default=18883)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8097)
    parser.add_argument("--device-id", default="device-01")
    parser.add_argument("--static", default=str(Path(__file__).with_name("frontend")))
    args = parser.parse_args()

    snapshot = DeviceSnapshot()
    client = MqttClient(args.mqtt_host, args.mqtt_port, client_id="backend-http-bridge")
    client.connect()
    client.start()
    base = f"urisys/example/{args.device_id}"
    client.subscribe(f"{base}/state", lambda _topic, payload: snapshot.update("state", payload))
    client.subscribe(f"{base}/telemetry", lambda _topic, payload: snapshot.update("telemetry", payload))
    client.subscribe(f"{base}/event", lambda _topic, payload: snapshot.update("event", payload))

    app = AppState(client, args.device_id, snapshot, Path(args.static))
    server = build_server(args.host, args.port, app)
    print(f"HTTP backend listening on http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    finally:
        client.close()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
