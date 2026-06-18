"""Install tellmesh urisys-node from GitHub Release wheel (no git credentials)."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from typing import Any

DEFAULT_GITHUB_OWNER = "tellmesh"
DEFAULT_GITHUB_VERSION = "0.1.29"

CORE_NODE_PACK_SPECS = (
    "https://github.com/tellmesh/uriscreen/releases/download/v0.1.0/uriscreen-0.1.0-py3-none-any.whl",
    "https://github.com/tellmesh/urishell/releases/download/v0.1.0/urishell-0.1.0-py3-none-any.whl",
)


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


def resolve_node_install() -> tuple[str, dict[str, Any]]:
    override = os.environ.get("URISYS_NODE_WHEEL_URL", "").strip()
    if override:
        return override, {"version": github_version(), "source": "env_wheel", "spec": override}
    spec_override = os.environ.get("URISYS_NODE_PIP_SPEC", "").strip()
    if spec_override:
        return spec_override, {"version": None, "source": "env_spec", "spec": spec_override}
    from .version_resolve import resolve_install_spec

    spec, meta = resolve_install_spec(
        dist="urisys-node",
        repo="urisys-node",
        wheel_url_builder=wheel_url,
        fallback_version=github_version(),
        owner=github_owner(),
    )
    return spec, {**meta, "spec": spec}


def pip_spec() -> str:
    """Newest urisys-node install spec (GitHub wheel when newer than PyPI)."""
    return resolve_node_install()[0]


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


def is_importable() -> bool:
    return importlib.util.find_spec("urisysnode") is not None


def _legacy_uninstall(*, python: str | None = None) -> dict[str, Any]:
    """Remove legacy urisysedge + old urisys-node so pip cannot stick on PyPI 0.1.3."""
    return pip_run(["uninstall", "-y", "urisysedge", "urisys-node"], python=python, timeout=120.0)


def _node_version_ok() -> bool:
    try:
        from importlib.metadata import version

        from .defaults import MIN_URISYS_NODE_VERSION
        from .version_resolve import parse_version

        cur = version("urisys-node")
    except Exception:
        return False
    return parse_version(cur) >= parse_version(MIN_URISYS_NODE_VERSION)


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


def _install_specs() -> list[tuple[str, dict[str, Any]]]:
    primary_spec, meta = resolve_node_install()
    specs: list[tuple[str, dict[str, Any]]] = [(primary_spec, meta)]
    if meta.get("source") != "fallback":
        fb = wheel_url(github_version())
        if fb != primary_spec:
            specs.append((fb, {"source": "fallback", "version": github_version(), "spec": fb}))
    return specs


def install_urisys_node(*, python: str | None = None, timeout: float = 600.0) -> dict[str, Any]:
    """Install newest urisys-node (GitHub when newer than squatted PyPI 0.1.3)."""
    attempts: list[dict[str, Any]] = []
    attempts.append({"source": "legacy_uninstall", **_legacy_uninstall(python=python)})

    ok = False
    chosen_spec = pip_spec()
    chosen_meta: dict[str, Any] = {}
    last: dict[str, Any] = {}
    for spec, meta in _install_specs():
        last = pip_run(["install", "-U", spec], python=python, timeout=timeout)
        attempts.append({"source": meta.get("source", "install"), "spec": spec, "meta": meta, **last})
        if last["ok"] and is_importable() and _node_version_ok():
            ok = True
            chosen_spec = spec
            chosen_meta = meta
            break

    core = ensure_core_node_packs(python=python, timeout=timeout) if ok else {"ok": False, "skipped": True}
    if ok:
        attempts.append({"source": "core_packs", **core})
        ok = core.get("ok", True)

    return {
        "ok": ok,
        "source": chosen_meta.get("source"),
        "version": chosen_meta.get("version"),
        "spec": chosen_spec,
        "attempts": attempts,
        "core_packs": core,
        "command": last.get("command"),
        "exit_code": last.get("exit_code"),
        "stdout": last.get("stdout", ""),
        "stderr": last.get("stderr", ""),
        "error": None if ok else "urisys-node still missing or older than required after install",
        "pip_hint": pip_spec(),
    }


def diagnose_urisys_node() -> dict[str, Any]:
    try:
        from importlib.metadata import version

        dist = version("urisys-node")
    except Exception:
        dist = None
    spec, meta = resolve_node_install()
    missing = _missing_core_node_modules()
    return {
        "urisys_node_dist": dist,
        "urisysnode_importable": is_importable(),
        "urisys_node_version_ok": _node_version_ok(),
        "uriscreen_importable": importlib.util.find_spec("uriscreen") is not None,
        "urishell_importable": importlib.util.find_spec("urishell") is not None,
        "missing_core_packs": [_module_for_boot_spec(s) for s in missing],
        "core_pack_specs": list(CORE_NODE_PACK_SPECS),
        "install_spec": spec,
        "install_source": meta.get("source"),
        "pypi_latest": meta.get("pypi"),
        "github_latest": meta.get("github"),
        "pip_hint": spec,
        "note": None if is_importable() and _node_version_ok() and not missing else "Run: urisys init",
    }
