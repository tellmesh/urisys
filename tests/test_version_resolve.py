"""resolve_install_spec picks the newest version across GitHub releases and PyPI."""

from __future__ import annotations

from urisys import version_resolve as vr


def _wheel(v: str) -> str:
    return f"https://github.com/tellmesh/uriguard/releases/download/v{v}/uriguard-{v}-py3-none-any.whl"


def _resolve(monkeypatch, gh, py):
    vr._cache.clear()
    monkeypatch.setattr(vr, "github_latest", lambda *a, **k: gh)
    monkeypatch.setattr(vr, "pypi_latest", lambda *a, **k: py)
    return vr.resolve_install_spec(
        dist="uriguard", repo="uriguard", wheel_url_builder=_wheel, fallback_version="0.1.0"
    )


def test_github_newer_uses_github_wheel(monkeypatch):
    spec, meta = _resolve(monkeypatch, gh="0.2.0", py="0.1.5")
    assert meta["source"] == "github" and meta["version"] == "0.2.0"
    assert spec == _wheel("0.2.0")


def test_pypi_newer_uses_pypi_spec(monkeypatch):
    spec, meta = _resolve(monkeypatch, gh="0.1.0", py="0.3.0")
    assert meta["source"] == "pypi"
    assert spec == "uriguard>=0.3.0"


def test_tie_prefers_github(monkeypatch):
    _, meta = _resolve(monkeypatch, gh="0.2.0", py="0.2.0")
    assert meta["source"] == "github"


def test_pypi_unreachable_uses_github(monkeypatch):
    spec, meta = _resolve(monkeypatch, gh="0.2.0", py=None)
    assert meta["source"] == "github" and spec == _wheel("0.2.0")


def test_both_unreachable_falls_back(monkeypatch):
    spec, meta = _resolve(monkeypatch, gh=None, py=None)
    assert meta["source"] == "fallback" and spec == _wheel("0.1.0")


def test_offline_skips_network(monkeypatch):
    monkeypatch.setenv("URISYS_OFFLINE", "1")
    assert vr.github_latest("uriguard") is None
    assert vr.pypi_latest("uriguard") is None
