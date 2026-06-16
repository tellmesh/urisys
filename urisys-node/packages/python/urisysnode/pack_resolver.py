"""Lazy PyPI install for optional urisys-node capability packs."""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
from typing import Any

# pack alias -> module exposing register(runtime)
PACK_MODULES: dict[str, str] = {
    "node": "urisysnode.routes",
    "screen": "uriscreen.routes",
    "kvm": "urikvm",
    "him": "urihim",
    "ocr": "uriocr",
    "llm": "urillm",
}

CORE_PACKS = frozenset({"node"})
PACK_PYPI: dict[str, str] = {
    "urisysedge": "urisysedge>=0.1.0",
    "kvm": "urikvm>=0.1.0",
    "him": "urihim>=0.1.0",
    "ocr": "uriocr>=0.1.0",
    "llm": "urillm[vision]>=0.1.0",
}

# URI scheme -> pack alias (screen/uriscreen is bundled with urisys wheel)
SCHEME_TO_PACK: dict[str, str] = {
    "kvm": "kvm",
    "him": "him",
    "ocr": "ocr",
    "llm": "llm",
}

# Real backends: extra pip specs when handler needs mss/pyautogui/etc.
REAL_PIP: dict[str, list[str]] = {
    "screen": ["mss>=9.0", "Pillow>=10.0"],
    "kvm": ["mss>=9.0", "Pillow>=10.0"],
    "him": ["pyautogui>=0.9.54"],
    "ocr": ["pytesseract>=0.3.10", "Pillow>=10.0"],
    "llm": ["litellm>=1.40"],
}


def auto_install_enabled() -> bool:
    return os.environ.get("URISYS_NODE_AUTO_INSTALL", "1") == "1"


def pack_module(pack: str) -> str:
    return PACK_MODULES.get(pack, pack)


def scheme_for_uri(uri: str) -> str:
    return uri.split("://", 1)[0].lower() if "://" in uri else ""


def pack_for_scheme(scheme: str) -> str | None:
    return SCHEME_TO_PACK.get(scheme)


def _pip_install(specs: list[str]) -> dict[str, Any]:
    cmd = [sys.executable, "-m", "pip", "install", "-U", *specs]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    return {
        "ok": proc.returncode == 0,
        "command": " ".join(cmd),
        "stdout": (proc.stdout or "")[-2000:],
        "stderr": (proc.stderr or "")[-2000:],
        "exit_code": proc.returncode,
    }


def ensure_pip_specs(specs: list[str], *, install: bool = True) -> dict[str, Any]:
    if not specs:
        return {"ok": True, "installed": [], "skipped": True}
    if not install or not auto_install_enabled():
        return {
            "ok": False,
            "error": "auto install disabled (URISYS_NODE_AUTO_INSTALL=0)",
            "specs": specs,
        }
    result = _pip_install(specs)
    result["specs"] = specs
    return result


def ensure_pack_pypi(pack: str, *, install: bool = True) -> dict[str, Any]:
    """Install pack + urisysedge dependency from PyPI when import would fail."""
    specs: list[str] = []
    if pack != "urisysedge":
        specs.append(PACK_PYPI.get("urisysedge", "urisysedge>=0.1.0"))
    spec = PACK_PYPI.get(pack)
    if spec:
        specs.append(spec)
    elif pack not in ("node", "screen"):
        return {"ok": False, "error": f"no PyPI mapping for pack {pack!r}"}
    else:
        return {"ok": True, "pack": pack, "skipped": True, "reason": "bundled in urisys"}
    out = ensure_pip_specs(specs, install=install)
    out["pack"] = pack
    return out


def ensure_real_deps(pack: str, *, install: bool = True) -> dict[str, Any]:
    specs = REAL_PIP.get(pack, [])
    out = ensure_pip_specs(specs, install=install)
    out["pack"] = pack
    out["real"] = True
    return out


def import_pack_module(pack: str):
    module_name = pack_module(pack)
    return importlib.import_module(module_name)


def pack_importable(pack: str) -> bool:
    try:
        import_pack_module(pack)
        return True
    except ModuleNotFoundError:
        return False
