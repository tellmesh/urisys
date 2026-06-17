"""Bootstrap entry and missing-uricore guardrails."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_bootstrap_import_does_not_require_uri_control():
    mod = _load_module("urisys_bootstrap_probe", SRC / "urisys" / "bootstrap.py")
    assert hasattr(mod, "main")


def test_cli_import_does_not_require_uri_control():
    import urisys.cli

    assert hasattr(urisys.cli, "main")
    assert hasattr(urisys.cli, "build_parser")


def test_missing_uricore_payload():
    from urisys.bootstrap import _missing_uricore_payload

    exc = ModuleNotFoundError("No module named 'uri_control'")
    exc.name = "uri_control"
    data = _missing_uricore_payload(exc)
    assert data["type"] == "module_not_found"
    assert "uricore" in data["hint"]
    assert data["commands"]["diagnose"] == "urisys doctor"


def test_doctor_subcommand_via_bootstrap():
    proc = subprocess.run(
        [sys.executable, "-m", "urisys.bootstrap", "doctor", "--min-version", "0.1.0"],
        cwd=ROOT,
        env={**__import__("os").environ, "PYTHONPATH": str(SRC)},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode in (0, 1), proc.stderr or proc.stdout
    data = json.loads(proc.stdout)
    assert "checks" in data
    ids = {c["id"] for c in data["checks"]}
    assert "import_uri_control" in ids
    assert "dist_uricore" in ids
