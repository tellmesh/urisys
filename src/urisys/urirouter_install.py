"""Install tellmesh uriguard (uri_guard) — the control-plane policy gate that uricontrol
requires. (Was urirouter/uri_router before the 2026-06 split into
uriguard/uriresolver/uritransport; function names kept for init_setup compatibility.)"""

from __future__ import annotations

import importlib.util
import os
from typing import Any

DEFAULT_GITHUB_OWNER = "tellmesh"
DEFAULT_GITHUB_VERSION = "0.1.0"
DIST_NAME = "uriguard"
MODULE_NAME = "uri_guard"


def github_owner() -> str:
    return os.environ.get("URISYS_URIROUTER_GITHUB_OWNER", DEFAULT_GITHUB_OWNER).strip()


def github_version() -> str:
    return os.environ.get("URISYS_URIROUTER_VERSION", DEFAULT_GITHUB_VERSION).strip().lstrip("v")


def wheel_url(version: str | None = None) -> str:
    ver = (version or github_version()).lstrip("v")
    override = os.environ.get("URISYS_URIROUTER_WHEEL_URL", "").strip()
    if override:
        return override
    return (
        f"https://github.com/{github_owner()}/{DIST_NAME}/releases/download/v{ver}/"
        f"{DIST_NAME}-{ver}-py3-none-any.whl"
    )


def pip_spec() -> str:
    """Install uriguard from the GitHub release wheel (new names hit PyPI 429);
    set URISYS_URIGUARD_PYPI=1 to use the PyPI spec instead."""
    if os.environ.get("URISYS_URIGUARD_PYPI", "").strip():
        return f"{DIST_NAME}>={github_version()}"
    return wheel_url()


def _module_exists(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def diagnose_urirouter() -> dict[str, Any]:
    ok = _module_exists(MODULE_NAME)
    return {
        "uri_guard_importable": ok,
        "wheel_url": pip_spec(),
        "note": None if ok else "Install tellmesh uriguard (uri_guard) — uricontrol policy gate.",
    }
