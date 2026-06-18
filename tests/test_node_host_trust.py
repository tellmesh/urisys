from __future__ import annotations

from pathlib import Path

import pytest

from urisys.node_host_trust import (
    remote_host_trust_command,
    resolve_enable_host_trust_script,
    resolve_urisys_node_root,
    run_host_trust,
)


def test_resolve_urisys_node_root_from_env(monkeypatch, tmp_path: Path):
    script = tmp_path / "scripts" / "enable-host-trust.sh"
    script.parent.mkdir(parents=True)
    script.write_text("#!/bin/bash\n", encoding="utf-8")
    monkeypatch.setenv("URISYS_NODE_ROOT", str(tmp_path))
    assert resolve_urisys_node_root() == tmp_path.resolve()
    assert resolve_enable_host_trust_script() == script


def test_run_host_trust_dry_run_python_only(monkeypatch, tmp_path: Path):
    import os

    venv = tmp_path / "venv"
    bin_dir = venv / "bin"
    bin_dir.mkdir(parents=True)
    node_bin = bin_dir / "urisys-node"
    node_bin.write_text("#!/bin/sh\n", encoding="utf-8")
    node_bin.chmod(0o755)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("URISYS_NODE_ROOT", raising=False)

    report = run_host_trust(
        venv=venv,
        node_id="lenovo",
        port=8790,
        host="0.0.0.0",
        dry_run=True,
        prefer_script=False,
    )
    assert report["ok"] is True
    assert report["mode"] == "python"
    assert report["node_id"] == "lenovo"
    assert any(a["path"].endswith("node-profile.json") for a in report["actions"])


def test_remote_host_trust_command_uses_urisys_cli():
    cmd = remote_host_trust_command(venv="~/venv", node_id="lenovo", pull=False)
    assert "urisys node host-trust" in cmd
    assert "enable-host-trust.sh" in cmd
    assert "curl -fsSL" in cmd


def test_remote_host_trust_command_git_pull():
    cmd = remote_host_trust_command(pull=True)
    assert "git pull" in cmd
    assert ".git" in cmd
