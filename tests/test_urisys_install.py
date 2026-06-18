"""urisys package install spec resolves GitHub vs PyPI."""

from __future__ import annotations

from urisys.urisys_install import pip_spec, resolve_pip_spec, wheel_url


def test_urisys_pip_spec_github_newer(monkeypatch):
    from urisys import version_resolve as vr

    vr._cache.clear()
    monkeypatch.setattr(vr, "github_latest", lambda *a, **k: "0.9.0")
    monkeypatch.setattr(vr, "pypi_latest", lambda *a, **k: "0.1.0")
    spec, meta = resolve_pip_spec()
    assert meta["source"] == "github"
    assert spec.startswith("urisys[real] @ https://")
    assert "0.9.0" in spec


def test_urisys_pip_spec_pypi_newer(monkeypatch):
    from urisys import version_resolve as vr

    vr._cache.clear()
    monkeypatch.setattr(vr, "github_latest", lambda *a, **k: "0.1.0")
    monkeypatch.setattr(vr, "pypi_latest", lambda *a, **k: "0.9.0")
    spec, meta = resolve_pip_spec()
    assert meta["source"] == "pypi"
    assert spec == "urisys[real]>=0.9.0"


def test_wheel_url_pattern():
    assert wheel_url("0.1.83").endswith("/urisys-0.1.83-py3-none-any.whl")


def test_pip_spec_returns_string():
    assert isinstance(pip_spec(), str)
