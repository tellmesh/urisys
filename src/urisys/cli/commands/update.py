from __future__ import annotations

import subprocess
import sys
from importlib.metadata import version as _dist_version

from ..helpers import print_json

# tellmesh packages whose GitHub release may be newer than PyPI (PyPI publish is rate-limited).
# dist name == GitHub repo name for all of these.
DEFAULT_TARGETS = (
    "urisys",
    "urisys-node",
    "uricontrol",
    "uriguard",
    "uriresolver",
    "uritransport",
)


def _installed(dist: str) -> str | None:
    try:
        return _dist_version(dist)
    except Exception:
        return None


def _wheel_url_for(dist: str, repo: str):
    def build(version: str) -> str:
        whl = f"{dist.replace('-', '_')}-{version}-py3-none-any.whl"
        return f"https://github.com/tellmesh/{repo}/releases/download/v{version}/{whl}"

    return build


def cmd_update(args) -> int:
    """Install the newest available version of each tellmesh package across PyPI and GitHub
    releases. Works around PyPI publish blocks: when the GitHub release is newer than PyPI,
    install the GitHub wheel. ``--check`` only reports the plan."""
    from ...version_resolve import parse_version, resolve_install_spec

    targets = list(args.packages) if args.packages else list(DEFAULT_TARGETS)
    plan: list[dict] = []
    for dist in targets:
        repo = dist  # dist == repo for tellmesh packages
        installed = _installed(dist)
        spec, meta = resolve_install_spec(
            dist=dist,
            repo=repo,
            wheel_url_builder=_wheel_url_for(dist, repo),
            fallback_version=installed or "0",
        )
        newest = meta.get("version")
        outdated = installed is None or (newest and parse_version(newest) > parse_version(installed))
        plan.append({
            "dist": dist,
            "installed": installed,
            "newest": newest,
            "source": meta.get("source"),
            "github": meta.get("github"),
            "pypi": meta.get("pypi"),
            "outdated": bool(outdated),
            "spec": spec if outdated else None,
        })

    to_install = [p for p in plan if p["outdated"] and p["spec"]]
    report = {"ok": True, "check": bool(args.check), "plan": plan,
              "to_install": [p["dist"] for p in to_install]}

    if args.check or not to_install:
        print_json(report)
        return 0

    specs = [p["spec"] for p in to_install]
    proc = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-U", *specs],
        capture_output=True, text=True,
    )
    report["pip"] = {
        "ok": proc.returncode == 0,
        "command": " ".join([sys.executable, "-m", "pip", "install", "-U", *specs]),
        "exit_code": proc.returncode,
        "stdout": (proc.stdout or "")[-3000:],
        "stderr": (proc.stderr or "")[-3000:],
    }
    report["ok"] = proc.returncode == 0
    print_json(report)
    return 0 if proc.returncode == 0 else 1
