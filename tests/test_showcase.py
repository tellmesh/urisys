from __future__ import annotations

from pathlib import Path

from urisys.managers.markpact_flows import classify_flow, declared_uses, extract_flows, extract_protos
from urisys.managers.markpact_manager import MarkpactManager

ROOT = Path(__file__).resolve().parents[1]
SHOWCASE = ROOT.parent / "markpact-contracts" / "packs" / "uribrowser.showcase.markpact.md"


def test_showcase_validates():
    info = MarkpactManager().validate(SHOWCASE)
    assert info["ok"] is True
    assert info["kind"] == "pack"
    assert info["scheme"] == "browser"


def test_analyze_classifies_use_case_and_integration():
    report = MarkpactManager().analyze(SHOWCASE)
    assert report["ok"] is True
    assert report["scheme"] == "browser"
    assert report["use_cases"] == ["open-and-read"]
    assert report["integrations"] == ["install-and-verify"]
    assert set(report["declared_uses"]) == {"env", "kvm", "shell"}
    assert report["undeclared_uses"] == []
    assert "browser/v1/browser.proto" in report["protos"]


def test_compile_extracts_flows_and_protos(tmp_path):
    compiled = MarkpactManager(cache_root=tmp_path / "cache").compile(SHOWCASE)
    assert set(compiled.flow_ids) == {"open-and-read", "install-and-verify"}
    assert compiled.flows_dir and compiled.flows_dir.exists()
    assert (compiled.flows_dir / "open_and_read.uri.flow.yaml").exists()
    assert compiled.proto_dir and (compiled.proto_dir / "browser/v1/browser.proto").exists()
    assert "browser/v1/browser.proto" in compiled.proto_files


def test_classify_flow_reports_undeclared_uses():
    flow = {"do": ["browser://x/page/open", "kvm://local/task/command/click-text"]}
    info = classify_flow(flow, pack_scheme="browser", declared_uses=set())
    assert info["kind"] == "integration"
    assert info["undeclared_uses"] == ["kvm"]

    info_ok = classify_flow(flow, pack_scheme="browser", declared_uses={"kvm"})
    assert info_ok["undeclared_uses"] == []


def test_declared_uses_strips_scheme_suffix():
    assert declared_uses({"uses": ["shell://", "kvm://", "env"]}) == {"shell", "kvm", "env"}
