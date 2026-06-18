"""Install/repair tellmesh uricore (uri_control) — PyPI name is squatted by another project."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from typing import Any

DEFAULT_GITHUB_OWNER = "tellmesh"
DEFAULT_GITHUB_VERSION = "0.1.14"
DIST_NAME = "uricontrol"  # PyPI dist (module is uri_control); renamed from squatted 'uricore'
GITHUB_REPO = "uricontrol"  # GitHub repo name
SQUATTED_DIST = "uricore"  # unrelated PyPI project (module uricore/, not uri_control/)


def github_owner() -> str:
    return os.environ.get("URISYS_URICORE_GITHUB_OWNER", DEFAULT_GITHUB_OWNER).strip()


def github_version() -> str:
    return os.environ.get("URISYS_URICORE_VERSION", DEFAULT_GITHUB_VERSION).strip().lstrip("v")


def wheel_url(version: str | None = None) -> str:
    """GitHub release wheel for uricontrol — the parallel channel, reused when PyPI is
    unavailable (force it via URISYS_URICORE_WHEEL_URL)."""
    ver = (version or github_version()).lstrip("v")
    override = os.environ.get("URISYS_URICORE_WHEEL_URL", "").strip()
    if override:
        return override
    return (
        f"https://github.com/{github_owner()}/{GITHUB_REPO}/releases/download/v{ver}/"
        f"{DIST_NAME}-{ver}-py3-none-any.whl"
    )


def pip_spec() -> str:
    """Newest of (GitHub release, PyPI). URISYS_URICORE_WHEEL_URL pins a wheel;
    URISYS_URICORE_PYPI=1 forces the PyPI spec. (PyPI uploads are 429-limited, so the
    GitHub release is usually newest.)"""
    if os.environ.get("URISYS_URICORE_WHEEL_URL", "").strip():
        return wheel_url()
    if os.environ.get("URISYS_URICORE_PYPI", "").strip():
        return f"{DIST_NAME}>={github_version()}"
    from .version_resolve import resolve_install_spec

    spec, _ = resolve_install_spec(
        dist=DIST_NAME, repo=DIST_NAME, wheel_url_builder=wheel_url,
        fallback_version=DEFAULT_GITHUB_VERSION, owner=github_owner(),
    )
    return spec


def _pkg_version(dist_name: str) -> str | None:
    try:
        from importlib.metadata import version

        return version(dist_name)
    except Exception:
        return None


def _module_exists(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _dist_top_levels(dist_name: str) -> set[str]:
    try:
        from importlib.metadata import files

        tops: set[str] = set()
        for entry in files(dist_name) or []:
            name = entry.name
            if "/" in name:
                tops.add(name.split("/")[0])
            elif name.endswith(".py"):
                tops.add(name[:-3])
        return tops
    except Exception:
        return set()


def is_wrong_uricore_installed() -> bool:
    """True when the squatted PyPI ``uricore`` dist shadows our control-plane (``uri_control``
    not importable). Our package is now ``uricontrol``, so a plain ``uricore`` is always wrong."""
    if _module_exists("uri_control"):
        return False
    return bool(_pkg_version(SQUATTED_DIST))


def diagnose_uricore() -> dict[str, Any]:
    installed = _pkg_version(DIST_NAME)
    uri_control_ok = _module_exists("uri_control")
    wrong = is_wrong_uricore_installed()
    return {
        "uricore_dist": installed,
        "uri_control_importable": uri_control_ok,
        "wrong_pypi_package": wrong,
        "wheel_url": pip_spec(),
        "note": (
            "PyPI package 'uricore' is an unrelated project (module uricore/, not uri_control/). "
            "Install 'uricontrol' (module uri_control) from PyPI."
            if wrong or (not uri_control_ok)
            else None
        ),
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


def repair_uricore(*, python: str | None = None, version: str | None = None) -> dict[str, Any]:
    """Uninstall the squatted PyPI ``uricore`` and install tellmesh ``uricontrol``."""
    steps: list[dict[str, Any]] = []
    if _pkg_version(SQUATTED_DIST):
        uninstall = pip_run(["uninstall", "-y", SQUATTED_DIST], python=python)
        steps.append({"name": "pip_uninstall_squatted_uricore", **uninstall})
        if not uninstall["ok"]:
            return {"ok": False, "steps": steps, "error": "pip uninstall uricore failed"}

    spec = wheel_url(version) if version else pip_spec()
    install = pip_run(["install", "-U", spec], python=python)
    steps.append({"name": "pip_install_uricontrol", **install})
    ok = install["ok"] and _module_exists("uri_control")
    return {
        "ok": ok,
        "steps": steps,
        "wheel_url": wheel_url(version),
        "diagnosis": diagnose_uricore(),
        "error": None if ok else "uri_control still not importable after repair",
    }
