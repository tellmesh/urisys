"""Install/repair tellmesh uricore (uri_control) — PyPI name is squatted by another project."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from typing import Any

DEFAULT_GITHUB_OWNER = "tellmesh"
DEFAULT_GITHUB_VERSION = "0.1.8"


def github_owner() -> str:
    return os.environ.get("URISYS_URICORE_GITHUB_OWNER", DEFAULT_GITHUB_OWNER).strip()


def github_version() -> str:
    return os.environ.get("URISYS_URICORE_VERSION", DEFAULT_GITHUB_VERSION).strip().lstrip("v")


def wheel_url(version: str | None = None) -> str:
    ver = (version or github_version()).lstrip("v")
    override = os.environ.get("URISYS_URICORE_WHEEL_URL", "").strip()
    if override:
        return override
    return (
        f"https://github.com/{github_owner()}/uricore/releases/download/v{ver}/"
        f"uricore-{ver}-py3-none-any.whl"
    )


def pip_spec() -> str:
    return wheel_url()


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
    """True when ``uricore`` dist is installed but ``uri_control`` is not available."""
    if _module_exists("uri_control"):
        return False
    if not _pkg_version("uricore"):
        return False
    tops = _dist_top_levels("uricore")
    if "uri_control" in tops:
        return True  # broken tellmesh install
    if "uricore" in tops:
        return True  # PyPI squatter package
    return True


def diagnose_uricore() -> dict[str, Any]:
    installed = _pkg_version("uricore")
    uri_control_ok = _module_exists("uri_control")
    wrong = is_wrong_uricore_installed()
    return {
        "uricore_dist": installed,
        "uri_control_importable": uri_control_ok,
        "wrong_pypi_package": wrong,
        "wheel_url": pip_spec(),
        "note": (
            "PyPI package 'uricore' is a different project (module uricore/, not uri_control/). "
            "Install tellmesh uricore from GitHub wheel."
            if wrong or (installed and not uri_control_ok)
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
    """Uninstall squatted PyPI uricore and install tellmesh wheel."""
    steps: list[dict[str, Any]] = []
    if is_wrong_uricore_installed() or _pkg_version("uricore"):
        uninstall = pip_run(["uninstall", "-y", "uricore"], python=python)
        steps.append({"name": "pip_uninstall_uricore", **uninstall})
        if not uninstall["ok"]:
            return {"ok": False, "steps": steps, "error": "pip uninstall uricore failed"}

    install = pip_run(["install", "-U", wheel_url(version)], python=python)
    steps.append({"name": "pip_install_tellmesh_uricore", **install})
    ok = install["ok"] and _module_exists("uri_control")
    return {
        "ok": ok,
        "steps": steps,
        "wheel_url": wheel_url(version),
        "diagnosis": diagnose_uricore(),
        "error": None if ok else "uri_control still not importable after repair",
    }
