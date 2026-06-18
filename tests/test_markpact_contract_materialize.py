"""Contract → pack → ``.markpact/`` → uricore runtime (uri_control / urisysedge)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from pack_import_isolation import reset_embedded_pack_imports
from urisys.managers import contract_gen
from urisys.managers.markpact_manager import MarkpactManager
from urisys.managers.markpact_materialize import materialize_markpact
from urisys.managers.markpact_pack_gen import generate_pack_markpact
from urisys.managers.markpact_run import run_markpact

TELLMESH = Path(__file__).resolve().parents[2]
URIKVM_MANIFEST = TELLMESH / "urikvm" / "urikvm" / "manifest.yaml"
URIKVM_CONTRACT = TELLMESH / "markpact-contracts" / "packs" / "urikvm.contract.markpact.md"
URIKVM_THIN = TELLMESH / "urikvm" / "markpacts" / "urikvm.markpact.md"


@pytest.mark.skipif(not URIKVM_MANIFEST.is_file(), reason="urikvm manifest missing")
def test_gen_contract_matches_manifest_no_drift():
    manifest = contract_gen.load_manifest(URIKVM_MANIFEST)
    contract = contract_gen.manifest_to_contract(manifest)
    assert contract_gen.diff_manifest_contract(manifest, contract) == []

    if URIKVM_CONTRACT.is_file():
        on_disk = contract_gen.load_contract_block(URIKVM_CONTRACT)
        assert contract_gen.diff_manifest_contract(manifest, on_disk) == []


@pytest.mark.skipif(not URIKVM_CONTRACT.is_file(), reason="urikvm contract missing")
def test_contract_validates_but_does_not_compile():
    info = MarkpactManager().validate(URIKVM_CONTRACT)
    assert info["ok"] is True
    assert info["kind"] == "contract"

    with pytest.raises(Exception, match="markpact:pack"):
        MarkpactManager(cache_root="/tmp/markpact-contract-compile").compile(URIKVM_CONTRACT)


@pytest.mark.skipif(not URIKVM_THIN.is_file(), reason="thin urikvm markpact missing")
def test_thin_pack_materializes_to_markpact_tree(tmp_path, monkeypatch):
    monkeypatch.setenv("TELLMESH_ROOT", str(TELLMESH))
    result = materialize_markpact(URIKVM_THIN, root=tmp_path / ".markpact", force=True)
    dest = Path(result["materialized"]["materialized_dir"])
    assert (dest / "manifest.yaml").is_file()
    assert (dest / "materialize.json").is_file()
    assert result["materialized"]["flow_ids"]


@pytest.mark.skipif(not URIKVM_THIN.is_file(), reason="thin urikvm markpact missing")
def test_thin_pack_routes_via_tellmesh_and_uricore(tmp_path, monkeypatch):
    monkeypatch.setenv("TELLMESH_ROOT", str(TELLMESH))
    from urisys.managers.markpact_pack_deps import extend_tellmesh_paths
    from uri_control.edge.manifest import register_manifest_file
    from uri_control.edge.runtime import Runtime

    try:
        extend_tellmesh_paths(anchor=URIKVM_THIN)
        import urikvm  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("urikvm sibling not available")

    mat = materialize_markpact(URIKVM_THIN, root=tmp_path / ".markpact", force=True)
    manifest = Path(mat["materialized"]["manifest_path"])
    rt = Runtime(events_path=str(tmp_path / "events.jsonl"), config={})
    register_manifest_file(rt, manifest)
    res = rt.call("kvm://local/monitor/query/list", {}, {"dry_run": True})
    assert res["ok"] is True
    assert "monitors" in res["result"]


@pytest.mark.skipif(not URIKVM_MANIFEST.is_file(), reason="urikvm manifest missing")
def test_full_pack_embedded_source_runs_without_tellmesh(tmp_path):
    """``urisys markpact pack`` embeds handlers; runtime needs only uricore + unpack dir."""
    text = generate_pack_markpact(URIKVM_MANIFEST.parent, repo_root=TELLMESH)
    src = tmp_path / "urikvm.full.markpact.md"
    src.write_text(text, encoding="utf-8")

    assert "markpact:module path=urikvm/handlers.py" in text
    info = MarkpactManager().validate(src)
    assert info["ok"] is True
    assert info["capabilities"] == 5

    result = run_markpact(src, mode="pack", out=tmp_path / ".markpact")
    assert result["ok"] is True
    assert len(result["routes"]) == 5

    compiled = MarkpactManager(cache_root=tmp_path / ".markpact").compile(src, force=True)
    for name in [m for m in list(sys.modules) if m == "urikvm" or m.startswith("urikvm.")]:
        del sys.modules[name]
    sys.path.insert(0, str(compiled.cache_dir))

    from uri_control.edge.manifest import register_manifest_file
    from uri_control.edge.runtime import Runtime

    rt = Runtime(events_path=str(tmp_path / "ev.jsonl"), config={})
    register_manifest_file(rt, compiled.manifest_path)
    res = rt.call("kvm://local/monitor/query/list", {}, {"dry_run": True})
    assert res["ok"] is True
    assert res["result"]["driver"] == "mock"
    reset_embedded_pack_imports()
