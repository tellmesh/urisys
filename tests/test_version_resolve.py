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


def test_github_api_uses_token_when_present(monkeypatch):
    import urllib.request
    from urisys import version_resolve as vr
    captured = {}

    class _Resp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self): return b'{"tag_name": "v9.9.9"}'

    def fake_urlopen(req, timeout=0):
        captured["headers"] = {k.lower(): v for k, v in req.header_items()}
        return _Resp()

    monkeypatch.delenv("URISYS_OFFLINE", raising=False)
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setenv("GH_TOKEN", "secret123")
    assert vr.github_latest("urisys-node") == "9.9.9"
    assert captured["headers"].get("authorization") == "Bearer secret123"


def test_no_auth_header_without_token(monkeypatch):
    import urllib.request
    from urisys import version_resolve as vr
    captured = {}

    class _Resp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self): return b'{"tag_name": "v1.0.0"}'

    def fake_urlopen(req, timeout=0):
        captured["headers"] = {k.lower(): v for k, v in req.header_items()}
        return _Resp()

    for v in ("URISYS_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN", "URISYS_OFFLINE"):
        monkeypatch.delenv(v, raising=False)
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert vr.github_latest("urisys-node") == "1.0.0"
    assert "authorization" not in captured["headers"]
