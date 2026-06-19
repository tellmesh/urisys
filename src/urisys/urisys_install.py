"""Install tellmesh urisys — prefer GitHub Release when newer than PyPI (429-safe)."""

from __future__ import annotations

import os
from typing import Any

DEFAULT_GITHUB_OWNER = "tellmesh"
DEFAULT_GITHUB_VERSION = "0.1.91"
DIST_NAME = "urisys"
GITHUB_REPO = "urisys"


def github_owner() -> str:
    return os.environ.get("URISYS_GITHUB_OWNER", DEFAULT_GITHUB_OWNER).strip()


def github_version() -> str:
    return os.environ.get("URISYS_VERSION", DEFAULT_GITHUB_VERSION).strip().lstrip("v")


def wheel_url(version: str | None = None) -> str:
    ver = (version or github_version()).lstrip("v")
    override = os.environ.get("URISYS_WHEEL_URL", "").strip()
    if override:
        return override
    return (
        f"https://github.com/{github_owner()}/{GITHUB_REPO}/releases/download/v{ver}/"
        f"{DIST_NAME}-{ver}-py3-none-any.whl"
    )


def resolve_pip_spec(*, with_real: bool = True) -> tuple[str, dict[str, Any]]:
    """Return pip install spec + resolution meta (github / pypi / fallback)."""
    if os.environ.get("URISYS_WHEEL_URL", "").strip():
        spec = wheel_url()
        return spec, {"version": github_version(), "source": "env_wheel", "spec": spec}
    if os.environ.get("URISYS_PYPI", "").strip():
        ver = github_version()
        spec = f'{DIST_NAME}[real]>={ver}' if with_real else f"{DIST_NAME}>={ver}"
        return spec, {"version": ver, "source": "pypi_env", "spec": spec}

    from .version_resolve import resolve_install_spec

    spec, meta = resolve_install_spec(
        dist=DIST_NAME,
        repo=GITHUB_REPO,
        wheel_url_builder=wheel_url,
        fallback_version=DEFAULT_GITHUB_VERSION,
        owner=github_owner(),
    )
    if meta.get("source") == "pypi":
        ver = meta["version"]
        pip_spec = f'{DIST_NAME}[real]>={ver}' if with_real else f"{DIST_NAME}>={ver}"
        return pip_spec, {**meta, "spec": pip_spec}
    if with_real:
        pip_spec = f"{DIST_NAME}[real] @ {spec}"
        return pip_spec, {**meta, "spec": pip_spec}
    return spec, {**meta, "spec": spec}


def pip_spec(*, with_real: bool = True) -> str:
    return resolve_pip_spec(with_real=with_real)[0]
