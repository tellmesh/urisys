from __future__ import annotations

from pathlib import Path

from urisys.managers import contract_gen
from urisys.managers.markpact_manager import MarkpactManager

ROOT = Path(__file__).resolve().parents[1]
TELLMESH = ROOT.parent
STEPPER_MANIFEST = TELLMESH / "uristepper" / "uristepper" / "manifest.yaml"


def test_manifest_to_contract_maps_kinds_and_approval():
    manifest = contract_gen.load_manifest(STEPPER_MANIFEST)
    contract = contract_gen.manifest_to_contract(manifest)

    assert contract["kind"] == "UriContract"
    assert contract["scheme"] == "stepper"
    assert contract["metadata"]["id"] == "uristepper.contract"
    assert contract["metadata"]["version"] == "1.0.0"  # int 1 normalised to semver

    queries = {q["pattern"]: q for q in contract["queries"]}
    assert "stepper://{device}/axis/{axis}/query/status" in queries
    assert queries["stepper://{device}/axis/{axis}/query/status"]["id"] == "stepper.status"

    commands = {c["pattern"]: c for c in contract["commands"]}
    move = commands["stepper://{device}/axis/{axis}/command/move-relative"]
    assert move["id"] == "stepper.move_relative"
    assert move["side_effects"] is True
    assert move["requires_approval"] is True


def test_generated_contract_validates(tmp_path):
    manifest = contract_gen.load_manifest(STEPPER_MANIFEST)
    out = tmp_path / "uristepper.contract.markpact.md"
    out.write_text(contract_gen.render_contract_markpact(manifest), encoding="utf-8")

    info = MarkpactManager().validate(out)
    assert info["ok"] is True
    assert info["kind"] == "contract"
    assert info["scheme"] == "stepper"


def test_self_drift_is_clean():
    manifest = contract_gen.load_manifest(STEPPER_MANIFEST)
    contract = contract_gen.manifest_to_contract(manifest)
    assert contract_gen.diff_manifest_contract(manifest, contract) == []


def test_drift_detected():
    manifest = contract_gen.load_manifest(STEPPER_MANIFEST)
    contract = contract_gen.manifest_to_contract(manifest)
    contract["scheme"] = "step"
    contract["metadata"]["version"] = "2.0.0"
    contract["commands"][0]["requires_approval"] = False
    contract["commands"].pop()

    issues = contract_gen.diff_manifest_contract(manifest, contract)
    joined = "\n".join(issues)
    assert "scheme:" in joined
    assert "metadata.version:" in joined
    assert "requires_approval" in joined
    assert "missing in contract" in joined


def test_existing_repo_contract_has_no_core_drift():
    """The hand-written richer contract may add input/output schemas, but its core
    surface (patterns/ids/approval) must still agree with the manifest."""
    manifest = contract_gen.load_manifest(STEPPER_MANIFEST)
    contract = contract_gen.load_contract_block(
        TELLMESH / "uristepper" / "markpacts" / "uristepper.contract.markpact.md"
    )
    assert contract_gen.diff_manifest_contract(manifest, contract) == []
