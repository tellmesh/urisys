"""Release hot-load glue: pairing + signature gate, then resolve + forward.

Covers the verify_release gate primitive and the hotload_release_pack glue that
chains fetch_release -> verify -> run_release -> register_forward_pack. The live
parts (catalog HTTP, docker) are mocked; the gating and wiring are exercised for
real.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parents[1] / "packages" / "python"
sys.path.insert(0, str(PKG))

from urisysedge.runtime import Runtime  # noqa: E402
import urisysnode.artifact_resolver as artifact_resolver  # noqa: E402
import urisysnode.identity as identity  # noqa: E402
import urisysnode.release_verify as release_verify  # noqa: E402
from urisysnode.release_verify import canonical_digest, verify_release  # noqa: E402
from urisysnode.serve import hotload_release_pack  # noqa: E402


def _runtime(tmp_path) -> Runtime:
    rt = Runtime(events_path=str(tmp_path / "events.jsonl"))
    rt._loaded_packs = set()
    return rt


def _release(**extra):
    base = {
        "contract_id": "uristepper.contract",
        "version": "0.1.0",
        "artifact_index_url": "https://example/artifact-index.json",
        "scheme": "stepper",
        "patterns": ["stepper://{axis}/command/move", "stepper://{axis}/query/position"],
    }
    base.update(extra)
    return base


# ---- verify_release gate -------------------------------------------------


def test_canonical_digest_ignores_signature_block():
    a = _release()
    b = _release(signature={"keyid": "k", "alg": "ed25519", "sig": "zzz"})
    assert canonical_digest(a) == canonical_digest(b)


def test_disabled_policy_passes_through(monkeypatch):
    monkeypatch.delenv("URISYS_NODE_REQUIRE_SIGNATURE", raising=False)
    verdict = verify_release(_release())
    assert verdict["ok"] is True
    assert verdict["verified"] is False
    assert verdict["required"] is False


def test_required_but_unsigned_fails(monkeypatch):
    monkeypatch.setenv("URISYS_NODE_REQUIRE_SIGNATURE", "1")
    verdict = verify_release(_release())
    assert verdict["ok"] is False
    assert "unsigned" in verdict["error"]


def test_required_untrusted_key_fails(monkeypatch):
    monkeypatch.setenv("URISYS_NODE_REQUIRE_SIGNATURE", "1")
    rel = _release(signature={"keyid": "rogue", "alg": "ed25519", "sig": "AA=="})
    verdict = verify_release(rel, trusted_keys={"markpact-root": "ZmFrZQ=="})
    assert verdict["ok"] is False
    assert "untrusted signing key" in verdict["error"]


def test_required_no_crypto_backend_fails_closed(monkeypatch):
    monkeypatch.setenv("URISYS_NODE_REQUIRE_SIGNATURE", "1")

    def boom(*_a, **_k):
        raise RuntimeError("signature required but no crypto backend; pip install cryptography")

    monkeypatch.setattr(release_verify, "_ed25519_verify", boom)
    rel = _release(signature={"keyid": "markpact-root", "alg": "ed25519", "sig": "AA=="})
    verdict = verify_release(rel, trusted_keys={"markpact-root": "ZmFrZQ=="})
    assert verdict["ok"] is False
    assert "crypto backend" in verdict["error"]


def test_required_good_signature_verifies(monkeypatch):
    monkeypatch.setenv("URISYS_NODE_REQUIRE_SIGNATURE", "1")
    monkeypatch.setattr(release_verify, "_ed25519_verify", lambda *_a, **_k: True)
    rel = _release(signature={"keyid": "markpact-root", "alg": "ed25519", "sig": "AA=="})
    verdict = verify_release(rel, trusted_keys={"markpact-root": "ZmFrZQ=="})
    assert verdict["ok"] is True
    assert verdict["verified"] is True
    assert verdict["keyid"] == "markpact-root"


def test_required_mismatched_signature_fails(monkeypatch):
    monkeypatch.setenv("URISYS_NODE_REQUIRE_SIGNATURE", "1")
    monkeypatch.setattr(release_verify, "_ed25519_verify", lambda *_a, **_k: False)
    rel = _release(signature={"keyid": "markpact-root", "alg": "ed25519", "sig": "AA=="})
    verdict = verify_release(rel, trusted_keys={"markpact-root": "ZmFrZQ=="})
    assert verdict["ok"] is False
    assert "mismatch" in verdict["error"]


# ---- hotload_release_pack glue -------------------------------------------


def test_hotload_requires_pairing(tmp_path, monkeypatch):
    monkeypatch.delenv("URISYS_NODE_SKIP_PAIRING", raising=False)
    monkeypatch.setattr(identity, "load_pairing", lambda: {"paired": False})
    called = {}
    monkeypatch.setattr(artifact_resolver, "fetch_release", lambda *a, **k: called.setdefault("fetch", True))

    out = hotload_release_pack(
        _runtime(tmp_path), "uristepper.contract", "0.1.0",
        catalog_url="https://markpact.com", profile_path=str(tmp_path / "p.yaml"),
    )
    assert out["ok"] is False
    assert out["stage"] == "pairing"
    assert "fetch" not in called  # gate fails before touching the catalog


def test_hotload_happy_path_wires_forward(tmp_path, monkeypatch):
    monkeypatch.delenv("URISYS_NODE_REQUIRE_SIGNATURE", raising=False)
    rt = _runtime(tmp_path)
    ran = {}

    monkeypatch.setattr(artifact_resolver, "fetch_release", lambda *a, **k: _release())

    def fake_run(release, profile, *, container, port):
        ran.update(release=release, port=port)
        return {"ok": True, "port": port, "ref": "img:amd64", "container": container}

    monkeypatch.setattr(artifact_resolver, "run_release", fake_run)

    out = hotload_release_pack(
        rt, "uristepper.contract", "0.1.0",
        catalog_url="https://markpact.com", profile_path=str(tmp_path / "p.yaml"),
        context={"skip_pairing": True}, port=8791,
    )

    assert out["ok"] is True
    assert out["stage"] == "registered"
    assert out["scheme"] == "stepper"
    assert out["endpoint"] == "http://127.0.0.1:8791"
    assert rt.config["forward_targets"]["stepper"] == "http://127.0.0.1:8791"
    assert any(r.pattern.endswith("/command/move") for r in rt.routes)
    move = next(r for r in rt.routes if r.pattern.endswith("/command/move"))
    assert move.approval == "required" and move.side_effects is True


def test_hotload_bad_signature_skips_run(tmp_path, monkeypatch):
    monkeypatch.setenv("URISYS_NODE_REQUIRE_SIGNATURE", "1")
    monkeypatch.setattr(artifact_resolver, "fetch_release", lambda *a, **k: _release())

    def must_not_run(*_a, **_k):
        raise AssertionError("run_release must not be called when signature gate fails")

    monkeypatch.setattr(artifact_resolver, "run_release", must_not_run)

    out = hotload_release_pack(
        _runtime(tmp_path), "uristepper.contract", "0.1.0",
        catalog_url="https://markpact.com", profile_path=str(tmp_path / "p.yaml"),
        context={"skip_pairing": True},
    )
    assert out["ok"] is False
    assert out["stage"] == "verify"


def test_hotload_missing_scheme_patterns(tmp_path, monkeypatch):
    monkeypatch.delenv("URISYS_NODE_REQUIRE_SIGNATURE", raising=False)
    rel = _release()
    rel.pop("scheme")
    rel.pop("patterns")
    monkeypatch.setattr(artifact_resolver, "fetch_release", lambda *a, **k: rel)
    monkeypatch.setattr(artifact_resolver, "run_release", lambda *a, **k: pytest.fail("should not run"))

    out = hotload_release_pack(
        _runtime(tmp_path), "uristepper.contract", "0.1.0",
        catalog_url="https://markpact.com", profile_path=str(tmp_path / "p.yaml"),
        context={"skip_pairing": True},
    )
    assert out["ok"] is False
    assert out["stage"] == "spec"
