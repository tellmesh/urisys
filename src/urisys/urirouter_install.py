"""Install tellmesh urirouter (uri_router) from GitHub Release wheel."""

from __future__ import annotations

import importlib.util
import os
from typing import Any

DEFAULT_GITHUB_OWNER = "tellmesh"
DEFAULT_GITHUB_VERSION = "0.1.0"


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
        f"https://github.com/{github_owner()}/urirouter/releases/download/v{ver}/"
        f"urirouter-{ver}-py3-none-any.whl"
    )


def pip_spec() -> str:
    return wheel_url()


def _module_exists(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def diagnose_urirouter() -> dict[str, Any]:
    uri_router_ok = _module_exists("uri_router")
    return {
        "uri_router_importable": uri_router_ok,
        "wheel_url": pip_spec(),
        "note": None if uri_router_ok else "Install tellmesh urirouter before uricore (resolver dependency).",
    }
