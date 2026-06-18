"""Regression: embedded markpact unpack must not break later sibling-pack tests."""

from __future__ import annotations

from pathlib import Path

from pack_import_isolation import reset_embedded_pack_imports
from urisys.managers.markpact_pack_gen import generate_pack_markpact
from urisys.managers.markpact_manager import MarkpactManager

TELLMESH = Path(__file__).resolve().parents[2]
URIKVM_PKG = TELLMESH / "urikvm" / "urikvm"
SHOWCASE = TELLMESH / "markpact-contracts" / "packs" / "uribrowser.showcase.markpact.md"


def test_embedded_urikvm_does_not_break_integration_flow(tmp_path, monkeypatch):
    """Reproduce session pollution: urikvm embed then browser showcase integration."""
    if not URIKVM_PKG.is_dir() or not SHOWCASE.is_file():
        import pytest

        pytest.skip("urikvm or showcase missing")

    monkeypatch.setenv("TELLMESH_ROOT", str(TELLMESH))
    text = generate_pack_markpact(URIKVM_PKG, repo_root=TELLMESH)
    src = tmp_path / "urikvm.full.markpact.md"
    src.write_text(text, encoding="utf-8")

    import sys

    compiled = MarkpactManager(cache_root=tmp_path / ".markpact").compile(src, force=True)
    for name in list(sys.modules):
        if name == "urikvm" or name.startswith("urikvm."):
            del sys.modules[name]
    sys.path.insert(0, str(compiled.cache_dir))
    import urikvm  # noqa: F401

    reset_embedded_pack_imports()

    from urisys.managers.markpact_pack_deps import extend_tellmesh_paths
    from urisys.managers.markpact_run_flow import run_markpact_flow

    try:
        extend_tellmesh_paths(anchor=SHOWCASE)
        import urienv  # noqa: F401
        import urikvm as urikvm_real  # noqa: F401
        import urishell  # noqa: F401
        assert "/pytest-" not in (getattr(urikvm_real, "__file__", "") or "")
    except ModuleNotFoundError:
        import pytest

        pytest.skip("tellmesh sibling packs not available")

    report = run_markpact_flow(
        SHOWCASE,
        flow_id="install-and-verify",
        out_dir=tmp_path / "cache",
        events_path=tmp_path / "events.jsonl",
        approved=True,
        dry_run=True,
    )
    assert report["ok"] is True
    assert report["uses"] == ["env", "kvm", "shell"]
