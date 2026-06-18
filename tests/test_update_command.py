"""`urisys update` picks the newest version across PyPI and GitHub (PyPI-block workaround)."""

from __future__ import annotations

import json

from urisys.cli.commands import update as upd


class _Args:
    def __init__(self, packages=None, check=True):
        self.packages = packages or []
        self.check = check


def test_update_check_reports_outdated_from_github(monkeypatch, capsys):
    monkeypatch.setattr(upd, "_installed", lambda d: "0.1.33" if d == "urisys-node" else "9.9.9")

    from urisys import version_resolve as vr

    def fake_resolve(*, dist, repo, wheel_url_builder, fallback_version):
        version = {"urisys-node": "0.1.35"}.get(dist, fallback_version)
        return wheel_url_builder(version), {
            "version": version, "source": "github", "github": version, "pypi": None,
        }

    monkeypatch.setattr(vr, "resolve_install_spec", fake_resolve)

    rc = upd.cmd_update(_Args(packages=["urisys-node", "uricontrol"], check=True))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)

    node = next(p for p in out["plan"] if p["dist"] == "urisys-node")
    assert node["outdated"] is True
    assert node["newest"] == "0.1.35"
    assert node["source"] == "github"
    assert node["spec"].endswith("urisys_node-0.1.35-py3-none-any.whl")
    assert "urisys-node" in out["to_install"]

    # uricontrol: installed 9.9.9 == newest fallback → not outdated, not installed
    uc = next(p for p in out["plan"] if p["dist"] == "uricontrol")
    assert uc["outdated"] is False
    assert uc["spec"] is None


def test_update_check_does_not_install(monkeypatch, capsys):
    import subprocess

    monkeypatch.setattr(upd, "_installed", lambda d: None)

    def _boom(*a, **k):
        raise AssertionError("pip must not run with --check")

    monkeypatch.setattr(subprocess, "run", _boom)
    rc = upd.cmd_update(_Args(packages=["uritransport"], check=True))
    assert rc == 0
    assert "pip" not in json.loads(capsys.readouterr().out)
