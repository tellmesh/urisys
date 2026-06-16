from __future__ import annotations

import pytest

from urisys.controllers.uri_controller import UriController
from urisys.controllers.flow_controller import FlowController
from urisys.managers.pack_manager import PackManager


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


def test_all_skips_uninstalled_packs(tmp_path):
    """`--packs all` must degrade gracefully when optional uri* packs are not
    installed, loading whatever is available instead of crashing."""
    with PackManager(packs="all") as pm:
        with pytest.warns(UserWarning, match="not installed"):
            registry = pm.create_registry()
    schemes = {route.scheme for route in registry.routes}
    assert "browser" in schemes
    assert "docker" in schemes


def test_explicit_missing_pack_raises_helpful_error():
    """A pack named explicitly (not via `all`) must fail loudly with guidance."""
    with PackManager(packs="desktop") as pm:
        with pytest.raises(ModuleNotFoundError, match="pip install uridesktop"):
            pm.create_registry()
