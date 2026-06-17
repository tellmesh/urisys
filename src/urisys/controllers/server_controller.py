from __future__ import annotations

from ..http_server import create_server
from ..defaults import DEFAULT_EVENTS_PATH


class ServerController:
    def __init__(self, *, host="127.0.0.1", port=8789, packs="all", markpacts=None, events_path=DEFAULT_EVENTS_PATH) -> None:
        self.host = host
        self.port = port
        self.packs = packs
        self.markpacts = markpacts
        self.events_path = events_path
        self.server = create_server(host, port, packs=packs, markpacts=markpacts, events_path=events_path)

    def serve_forever(self) -> None:
        print(f"urisys server listening on http://{self.host}:{self.port}")
        print("endpoints: GET /health, GET /uri/routes, GET /uri/events, POST /uri/call, POST /uri/explain")
        self.server.serve_forever()
