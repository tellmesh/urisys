"""Install/repair urisysedge when metadata exists but import fails."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from typing import Any


def is_importable() -> bool:
    return importlib.util.find_spec("urisysedge") is not None


def _dist_version() -> str | None:
    try:
        from importlib.metadata import version

        return version("urisysedge")
    except Exception:
        return None


def is_broken_install() -> bool:
    """True when pip metadata exists but ``import urisysedge`` fails."""
    return _dist_version() is not None and not is_importable()


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


def repair_urisysedge(*, python: str | None = None, force: bool = False) -> dict[str, Any]:
    """Reinstall urisysedge when import fails (common after partial pip uninstall)."""
    if is_importable() and not force:
        return {"ok": True, "already": True, "dist": _dist_version()}

    steps: list[dict[str, Any]] = []
    if is_broken_install():
        uninstall = pip_run(["uninstall", "-y", "urisysedge"], python=python)
        steps.append({"name": "pip_uninstall_urisysedge", **uninstall})

    install = pip_run(["install", "--force-reinstall", "urisysedge>=0.1.0"], python=python)
    steps.append({"name": "pip_install_urisysedge", **install})
    ok = install["ok"] and is_importable()
    return {
        "ok": ok,
        "steps": steps,
        "dist": _dist_version(),
        "broken_before": is_broken_install() if not ok else False,
        "pip_hint": "pip install --force-reinstall urisysedge>=0.1.0",
        "error": None if ok else "urisysedge still not importable after repair",
    }


def ensure_urisysedge(*, python: str | None = None) -> dict[str, Any]:
    if is_importable():
        return {"ok": True, "already": True, "dist": _dist_version()}
    if is_broken_install():
        return repair_urisysedge(python=python)
    install = pip_run(["install", "-U", "urisysedge>=0.1.0"], python=python)
    install["already"] = False
    install["importable"] = is_importable()
    install["ok"] = install["ok"] and install["importable"]
    if not install["ok"]:
        repair = repair_urisysedge(python=python)
        install["repair"] = repair
        install["ok"] = repair.get("ok", False)
    return install
