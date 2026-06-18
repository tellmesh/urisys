"""Pick the newest available version of a tellmesh package across PyPI and GitHub.

Our control-plane packages (uricontrol, uriguard, uriresolver, uritransport, urisys-node)
publish to **GitHub Releases first** because registering / uploading to PyPI is rate-limited
(HTTP 429) and several names are squatted. So install resolution must not hard-pin a single
channel: when the GitHub release is newer than PyPI (or PyPI is unreachable), install the
GitHub wheel; otherwise use the PyPI spec.

Network calls are best-effort with short timeouts and a process cache; any failure falls back
to the caller's pinned ``fallback_version`` GitHub wheel, so installs never hang on a blocked
PyPI. Set ``URISYS_OFFLINE=1`` to skip all network probes.
"""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Callable

_cache: dict[str, tuple[str, dict[str, Any]]] = {}


def parse_version(text: str | None) -> tuple[int, ...]:
    parts: list[int] = []
    for piece in (text or "").strip().lstrip("v").split("."):
        num = ""
        for ch in piece:
            if ch.isdigit():
                num += ch
            else:
                break
        parts.append(int(num) if num else 0)
    return tuple(parts) or (0,)


def _get_json(url: str, timeout: float) -> dict[str, Any] | None:
    if os.environ.get("URISYS_OFFLINE", "").strip():
        return None
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "urisys"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec - fixed registry hosts
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def github_latest(repo: str, owner: str = "tellmesh", timeout: float = 8.0) -> str | None:
    data = _get_json(f"https://api.github.com/repos/{owner}/{repo}/releases/latest", timeout)
    tag = (data or {}).get("tag_name")
    return tag.lstrip("v") if tag else None


def pypi_latest(dist: str, timeout: float = 6.0) -> str | None:
    data = _get_json(f"https://pypi.org/pypi/{dist}/json", timeout)
    return ((data or {}).get("info") or {}).get("version")


def resolve_install_spec(
    *,
    dist: str,
    repo: str,
    wheel_url_builder: Callable[[str], str],
    fallback_version: str,
    owner: str = "tellmesh",
) -> tuple[str, dict[str, Any]]:
    """Return ``(pip_spec, meta)`` for the newest version across PyPI and GitHub.

    GitHub wins ties (it is the primary channel and PyPI is rate-limited). When neither
    probe answers, falls back to the GitHub wheel at ``fallback_version``.
    """
    if dist in _cache:
        return _cache[dist]

    gh = github_latest(repo, owner)
    py = pypi_latest(dist)

    if gh and (py is None or parse_version(gh) >= parse_version(py)):
        spec, source, version = wheel_url_builder(gh), "github", gh
    elif py and (gh is None or parse_version(py) > parse_version(gh)):
        spec, source, version = f"{dist}>={py}", "pypi", py
    else:
        spec, source, version = wheel_url_builder(fallback_version), "fallback", fallback_version

    meta = {"version": version, "source": source, "github": gh, "pypi": py}
    _cache[dist] = (spec, meta)
    return spec, meta
