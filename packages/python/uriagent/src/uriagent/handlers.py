from __future__ import annotations

from typing import Any
from urllib import request
import json

from .common import mock_result, safe_mode, var


def health(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return mock_result("agent.health", context, name=var(context, "name", "default"), status="healthy")


def call(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Call another URI server when endpoint is provided and real mode is enabled.

    Expected payload:
      {"endpoint": "http://127.0.0.1:8080/uri/call", "uri": "...", "payload": {...}}
    """
    endpoint = payload.get("endpoint")
    target_uri = payload.get("uri")
    if not endpoint or not target_uri or safe_mode(context):
        return mock_result("agent.call", context, name=var(context, "name"), endpoint=endpoint, target_uri=target_uri, forwarded=False)

    body = json.dumps({"uri": target_uri, "payload": payload.get("payload") or {}, "context": payload.get("context") or {}}).encode("utf-8")
    req = request.Request(str(endpoint), data=body, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=int(payload.get("timeout") or 10)) as response:  # nosec - user-controlled explicit endpoint
        return json.loads(response.read().decode("utf-8"))


def start(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return mock_result("agent.start", context, name=var(context, "name"), started=True)


def stop(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return mock_result("agent.stop", context, name=var(context, "name"), stopped=True)
