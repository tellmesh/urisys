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
from uri_contract import DEVICE_ID, command_topic_for_uri, device_uris, mqtt_topics, query_kind_for_uri


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
        self.snapshot = snapshot
        self.static_root = static_root

    def uris(self) -> dict:
        return device_uris(self.device_id)

    def topics(self) -> dict:
        return mqtt_topics(self.device_id)

    def call_uri(self, uri: str, payload: dict | None = None) -> dict:
        payload = payload or {}
        topic = command_topic_for_uri(uri, self.device_id)
        if topic:
            envelope = {"payload": payload, "source": "backend", "ts": time.time(), "uri": uri}
            self.mqtt.publish(topic, json.dumps(envelope))
            return {"kind": "command", "published": {"payload": envelope, "topic": topic}}

        kind = query_kind_for_uri(uri, self.device_id)
        snapshot = self.snapshot.to_dict()
        if kind == "state":
            return {"kind": "query", "result": {**snapshot, "topics": self.topics(), "uris": self.uris()}}
        if kind == "telemetry":
            return {"kind": "query", "result": {"telemetry": snapshot["telemetry"]}}
        if kind == "events":
            return {"kind": "query", "result": {"events": snapshot["events"]}}
        if kind == "topics":
            return {"kind": "query", "result": {"topics": self.topics(), "uris": self.uris()}}
        raise KeyError(f"unknown URI: {uri}")


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
        elif path == "/api/uris":
            self._json(200, {"ok": True, "uris": self.app.uris()})
        elif path == "/api/mqtt/topics":
            self._json(200, {"ok": True, "topics": self.app.topics(), "uris": self.app.uris()})
        elif path == "/api/device/state":
            self._json(200, {"ok": True, **self.app.snapshot.to_dict(), "topics": self.app.topics(), "uris": self.app.uris()})
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
            self._call_uri(self.app.uris()["led_set"], {"on": bool(body.get("on"))})
        elif path == "/api/device/ping":
            self._call_uri(self.app.uris()["ping_send"], {"source": body.get("source") or "frontend"})
        elif path == "/api/uri/call":
            uri = str(body.get("uri") or "")
            payload = body.get("payload") or {}
            self._call_uri(uri, payload)
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

    def _call_uri(self, uri: str, payload: dict) -> None:
        if not uri:
            self._json(400, {"ok": False, "error": "uri is required"})
            return
        try:
            result = self.app.call_uri(uri, payload)
        except KeyError as exc:
            self._json(404, {"ok": False, "error": str(exc), "uri": uri})
            return
        self._json(200, {"ok": True, "uri": uri, **result})

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
    parser.add_argument("--device-id", default=DEVICE_ID)
    parser.add_argument("--static", default=str(Path(__file__).with_name("frontend")))
    args = parser.parse_args()

    snapshot = DeviceSnapshot()
    client = MqttClient(args.mqtt_host, args.mqtt_port, client_id="backend-http-bridge")
    client.connect()
    client.start()
    topics = mqtt_topics(args.device_id)
    client.subscribe(topics["state"], lambda _topic, payload: snapshot.update("state", payload))
    client.subscribe(topics["telemetry"], lambda _topic, payload: snapshot.update("telemetry", payload))
    client.subscribe(topics["event"], lambda _topic, payload: snapshot.update("event", payload))

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
