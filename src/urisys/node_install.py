"""Install tellmesh urisys-node from GitHub Release wheel (no git credentials)."""

from __future__ import annotations

import importlib.util
import os
from typing import Any

DEFAULT_GITHUB_OWNER = "tellmesh"
DEFAULT_GITHUB_VERSION = "0.1.3"


def github_owner() -> str:
    return os.environ.get("URISYS_NODE_GITHUB_OWNER", DEFAULT_GITHUB_OWNER).strip()


def github_version() -> str:
    return os.environ.get("URISYS_NODE_VERSION", DEFAULT_GITHUB_VERSION).strip().lstrip("v")


def wheel_url(version: str | None = None) -> str:
    override = os.environ.get("URISYS_NODE_WHEEL_URL", "").strip()
    if override:
        return override
    ver = (version or github_version()).lstrip("v")
    return (
        f"https://github.com/{github_owner()}/urisys-node/releases/download/v{ver}/"
        f"urisys-node-{ver}-py3-none-any.whl"
    )


def pip_spec() -> str:
    return wheel_url()


def is_importable() -> bool:
    return importlib.util.find_spec("urisysnode") is not None


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
        "note": None if is_importable() else "Install from GitHub Release wheel (no git clone).",
    }
