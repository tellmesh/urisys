"""Install/repair tellmesh uriguard (uri_guard) — policy gate for uricontrol.

PyPI name ``urirouter`` is squatted by an unrelated project; always uninstall it.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from typing import Any

DEFAULT_GITHUB_OWNER = "tellmesh"
DEFAULT_GITHUB_VERSION = "0.1.0"
DIST_NAME = "uriguard"
MODULE_NAME = "uri_guard"
SQUATTED_ROUTER_DIST = "urirouter"


def github_owner() -> str:
    return os.environ.get("URISYS_URIGUARD_GITHUB_OWNER", DEFAULT_GITHUB_OWNER).strip()


def github_version() -> str:
    return os.environ.get("URISYS_URIGUARD_VERSION", DEFAULT_GITHUB_VERSION).strip().lstrip("v")


def wheel_url(version: str | None = None) -> str:
    ver = (version or github_version()).lstrip("v")
    override = os.environ.get("URISYS_URIGUARD_WHEEL_URL", "").strip()
    if override:
        return override
    return (
        f"https://github.com/{github_owner()}/{DIST_NAME}/releases/download/v{ver}/"
        f"{DIST_NAME}-{ver}-py3-none-any.whl"
    )


def pip_spec() -> str:
    """Install uriguard from the GitHub release wheel (set URISYS_URIGUARD_PYPI=1 for PyPI)."""
    if os.environ.get("URISYS_URIGUARD_PYPI", "").strip():
        return f"{DIST_NAME}>={github_version()}"
    return wheel_url()


def _pkg_version(dist_name: str) -> str | None:
    try:
        from importlib.metadata import version

        return version(dist_name)
    except Exception:
        return None


def _module_exists(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def is_wrong_urirouter_installed() -> bool:
    """True when the squatted PyPI ``urirouter`` dist is present (legacy tellmesh name)."""
    return bool(_pkg_version(SQUATTED_ROUTER_DIST))


def diagnose_uriguard() -> dict[str, Any]:
    ok = _module_exists(MODULE_NAME)
    wrong_router = is_wrong_urirouter_installed()
    note = None
    if wrong_router:
        note = (
            f"PyPI package '{SQUATTED_ROUTER_DIST}' is unrelated (legacy name). "
            f"Run: pip uninstall -y {SQUATTED_ROUTER_DIST}"
        )
    elif not ok:
        note = "Install tellmesh uriguard (uri_guard) — uricontrol policy gate."
    return {
        "uri_guard_importable": ok,
        "wrong_urirouter_dist": wrong_router,
        "urirouter_dist": _pkg_version(SQUATTED_ROUTER_DIST),
        "wheel_url": pip_spec(),
        "note": note,
    }


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


def uninstall_squatted_urirouter(*, python: str | None = None) -> dict[str, Any]:
    """Remove the unrelated PyPI ``urirouter`` package if installed."""
    if not is_wrong_urirouter_installed():
        return {"ok": True, "skipped": True}
    uninstall = pip_run(["uninstall", "-y", SQUATTED_ROUTER_DIST], python=python)
    ok = uninstall["ok"] and not is_wrong_urirouter_installed()
    return {
        "ok": ok,
        "uninstall": uninstall,
        "error": None if ok else f"pip uninstall {SQUATTED_ROUTER_DIST} failed",
    }
