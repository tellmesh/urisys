from __future__ import annotations

from pathlib import Path

from urisys.controllers.uri_controller import UriController
from urisys.managers.markpact_manager import MarkpactManager

ROOT = Path(__file__).resolve().parents[1]
BROWSER_MARKPACT = ROOT / "markpacts" / "packs" / "uribrowser.markpact.md"
SYSTEMD_MARKPACT = ROOT / "markpacts" / "packs" / "urisystemd.markpact.md"


def test_markpact_validate():
    info = MarkpactManager().validate(BROWSER_MARKPACT)
    assert info["ok"] is True
    assert info["kind"] == "pack"
    assert info["scheme"] == "browser"
    assert info["capabilities"] >= 2


def test_markpact_validate_contract():
    path = ROOT / "urirdp-docker" / "markpacts" / "urikvm.contract.markpact.md"
    info = MarkpactManager().validate(path)
    assert info["ok"] is True
    assert info["kind"] == "contract"
    assert info["scheme"] == "kvm"
    assert info["capabilities"] >= 2


def test_markpact_validate_implementation():
    path = ROOT / "urienv-docker" / "markpacts" / "urienv-python.markpact.md"
    info = MarkpactManager().validate(path)
    assert info["ok"] is True
    assert info["kind"] == "implementation"
    assert info["implements"] == "urienv.contract"


def test_markpact_validate_bundle():
    path = ROOT / "urirdp-docker" / "markpacts" / "urikvm-rdp.contract.markpact.md"
    info = MarkpactManager().validate(path)
    assert info["ok"] is True
    assert info["kind"] == "bundle"


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


def test_build_route_shape():
    """Guards the extracted _build_route: a markpact:// handler becomes a python://
    ref registered in handlers, and command kind defaults approval to required."""
    manager = MarkpactManager()
    handlers: dict[str, str] = {}
    route = manager._build_route(
        {"pattern": "browser://{s}/page/open", "operation": "open_page",
         "handler": "markpact://open_page", "kind": "command"},
        package_id="uribrowser", scheme="browser", module_name="mod", handlers=handlers,
    )
    assert route["pattern"] == "browser://{s}/page/open"
    assert route["kind"] == "command"
    assert route["approval"] == "required"
    assert route["side_effects"] is True
    assert route["handler"] == "python://mod.open_page:handle"
    assert handlers["open_page"] == "python://mod.open_page:handle"
