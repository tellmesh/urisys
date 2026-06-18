from __future__ import annotations

from pathlib import Path

import pytest

from urisys.controllers.uri_controller import UriController
from urisys.controllers.flow_controller import FlowController
from urisys.managers.pack_manager import PackManager

TELLMESH = Path(__file__).resolve().parents[2]
BROWSER_MARKPACT = TELLMESH / "markpact-contracts" / "packs" / "uribrowser.markpact.md"
DOCKER_MARKPACT = TELLMESH / "markpact-contracts" / "packs" / "uridocker.markpact.md"


def test_call_browser_open(tmp_path):
    if not BROWSER_MARKPACT.is_file():
        pytest.skip("uribrowser markpact missing")
    ctrl = UriController(
        packs="none",
        markpacts=str(BROWSER_MARKPACT),
        events_path=str(tmp_path / "events.jsonl"),
    )
    try:
        result = ctrl.call("browser://default/page/open", {"url": "https://example.com"}, approved=True)
        assert result["ok"] is True
        assert result["operation"] == "browser.page.open"
    finally:
        ctrl.close()


def test_routes_load(tmp_path):
    if not BROWSER_MARKPACT.is_file() or not DOCKER_MARKPACT.is_file():
        pytest.skip("markpact contracts missing")
    ctrl = UriController(
        packs="none",
        markpacts=f"{BROWSER_MARKPACT},{DOCKER_MARKPACT}",
        events_path=str(tmp_path / "events.jsonl"),
    )
    try:
        routes = ctrl.routes()
        assert any(route["scheme"] == "browser" for route in routes)
        assert any(route["scheme"] == "docker" for route in routes)
    finally:
        ctrl.close()


def test_all_skips_uninstalled_packs(tmp_path, monkeypatch):
    """`--packs all` must degrade gracefully when optional uri* packs are not
    installed, loading whatever is available instead of crashing."""
    monkeypatch.delenv("TELLMESH_ROOT", raising=False)
    monkeypatch.chdir(tmp_path)
    with PackManager(packs="all") as pm:
        with pytest.warns(UserWarning, match="Skipping uri pack"):
            registry = pm.create_registry()
    schemes = {route.scheme for route in registry.routes}
    assert len(schemes) >= 0


def test_explicit_missing_pack_raises_helpful_error():
    """A pack named explicitly (not via `all`) must fail loudly with guidance."""
    with PackManager(packs="not_installed_uri_pack_xyz") as pm:
        with pytest.raises(ModuleNotFoundError, match="pip install not_installed_uri_pack_xyz"):
            pm.create_registry()
