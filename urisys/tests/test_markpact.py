from __future__ import annotations

from pathlib import Path

from urisys.controllers.uri_controller import UriController
from urisys.managers.markpact_manager import MarkpactManager

ROOT = Path(__file__).resolve().parents[2]
BROWSER_MARKPACT = ROOT / "urisys" / "markpacts" / "packs" / "uribrowser.markpact.md"
SYSTEMD_MARKPACT = ROOT / "urisys" / "markpacts" / "packs" / "urisystemd.markpact.md"


def test_markpact_validate():
    info = MarkpactManager().validate(BROWSER_MARKPACT)
    assert info["ok"] is True
    assert info["scheme"] == "browser"
    assert info["capabilities"] >= 2


def test_markpact_compile_and_call(tmp_path):
    manager = MarkpactManager(cache_root=tmp_path / "cache")
    compiled = manager.compile(BROWSER_MARKPACT)
    assert compiled.manifest_path.exists()

    ctrl = UriController(packs=str(compiled.manifest_path), events_path=str(tmp_path / "events.jsonl"))
    try:
        result = ctrl.call(
            "browser://default/page/open",
            {"url": "https://example.com"},
            approved=True,
            dry_run=True,
            environment="mock",
        )
        assert result["ok"] is True
        assert result["operation"] == "open_page"
        assert result["result"]["url"] == "https://example.com"
    finally:
        ctrl.close()


def test_uri_controller_loads_markpact_directly(tmp_path):
    ctrl = UriController(packs="none", markpacts=[str(SYSTEMD_MARKPACT)], events_path=str(tmp_path / "events.jsonl"))
    try:
        result = ctrl.call("systemd://unit/docker.service/query/status")
        assert result["ok"] is True
        assert result["operation"] == "status"
        assert result["result"]["unit"] == "docker.service"
    finally:
        ctrl.close()


def test_markpact_embedded_tests(tmp_path):
    report = MarkpactManager(cache_root=tmp_path / "cache").run_tests(BROWSER_MARKPACT, events_path=tmp_path / "events.jsonl")
    assert report["ok"] is True
    assert len(report["tests"]) == 2
