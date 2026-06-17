"""Install tellmesh urisys-node from GitHub Release wheel (no git credentials)."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from typing import Any

DEFAULT_GITHUB_OWNER = "tellmesh"
DEFAULT_GITHUB_VERSION = "0.1.3"


def github_owner() -> str:
    return os.environ.get("URISYS_NODE_GITHUB_OWNER", DEFAULT_GITHUB_OWNER).strip()


def github_version() -> str:
    return os.environ.get("URISYS_NODE_VERSION", DEFAULT_GITHUB_VERSION).strip().lstrip("v")


def wheel_filename(version: str | None = None) -> str:
    """PEP 427 wheel name — distribution uses underscores, not hyphens."""
    ver = (version or github_version()).lstrip("v")
    return f"urisys_node-{ver}-py3-none-any.whl"


def wheel_url(version: str | None = None) -> str:
    override = os.environ.get("URISYS_NODE_WHEEL_URL", "").strip()
    if override:
        return override
    ver = (version or github_version()).lstrip("v")
    return (
        f"https://github.com/{github_owner()}/urisys-node/releases/download/v{ver}/"
        f"{wheel_filename(ver)}"
    )


def pip_spec() -> str:
    return wheel_url()


def is_importable() -> bool:
    return importlib.util.find_spec("urisysnode") is not None


def pip_run(args: list[str], *, python: str | None = None, timeout: float = 600.0) -> dict[str, Any]:
    exe = python or sys.executable
    cmd = [exe, "-m", "pip", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return {
        "ok": proc.returncode == 0,
        "command": " ".join(cmd),
        "exit_code": proc.returncode,
        "stdout": (proc.stdout or "")[-3000:],
        "stderr": (proc.stderr or "")[-3000:],
    }


def install_urisys_node(*, python: str | None = None, timeout: float = 600.0) -> dict[str, Any]:
    """GitHub Release wheel (PEP 427 name), then PyPI ``urisys-node`` fallback."""
    attempts: list[dict[str, Any]] = []

    wheel = pip_run(["install", "-U", wheel_url()], python=python, timeout=timeout)
    attempts.append({"source": "github_wheel", "spec": wheel_url(), **wheel})
    if wheel["ok"] and is_importable():
        return {
            "ok": True,
            "source": "github_wheel",
            "spec": wheel_url(),
            "attempts": attempts,
            **wheel,
        }

    pypi_spec = os.environ.get("URISYS_NODE_PIP_SPEC", "urisys-node>=0.1.3").strip()
    pypi = pip_run(["install", "-U", pypi_spec], python=python, timeout=timeout)
    attempts.append({"source": "pypi", "spec": pypi_spec, **pypi})
    ok = pypi["ok"] and is_importable()
    return {
        "ok": ok,
        "source": "pypi" if ok else None,
        "spec": pypi_spec if ok else wheel_url(),
        "attempts": attempts,
        "command": pypi["command"],
        "exit_code": pypi["exit_code"],
        "stdout": pypi["stdout"],
        "stderr": pypi["stderr"],
        "error": None if ok else "urisysnode still not importable after wheel and PyPI install",
    }


def diagnose_urisys_node() -> dict[str, Any]:
    try:
        from importlib.metadata import version

        dist = version("urisys-node")
    except Exception:
        dist = None
    return {
        "urisys_node_dist": dist,
        "urisysnode_importable": is_importable(),
        "wheel_url": pip_spec(),
        "wheel_filename": wheel_filename(),
        "note": None if is_importable() else "Install from GitHub Release wheel (no git clone).",
    }
