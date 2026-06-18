from __future__ import annotations

from pathlib import Path

from urisys.managers.markpact_run import run_markpact

from pack_import_isolation import reset_embedded_pack_imports

TELLMESH = Path(__file__).resolve().parents[2]
URISHELL = TELLMESH / "urishell" / "markpacts" / "urishell.markpact.md"
SHOWCASE = TELLMESH / "markpact-contracts" / "packs" / "uribrowser.showcase.markpact.md"


def test_run_pack_mode(tmp_path, monkeypatch):
    monkeypatch.setenv("TELLMESH_ROOT", str(TELLMESH))
    if not URISHELL.is_file():
        import pytest

        pytest.skip("urishell.markpact.md not generated yet")
    result = run_markpact(URISHELL, mode="pack", out=tmp_path / ".markpact")
    assert result["ok"] is True
    assert result["mode"] == "pack"
    assert len(result["routes"]) >= 1


def test_run_interface_mode(tmp_path, monkeypatch):
    monkeypatch.setenv("TELLMESH_ROOT", str(TELLMESH))
    if not URISHELL.is_file():
        import pytest

        pytest.skip("urishell.markpact.md not generated yet")
    result = run_markpact(URISHELL, mode="interface", out=tmp_path / ".markpact")
    assert result["ok"] is True
    assert result["interface"]


def test_run_flow_mode(tmp_path, monkeypatch):
    monkeypatch.setenv("TELLMESH_ROOT", str(TELLMESH))
    if not URISHELL.is_file():
        import pytest

        pytest.skip("urishell.markpact.md not generated yet")
    result = run_markpact(URISHELL, mode="flow", approve=True, dry_run=True, out=tmp_path / ".markpact")
    assert result["ok"] is True
    assert result["flows"][0]["id"] == "shell-smoke"


def test_run_flow_fragment(tmp_path, monkeypatch):
    monkeypatch.setenv("TELLMESH_ROOT", str(TELLMESH))
    if not SHOWCASE.is_file():
        import pytest

        pytest.skip("uribrowser showcase missing")
    result = run_markpact(
        SHOWCASE,
        mode="flow",
        flow_id="open-and-read",
        approve=True,
        dry_run=True,
        out=tmp_path / ".markpact",
    )
    assert result["ok"] is True
    assert len(result["flows"]) == 1
    assert result["flows"][0]["id"] == "open-and-read"


def test_run_integration_flow_local_siblings(tmp_path, monkeypatch):
    monkeypatch.setenv("TELLMESH_ROOT", str(TELLMESH))
    if not SHOWCASE.is_file():
        import pytest

        pytest.skip("uribrowser showcase missing")
    reset_embedded_pack_imports()
    from urisys.managers.markpact_pack_deps import extend_tellmesh_paths

    try:
        extend_tellmesh_paths(anchor=SHOWCASE)
        import urienv  # noqa: F401
        import urikvm  # noqa: F401
        import urishell  # noqa: F401
    except ModuleNotFoundError:
        import pytest

        pytest.skip("tellmesh sibling packs not available")

    result = run_markpact(
        SHOWCASE,
        mode="flow",
        flow_id="install-and-verify",
        approve=True,
        dry_run=True,
        out=tmp_path / ".markpact",
    )
    assert result["ok"] is True
    assert len(result["flows"]) == 1
    assert result["flows"][0]["id"] == "install-and-verify"
    assert len(result["flows"][0]["results"]) == 4
