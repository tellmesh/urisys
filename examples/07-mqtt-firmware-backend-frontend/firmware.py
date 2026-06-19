from __future__ import annotations

import argparse
import json
import time

from mqtt_codec import MqttClient
from uri_contract import DEVICE_ID, device_uris, mqtt_topics


def json_bytes(data: dict) -> bytes:
    return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")


class FirmwareDevice:
    def __init__(self, mqtt_host: str, mqtt_port: int, device_id: str) -> None:
        self.device_id = device_id
        self.topics = mqtt_topics(device_id)
        self.uris = device_uris(device_id)
        self.client = MqttClient(mqtt_host, mqtt_port, client_id=f"firmware-{device_id}")
        self.booted_at = time.time()
        self.led = False
        self.last_command = "boot"
        self.last_command_uri = None

    def start(self) -> None:
        self.client.connect()
        self.client.start()
        self.client.subscribe(self.topics["command_led"], self.on_led_command)
        self.client.subscribe(self.topics["command_ping"], self.on_ping_command)
        self.publish_state("online")
        while True:
            self.publish_state("heartbeat")
            self.publish_telemetry()
            time.sleep(1.0)

    def on_led_command(self, topic: str, payload: bytes) -> None:
        try:
            data = json.loads(payload.decode("utf-8"))
            command_payload = data.get("payload", data)
            self.last_command_uri = data.get("uri") or self.uris["led_set"]
            self.led = bool(command_payload.get("on"))
            self.last_command = "led:on" if self.led else "led:off"
            self.publish_state("led")
            self.publish_telemetry()
        except Exception as exc:
            self.publish_event("error", {"topic": topic, "error": str(exc)})

    def on_ping_command(self, _topic: str, payload: bytes) -> None:
        data = json.loads(payload.decode("utf-8"))
        self.last_command_uri = data.get("uri") or self.uris["ping_send"]
        self.last_command = "ping"
        self.publish_event("pong", {"payload": data.get("payload", data)})
        self.publish_state("ping")
        self.publish_telemetry()

    def publish_state(self, reason: str) -> None:
        self.client.publish(
            self.topics["state"],
            json_bytes(
                {
                    "device_id": self.device_id,
                    "firmware": "mqtt-demo-0.1",
                    "last_command": self.last_command,
                    "last_command_uri": self.last_command_uri,
                    "led": self.led,
                    "online": True,
                    "reason": reason,
                    "uri": self.uris["state_current"],
                    "uptime_ms": int((time.time() - self.booted_at) * 1000),
                }
            ),
        )

    def publish_telemetry(self) -> None:
        uptime_ms = int((time.time() - self.booted_at) * 1000)
        self.client.publish(
            self.topics["telemetry"],
            json_bytes(
                {
                    "device_id": self.device_id,
                    "led": self.led,
                    "temperature_c": round(21.5 + (uptime_ms % 7000) / 7000, 2),
                    "uri": self.uris["telemetry_latest"],
                    "uptime_ms": uptime_ms,
                    "voltage_v": 3.3,
                }
            ),
        )

    def publish_event(self, event: str, payload: dict) -> None:
        self.client.publish(
            self.topics["event"],
            json_bytes(
                {
                    "device_id": self.device_id,
                    "event": event,
                    "last_command_uri": self.last_command_uri,
                    "payload": payload,
                    "ts": time.time(),
                    "uri": self.uris["events_recent"],
                }
            ),
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="MQTT firmware simulator.")
    parser.add_argument("--mqtt-host", default="127.0.0.1")
    parser.add_argument("--mqtt-port", type=int, default=18883)
    parser.add_argument("--device-id", default=DEVICE_ID)
    args = parser.parse_args()
    FirmwareDevice(args.mqtt_host, args.mqtt_port, args.device_id).start()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
