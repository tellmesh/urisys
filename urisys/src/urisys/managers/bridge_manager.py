from __future__ import annotations

import json
from urllib import request


class BridgeManager:
    """Forwards URI envelopes to another URI server."""

    def call_http(self, endpoint: str, uri: str, payload=None, context=None, timeout=15) -> dict:
        body = json.dumps({"uri": uri, "payload": payload or {}, "context": context or {}}).encode("utf-8")
        req = request.Request(endpoint, data=body, headers={"Content-Type": "application/json"}, method="POST")
        with request.urlopen(req, timeout=timeout) as response:  # explicit endpoint selected by caller
            return json.loads(response.read().decode("utf-8"))
