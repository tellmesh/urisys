from __future__ import annotations

from pathlib import Path

import pytest

from urisys.managers.markpact_manager import MarkpactManager
from urisys.managers.markpact_run_flow import (
    flow_path_for,
    pick_flow_id,
    run_markpact_flow,
    split_flow_ref,
)

ROOT = Path(__file__).resolve().parents[1]
TELLMESH = ROOT.parent
SHOWCASE = TELLMESH / "markpact-contracts" / "packs" / "uribrowser.showcase.markpact.md"


def test_split_flow_ref():
    assert split_flow_ref("pack.md") == ("pack.md", None)
    assert split_flow_ref("pack.md#open-and-read") == ("pack.md", "open-and-read")


def test_pick_flow_id_requires_fragment_when_many(tmp_path):
    manager = MarkpactManager(cache_root=tmp_path / "cache")
    compiled = manager.compile(SHOWCASE)
    with pytest.raises(Exception, match="Multiple embedded flows"):
        pick_flow_id(compiled, None)


def test_compile_cache_hit_preserves_flow_ids(tmp_path):
    manager = MarkpactManager(cache_root=tmp_path / "cache")
    first = manager.compile(SHOWCASE, force=True)
    assert first.flow_ids
    second = manager.compile(SHOWCASE, force=False)
    assert second.flow_ids == first.flow_ids
    assert second.flows_dir == first.flows_dir


def test_run_flow_use_case(tmp_path):
    report = run_markpact_flow(
        SHOWCASE,
        flow_id="open-and-read",
        out_dir=tmp_path / "cache",
        events_path=tmp_path / "events.jsonl",
        approved=True,
        dry_run=True,
    )
    assert report["ok"] is True
    assert report["flow_id"] == "open-and-read"
    assert len(report["results"]) == 2
    assert all(r.get("ok") for r in report["results"])
    assert report["uses"] == []


def test_run_flow_via_fragment(tmp_path):
    report = run_markpact_flow(
        f"{SHOWCASE}#open-and-read",
        out_dir=tmp_path / "cache",
        events_path=tmp_path / "events.jsonl",
        approved=True,
        dry_run=True,
    )
    assert report["ok"] is True
    assert report["flow_id"] == "open-and-read"


def test_flow_path_for(tmp_path):
    compiled = MarkpactManager(cache_root=tmp_path / "cache").compile(SHOWCASE)
    path = flow_path_for(compiled, "install-and-verify")
    assert path.name == "install_and_verify.uri.flow.yaml"
    assert path.is_file()


@pytest.mark.skipif(not SHOWCASE.is_file(), reason="showcase markpact missing")
def test_run_integration_flow_local_siblings(tmp_path, monkeypatch):
    monkeypatch.setenv("TELLMESH_ROOT", str(TELLMESH))
    from urisys.managers.markpact_pack_deps import extend_tellmesh_paths

    try:
        extend_tellmesh_paths(anchor=SHOWCASE)
        import urienv  # noqa: F401
        import urikvm  # noqa: F401
        import urishell  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("tellmesh sibling packs not available")

    report = run_markpact_flow(
        SHOWCASE,
        flow_id="install-and-verify",
        out_dir=tmp_path / "cache",
        events_path=tmp_path / "events.jsonl",
        approved=True,
        dry_run=True,
    )
    assert report["uses"] == ["env", "kvm", "shell"]
    assert report["ok"] is True
    assert len(report["results"]) == 4
