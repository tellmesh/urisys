"""Helpers to undo markpact unpack pollution of sys.modules / sys.path."""

from __future__ import annotations

import sys

_EMBEDDED_PACK_PREFIXES = (
    "uristepper",
    "urikvm",
    "urienv",
    "urishell",
    "uribrowser",
    "urichat",
    "uriocr",
    "urillm",
    "urihim",
    "urikv",
    "urimail",
    "urioffice",
)


def _is_embedded_pack_module(name: str) -> bool:
    return name in _EMBEDDED_PACK_PREFIXES or any(
        name.startswith(f"{prefix}.") for prefix in _EMBEDDED_PACK_PREFIXES
    )


def _is_ephemeral_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return "/pytest-" in normalized or "/.markpact/" in normalized


def reset_embedded_pack_imports() -> None:
    """Remove pack modules loaded from ephemeral markpact unpack dirs."""
    for name in list(sys.modules):
        if not _is_embedded_pack_module(name):
            continue
        mod = sys.modules.get(name)
        file = getattr(mod, "__file__", "") or ""
        if file and _is_ephemeral_path(file):
            del sys.modules[name]
    sys.path[:] = [p for p in sys.path if not _is_ephemeral_path(p)]
