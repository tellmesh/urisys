"""Install tellmesh uriresolver (uri_resolver) — YAML target resolution for the mesh."""

from __future__ import annotations

import importlib.util
import os
from typing import Any

DEFAULT_GITHUB_OWNER = "tellmesh"
DEFAULT_GITHUB_VERSION = "0.1.0"
DIST_NAME = "uriresolver"
MODULE_NAME = "uri_resolver"


def github_owner() -> str:
    return os.environ.get("URISYS_URIRESOLVER_GITHUB_OWNER", DEFAULT_GITHUB_OWNER).strip()


def github_version() -> str:
    return os.environ.get("URISYS_URIRESOLVER_VERSION", DEFAULT_GITHUB_VERSION).strip().lstrip("v")


def wheel_url(version: str | None = None) -> str:
    ver = (version or github_version()).lstrip("v")
    override = os.environ.get("URISYS_URIRESOLVER_WHEEL_URL", "").strip()
    if override:
        return override
    return (
        f"https://github.com/{github_owner()}/{DIST_NAME}/releases/download/v{ver}/"
        f"{DIST_NAME}-{ver}-py3-none-any.whl"
    )


def pip_spec() -> str:
    """Install uriresolver from GitHub wheel (set URISYS_URIRESOLVER_PYPI=1 for PyPI)."""
    if os.environ.get("URISYS_URIRESOLVER_PYPI", "").strip():
        return f"{DIST_NAME}>={github_version()}"
    return wheel_url()


def _module_exists(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def diagnose_uriresolver() -> dict[str, Any]:
    ok = _module_exists(MODULE_NAME)
    return {
        "uri_resolver_importable": ok,
        "wheel_url": pip_spec(),
        "note": None if ok else "Install tellmesh uriresolver (uri_resolver).",
    }
