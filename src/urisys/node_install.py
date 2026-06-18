"""Install tellmesh urisys-node from GitHub Release wheel (no git credentials)."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from typing import Any

DEFAULT_GITHUB_OWNER = "tellmesh"
DEFAULT_GITHUB_VERSION = "0.1.23"


def github_owner() -> str:
    return os.environ.get("URISYS_NODE_GITHUB_OWNER", DEFAULT_GITHUB_OWNER).strip()


def github_version() -> str:
    return os.environ.get("URISYS_NODE_VERSION", DEFAULT_GITHUB_VERSION).strip().lstrip("v")


def wheel_filename(version: str | None = None) -> str:
    """PEP 427 wheel name — distribution uses underscores, not hyphens."""
    ver = (version or github_version()).lstrip("v")
    return f"urisys_node-{ver}-py3-none-any.whl"


def wheel_url(version: str | None = None) -> str:
    override = os.environ.get("URISYS_NODE_WHEEL_URL", "").strip()
    if override:
        return override
    ver = (version or github_version()).lstrip("v")
    return (
        f"https://github.com/{github_owner()}/urisys-node/releases/download/v{ver}/"
        f"{wheel_filename(ver)}"
    )


def pip_spec() -> str:
    return wheel_url()


def is_importable() -> bool:
    return importlib.util.find_spec("urisysnode") is not None


CORE_NODE_PACK_SPECS = (
    "https://github.com/tellmesh/uriscreen/releases/download/v0.1.0/uriscreen-0.1.0-py3-none-any.whl",
    "https://github.com/tellmesh/urishell/releases/download/v0.1.0/urishell-0.1.0-py3-none-any.whl",
)


def _module_for_boot_spec(spec: str) -> str:
    if "uriscreen" in spec:
        return "uriscreen"
    if "urishell" in spec:
        return "urishell"
    return spec.split(">=")[0].split("[", 1)[0]


def _missing_core_node_modules() -> list[str]:
    missing: list[str] = []
    for spec in CORE_NODE_PACK_SPECS:
        module = _module_for_boot_spec(spec)
        if importlib.util.find_spec(module) is None:
            missing.append(spec)
    return missing


def ensure_core_node_packs(*, python: str | None = None, timeout: float = 600.0) -> dict[str, Any]:
    """Install screen/shell packs required by default URISYS_NODE_PACKS boot."""
    missing = _missing_core_node_modules()
    if not missing:
        return {"ok": True, "skipped": True, "specs": list(CORE_NODE_PACK_SPECS)}
    result = pip_run(["install", "-U", "--no-deps", *missing], python=python, timeout=timeout)
    result["specs"] = missing
    still_missing = [
        _module_for_boot_spec(spec)
        for spec in missing
        if importlib.util.find_spec(_module_for_boot_spec(spec)) is None
    ]
    if still_missing:
        result["ok"] = False
        result["error"] = f"still missing after pip: {', '.join(still_missing)}"
    return result


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


def install_urisys_node(*, python: str | None = None, timeout: float = 600.0) -> dict[str, Any]:
    """GitHub Release wheel (PEP 427 name), then PyPI ``urisys-node`` fallback."""
    attempts: list[dict[str, Any]] = []

    wheel = pip_run(["install", "-U", wheel_url()], python=python, timeout=timeout)
    attempts.append({"source": "github_wheel", "spec": wheel_url(), **wheel})
    if wheel["ok"] and is_importable():
        core = ensure_core_node_packs(python=python, timeout=timeout)
        attempts.append({"source": "core_packs", **core})
        return {
            "ok": core.get("ok", True),
            "source": "github_wheel",
            "spec": wheel_url(),
            "attempts": attempts,
            "core_packs": core,
            **wheel,
        }

    pypi_spec = os.environ.get("URISYS_NODE_PIP_SPEC", "urisys-node>=0.1.3").strip()
    pypi = pip_run(["install", "-U", pypi_spec], python=python, timeout=timeout)
    attempts.append({"source": "pypi", "spec": pypi_spec, **pypi})
    ok = pypi["ok"] and is_importable()
    core = ensure_core_node_packs(python=python, timeout=timeout) if ok else {"ok": False, "skipped": True}
    if ok:
        attempts.append({"source": "core_packs", **core})
        ok = core.get("ok", True)
    return {
        "ok": ok,
        "source": "pypi" if ok else None,
        "spec": pypi_spec if ok else wheel_url(),
        "attempts": attempts,
        "core_packs": core,
        "command": pypi["command"],
        "exit_code": pypi["exit_code"],
        "stdout": pypi["stdout"],
        "stderr": pypi["stderr"],
        "error": None if ok else "urisysnode still not importable after wheel and PyPI install",
    }


def diagnose_urisys_node() -> dict[str, Any]:
    try:
        from importlib.metadata import version

        dist = version("urisys-node")
    except Exception:
        dist = None
    missing = _missing_core_node_modules()
    return {
        "urisys_node_dist": dist,
        "urisysnode_importable": is_importable(),
        "uriscreen_importable": importlib.util.find_spec("uriscreen") is not None,
        "urishell_importable": importlib.util.find_spec("urishell") is not None,
        "missing_core_packs": [_module_for_boot_spec(s) for s in missing],
        "core_pack_specs": list(CORE_NODE_PACK_SPECS),
        "wheel_url": pip_spec(),
        "wheel_filename": wheel_filename(),
        "note": None if is_importable() and not missing else "Run: urisys init  or  pip install --no-deps <uriscreen/urishell wheels>",
    }
