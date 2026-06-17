"""Tests for urisys init bootstrap."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def test_init_dry_run_via_bootstrap():
    proc = subprocess.run(
        [sys.executable, "-m", "urisys.bootstrap", "init", "--dry-run"],
        cwd=ROOT,
        env={**__import__("os").environ, "PYTHONPATH": str(SRC)},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    data = json.loads(proc.stdout)
    assert data["ok"] is True
    assert data["profile"] == "slave"
    names = [s["name"] for s in data["steps"]]
    assert "pip_install" in names
    assert "write_env" in names
    assert "URISYS_ALLOW_REAL" in data["shell_env"]


def test_run_init_skip_pip_writes_env(tmp_path):
    from urisys.init_setup import run_init

    env_file = tmp_path / "node.env"
    with patch("urisys.init_setup.run_doctor", return_value={"ok": True, "checks": []}):
        report = run_init(
            install=False,
            write_env=True,
            env_file=env_file,
        )
    assert report["ok"] is True
    assert env_file.is_file()
    text = env_file.read_text(encoding="utf-8")
    assert 'URISYS_ALLOW_REAL="1"' in text
    assert "urisys node serve" in text


def test_pip_install_failure():
    from urisys.init_setup import run_init

    with patch(
        "urisys.init_setup.pip_install_specs",
        return_value={"ok": False, "exit_code": 1, "stderr": "network error"},
    ):
        report = run_init(install=True, write_env=False)
    assert report["ok"] is False
    assert report["error"] == "pip install failed"
