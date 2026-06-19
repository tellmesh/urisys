from __future__ import annotations

import argparse
import socket
import socketserver
import struct
import threading
import time
from collections.abc import Callable


CONNECT = 1
CONNACK = 2
PUBLISH = 3
SUBSCRIBE = 8
SUBACK = 9
PINGREQ = 12
PINGRESP = 13
DISCONNECT = 14


def encode_varint(value: int) -> bytes:
    out = bytearray()
    while True:
        digit = value % 128
        value //= 128
        if value > 0:
            digit |= 0x80
        out.append(digit)
        if value == 0:
            return bytes(out)


def read_exact(sock: socket.socket, size: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        chunk = sock.recv(size - len(chunks))
        if not chunk:
            raise EOFError("socket closed")
        chunks.extend(chunk)
    return bytes(chunks)


def read_varint(sock: socket.socket) -> int:
    multiplier = 1
    value = 0
    for _ in range(4):
        digit = read_exact(sock, 1)[0]
        value += (digit & 127) * multiplier
        if (digit & 128) == 0:
            return value
        multiplier *= 128
    raise ValueError("malformed MQTT remaining length")


def encode_string(value: str) -> bytes:
    raw = value.encode("utf-8")
    return struct.pack("!H", len(raw)) + raw


def decode_string(data: bytes, offset: int = 0) -> tuple[str, int]:
    size = struct.unpack("!H", data[offset : offset + 2])[0]
    start = offset + 2
    end = start + size
    return data[start:end].decode("utf-8"), end


def make_packet(packet_type: int, payload: bytes = b"", flags: int = 0) -> bytes:
    return bytes([(packet_type << 4) | flags]) + encode_varint(len(payload)) + payload


def read_packet(sock: socket.socket) -> tuple[int, int, bytes]:
    first = read_exact(sock, 1)[0]
    packet_type = first >> 4
    flags = first & 0x0F
    remaining = read_varint(sock)
    return packet_type, flags, read_exact(sock, remaining)


def topic_matches(topic_filter: str, topic: str) -> bool:
    if topic_filter == "#":
        return True
    f_parts = topic_filter.split("/")
    t_parts = topic.split("/")
    for index, part in enumerate(f_parts):
        if part == "#":
            return index == len(f_parts) - 1
        if index >= len(t_parts):
            return False
        if part != "+" and part != t_parts[index]:
            return False
    return len(f_parts) == len(t_parts)


class BrokerState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.subscriptions: list[tuple[str, "BrokerHandler"]] = []

    def subscribe(self, topic_filter: str, handler: "BrokerHandler") -> None:
        with self.lock:
            self.subscriptions = [
                item for item in self.subscriptions if not (item[0] == topic_filter and item[1] is handler)
            ]
            self.subscriptions.append((topic_filter, handler))

    def unsubscribe_handler(self, handler: "BrokerHandler") -> None:
        with self.lock:
            self.subscriptions = [item for item in self.subscriptions if item[1] is not handler]

    def publish(self, topic: str, payload: bytes) -> None:
        with self.lock:
            targets = [handler for topic_filter, handler in self.subscriptions if topic_matches(topic_filter, topic)]
        for handler in targets:
            handler.send_publish(topic, payload)


class BrokerHandler(socketserver.BaseRequestHandler):
    server: "MqttBroker"

    def setup(self) -> None:
        self.send_lock = threading.Lock()
        self.client_id = "unknown"

    def handle(self) -> None:
        try:
            while True:
                packet_type, flags, payload = read_packet(self.request)
                if packet_type == CONNECT:
                    self._handle_connect(payload)
                elif packet_type == PUBLISH:
                    topic, offset = decode_string(payload)
                    self.server.state.publish(topic, payload[offset:])
                elif packet_type == SUBSCRIBE:
                    self._handle_subscribe(payload)
                elif packet_type == PINGREQ:
                    self._send(make_packet(PINGRESP))
                elif packet_type == DISCONNECT:
                    break
                else:
                    raise ValueError(f"unsupported packet type {packet_type}")
        except (EOFError, OSError, ValueError):
            pass
        finally:
            self.server.state.unsubscribe_handler(self)

    def _send(self, packet: bytes) -> None:
        with self.send_lock:
            self.request.sendall(packet)

    def _handle_connect(self, payload: bytes) -> None:
        protocol, offset = decode_string(payload)
        if protocol != "MQTT" or payload[offset] != 4:
            raise ValueError("only MQTT 3.1.1 is supported")
        offset += 4
        self.client_id, _ = decode_string(payload, offset)
        self._send(make_packet(CONNACK, b"\x00\x00"))

    def _handle_subscribe(self, payload: bytes) -> None:
        packet_id = payload[:2]
        offset = 2
        granted = bytearray()
        while offset < len(payload):
            topic_filter, offset = decode_string(payload, offset)
            offset += 1
            self.server.state.subscribe(topic_filter, self)
            granted.append(0)
        self._send(make_packet(SUBACK, packet_id + bytes(granted)))

    def send_publish(self, topic: str, payload: bytes) -> None:
        try:
            self._send(make_packet(PUBLISH, encode_string(topic) + payload))
        except OSError:
            self.server.state.unsubscribe_handler(self)


class MqttBroker(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address: tuple[str, int]) -> None:
        self.state = BrokerState()
        super().__init__(server_address, BrokerHandler)


class MqttClient:
    def __init__(self, host: str, port: int, client_id: str) -> None:
        self.host = host
        self.port = port
        self.client_id = client_id
        self.sock: socket.socket | None = None
        self.send_lock = threading.Lock()
        self.callbacks: list[tuple[str, Callable[[str, bytes], None]]] = []
        self._closed = threading.Event()
        self._reader: threading.Thread | None = None
        self._packet_id = 0

    def connect(self, retries: int = 40, delay: float = 0.1) -> None:
        last_error: OSError | None = None
        for _ in range(retries):
            try:
                sock = socket.create_connection((self.host, self.port), timeout=3)
                self.sock = sock
                variable = encode_string("MQTT") + b"\x04\x02" + struct.pack("!H", 30)
                self._send(make_packet(CONNECT, variable + encode_string(self.client_id)))
                packet_type, _flags, payload = read_packet(sock)
                if packet_type != CONNACK or payload != b"\x00\x00":
                    raise RuntimeError("MQTT broker rejected connection")
                return
            except OSError as exc:
                last_error = exc
                time.sleep(delay)
        raise RuntimeError(f"could not connect to MQTT broker: {last_error}")

    def start(self) -> None:
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()

    def subscribe(self, topic_filter: str, callback: Callable[[str, bytes], None]) -> None:
        self.callbacks.append((topic_filter, callback))
        self._packet_id = (self._packet_id % 65535) + 1
        payload = struct.pack("!H", self._packet_id) + encode_string(topic_filter) + b"\x00"
        self._send(make_packet(SUBSCRIBE, payload, flags=2))

    def publish(self, topic: str, payload: bytes | str) -> None:
        if isinstance(payload, str):
            payload = payload.encode("utf-8")
        self._send(make_packet(PUBLISH, encode_string(topic) + payload))

    def close(self) -> None:
        self._closed.set()
        try:
            self._send(make_packet(DISCONNECT))
        except Exception:
            pass
        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass

    def _send(self, packet: bytes) -> None:
        if self.sock is None:
            raise RuntimeError("MQTT client is not connected")
        with self.send_lock:
            self.sock.sendall(packet)

    def _read_loop(self) -> None:
        assert self.sock is not None
        while not self._closed.is_set():
            try:
                packet_type, _flags, payload = read_packet(self.sock)
            except (EOFError, OSError):
                return
            if packet_type == PUBLISH:
                topic, offset = decode_string(payload)
                message = payload[offset:]
                for topic_filter, callback in list(self.callbacks):
                    if topic_matches(topic_filter, topic):
                        callback(topic, message)


def run_broker(host: str, port: int) -> None:
    server = MqttBroker((host, port))
    print(f"MQTT broker listening on {host}:{port}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.shutdown()
        server.server_close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Tiny MQTT broker/client helpers for the urisys example.")
    sub = parser.add_subparsers(dest="command", required=True)
    broker = sub.add_parser("broker")
    broker.add_argument("--host", default="127.0.0.1")
    broker.add_argument("--port", type=int, default=18883)
    args = parser.parse_args()
    if args.command == "broker":
        run_broker(args.host, args.port)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
