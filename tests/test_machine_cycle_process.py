"""UriProcess: machine-cycle — process glue over existing URI packs."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from urisys.managers.markpact_manager import MarkpactManager
from urisys.managers.markpact_run import run_markpact

TELLMESH = Path(__file__).resolve().parents[2]
PROCESS_MARKPACT = TELLMESH / "markpact-contracts" / "packs" / "machine-cycle-process.markpact.md"


@pytest.mark.skipif(not PROCESS_MARKPACT.is_file(), reason="machine-cycle process markpact missing")
def test_machine_cycle_process_validates_and_analyzes():
    mgr = MarkpactManager()
    info = mgr.validate(PROCESS_MARKPACT)
    assert info["ok"] is True
    assert info["scheme"] == "process"

    analysis = mgr.analyze(PROCESS_MARKPACT)
    assert analysis["ok"] is True
    assert "machine-cycle" in analysis["integrations"]
    assert analysis["declared_uses"] == ["screen", "stepper", "tts"]
    assert analysis["profile"]["uses_packs"] == ["uristepper", "uriscreen", "uristt-tts"]


@pytest.mark.skipif(not PROCESS_MARKPACT.is_file(), reason="machine-cycle process markpact missing")
def test_machine_cycle_compiles_urisys_flow_handler(tmp_path):
    compiled = MarkpactManager(cache_root=tmp_path / ".markpact").compile(PROCESS_MARKPACT, force=True)
    manifest = yaml.safe_load(compiled.manifest_path.read_text(encoding="utf-8"))

    assert manifest["handlers"]["urisys"]["machine_cycle.run"] == "urisys://flow/machine-cycle"
    assert manifest["uri_patterns"][0]["operation"] == "machine_cycle.run"
    assert "machine-cycle" in manifest["urisys"]["flows"]
    assert (compiled.flows_dir / "machine_cycle.uri.flow.yaml").is_file()


@pytest.mark.skipif(not PROCESS_MARKPACT.is_file(), reason="machine-cycle process markpact missing")
def test_machine_cycle_requires_approval_without_deps(tmp_path):
    compiled = MarkpactManager(cache_root=tmp_path / ".markpact").compile(PROCESS_MARKPACT, force=True)

    from uri_control.edge.manifest import register_manifest_file
    from uri_control.edge.runtime import Runtime

    rt = Runtime(events_path=str(tmp_path / "events.jsonl"), config={})
    register_manifest_file(rt, compiled.manifest_path)

    denied = rt.call("process://machine-cycle/command/run", {}, {"approved": False, "dry_run": True})
    assert denied["ok"] is False


@pytest.mark.skipif(not PROCESS_MARKPACT.is_file(), reason="machine-cycle process markpact missing")
def test_machine_cycle_embedded_markpact_test_policy_only(tmp_path):
    result = MarkpactManager(cache_root=tmp_path / ".markpact").run_tests(
        PROCESS_MARKPACT,
        events_path=tmp_path / "test-events.jsonl",
    )
    assert result["ok"] is True
    assert len(result["tests"]) == 2
    assert result["tests"][0]["id"] == "machine_cycle.requires_approval"


@pytest.mark.skipif(
    not PROCESS_MARKPACT.is_file() or not os.environ.get("TELLMESH_ROOT"),
    reason="needs TELLMESH_ROOT and sibling uri* packs",
)
def test_machine_cycle_flow_dry_run_with_tellmesh(tmp_path, monkeypatch):
    monkeypatch.setenv("TELLMESH_ROOT", os.environ["TELLMESH_ROOT"])
    result = run_markpact(
        PROCESS_MARKPACT,
        mode="flow",
        out=tmp_path / ".markpact",
        approve=True,
        dry_run=True,
    )
    assert result["ok"] is True
    assert result["flows"][0]["id"] == "machine-cycle"
    passed = [r for r in result["flows"][0].get("results", []) if r.get("type") == "expect_passed"]
    assert passed, "machine-cycle flow should pass expect block"
