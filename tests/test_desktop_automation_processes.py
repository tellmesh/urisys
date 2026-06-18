"""UriProcess: desktop-automation-processes — conformance with v1alpha profile."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from urisys.managers.markpact_manager import MarkpactManager
from urisys.managers.markpact_run import run_markpact

TELLMESH = Path(__file__).resolve().parents[2]
PROCESS_MARKPACT = TELLMESH / "markpact-contracts" / "packs" / "desktop-automation-processes.markpact.md"
RESOLVER = TELLMESH / "markpact-contracts" / "packs" / "examples" / "urisys.runtime.resolver.yaml"


@pytest.mark.skipif(not PROCESS_MARKPACT.is_file(), reason="desktop automation markpact missing")
def test_desktop_automation_validates_and_analyzes():
    mgr = MarkpactManager()
    info = mgr.validate(PROCESS_MARKPACT)
    assert info["ok"] is True
    assert info["scheme"] == "process"

    analysis = mgr.analyze(PROCESS_MARKPACT)
    assert analysis["ok"] is True
    assert len(analysis["integrations"]) == 4
    assert analysis["profile"]["requires"]["schemes"]


@pytest.mark.skipif(not PROCESS_MARKPACT.is_file(), reason="desktop automation markpact missing")
def test_desktop_automation_embedded_approval_test(tmp_path):
    result = MarkpactManager(cache_root=tmp_path / ".markpact").run_tests(
        PROCESS_MARKPACT,
        events_path=tmp_path / "test-events.jsonl",
    )
    assert result["ok"] is True
    assert result["tests"][0]["id"] == "process.install_update_verify_browser.requires_approval"


@pytest.mark.skipif(
    not PROCESS_MARKPACT.is_file() or not os.environ.get("TELLMESH_ROOT"),
    reason="needs TELLMESH_ROOT",
)
def test_desktop_gui_flow_dry_run(tmp_path, monkeypatch):
    monkeypatch.setenv("TELLMESH_ROOT", os.environ["TELLMESH_ROOT"])
    result = run_markpact(
        PROCESS_MARKPACT,
        mode="flow",
        out=tmp_path / ".markpact",
        approve=True,
        dry_run=True,
        flow_id="gui-open-software-center",
    )
    assert result["ok"] is True


@pytest.mark.skipif(
    not PROCESS_MARKPACT.is_file()
    or not os.environ.get("TELLMESH_ROOT")
    or not RESOLVER.is_file(),
    reason="needs TELLMESH_ROOT and resolver yaml",
)
def test_desktop_install_flow_dry_run_with_resolver(tmp_path, monkeypatch):
    monkeypatch.setenv("TELLMESH_ROOT", os.environ["TELLMESH_ROOT"])
    monkeypatch.setenv("URISYS_RESOLVER_CONFIG", str(RESOLVER))
    result = run_markpact(
        PROCESS_MARKPACT,
        mode="flow",
        out=tmp_path / ".markpact",
        approve=True,
        dry_run=True,
        flow_id="install-update-verify-browser",
    )
    assert result["ok"] is True
