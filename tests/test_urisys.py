from __future__ import annotations

from urisys.controllers.uri_controller import UriController
from urisys.controllers.flow_controller import FlowController


def test_call_browser_open(tmp_path):
    ctrl = UriController(packs="browser", events_path=str(tmp_path / "events.jsonl"))
    try:
        result = ctrl.call("browser://default/page/open", {"url": "https://example.com"}, approved=True)
        assert result["ok"] is True
        assert result["operation"] == "open_page"
    finally:
        ctrl.close()


def test_routes_load(tmp_path):
    ctrl = UriController(packs="browser,docker", events_path=str(tmp_path / "events.jsonl"))
    try:
        routes = ctrl.routes()
        assert any(route["scheme"] == "browser" for route in routes)
        assert any(route["scheme"] == "docker" for route in routes)
    finally:
        ctrl.close()
