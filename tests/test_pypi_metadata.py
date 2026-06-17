"""PyPI upload guard: metadata must not declare direct URL dependencies."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-pypi-metadata.sh"


def test_validate_pypi_metadata_script_exists():
    assert SCRIPT.is_file()


def test_built_wheel_has_no_direct_url_requires_dist():
    dist = ROOT / "dist"
    wheels = sorted(dist.glob("urisys-*.whl"))
    if not wheels:
        import pytest

        pytest.skip("no dist/urisys-*.whl — run: python -m build")
    proc = subprocess.run(["bash", str(SCRIPT), *map(str, wheels)], cwd=ROOT, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_pyproject_runtime_deps_have_no_direct_urls():
    import tomllib

    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    deps = data["project"]["dependencies"]
    offenders = [d for d in deps if " @ " in d]
    assert not offenders, f"runtime deps must not use direct URLs for PyPI: {offenders}"
