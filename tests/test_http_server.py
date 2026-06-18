"""Characterization tests for the urisys HTTP server after it was migrated onto
the shared ``uri_control.edge.http`` transport. Locks the wire contract that browser
and CLI clients rely on (CORS, exact /health shape, full route dicts)."""

import json
import os
import tempfile
import threading
import urllib.request

from urisys.http_server import create_server


def _start():
    events_path = os.path.join(tempfile.mkdtemp(), "ev.jsonl")
    server = create_server("127.0.0.1", 0, events_path=events_path)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, port


def _get(port, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}") as r:
        return r.status, dict(r.headers), json.loads(r.read())


def test_health_exact_shape_and_cors():
    server, port = _start()
    try:
        status, headers, body = _get(port, "/health")
        assert status == 200
        # exact urisys shape — no edge "runtime" key leaking in
        assert body == {"ok": True, "service": "urisys"}
        assert headers.get("Access-Control-Allow-Origin") == "*"
    finally:
        server.shutdown()


def test_routes_are_full_dicts_not_flattened():
    server, port = _start()
    try:
        _, _, body = _get(port, "/uri/routes")
        assert body["ok"] is True
        assert isinstance(body["routes"], list)
        # urisys returns rich route dicts, not bare pattern strings
        if body["routes"]:
            assert isinstance(body["routes"][0], dict)
    finally:
        server.shutdown()


def test_options_preflight_204():
    server, port = _start()
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/uri/call", method="OPTIONS")
        with urllib.request.urlopen(req) as r:
            assert r.status == 204
    finally:
        server.shutdown()


def test_events_endpoint():
    server, port = _start()
    try:
        _, _, body = _get(port, "/uri/events")
        assert body["ok"] is True and "events" in body
    finally:
        server.shutdown()
