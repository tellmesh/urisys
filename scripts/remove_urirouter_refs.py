#!/usr/bin/env python3
"""Replace legacy uriresolver references with uriresolver/uriguard across the monorepo."""

from __future__ import annotations

import re
from pathlib import Path

TELLMESH = Path(__file__).resolve().parents[2]

SKIP_PARTS = {
    ".git",
    ".idea",
    "node_modules",
    "__pycache__",
    "egg-info",
    "dist",
    "build",
    ".venv",
    "SUMD.md",
    "SUMR.md",
    "tree.txt",
}

# Never rewrite squatter-detection code (must keep literal ``urirouter`` dist name).
PROTECTED_SUFFIXES = (
    "urisys/src/urisys/uriguard_install.py",
    "urisys/src/urisys/init_setup.py",
    "urisys/src/urisys/doctor.py",
)

REPLACEMENTS: list[tuple[str, str]] = [
    ("tellmesh/uriresolver", "tellmesh/uriresolver"),
    ("github.com/tellmesh/uriresolver", "github.com/tellmesh/uriresolver"),
    ("uriresolver/src", "uriresolver/src"),
    ("`uri_resolver`", "`uri_resolver`"),
    ("uri_resolver", "uri_resolver"),
    ("`uriresolver`", "`uriresolver`"),
    ("uriresolver, uriguard, uricontrol", "uriresolver, uriguard, uricontrol"),
    ("uriresolver, uriguard, uricontrol", "uriresolver, uriguard, uricontrol"),
    ("uriresolver + uriguard + uricontrol", "uriresolver + uriguard + uricontrol"),
    ("uriresolver/uriguard/uricontrol", "uriresolver/uriguard/uricontrol"),
    ("uriresolver, uriguard, uricontrol,", "uriresolver, uriguard, uricontrol,"),
    ("uriresolver, uriguard, uricontrol ", "uriresolver, uriguard, uricontrol "),
    ("`uricore`, `uriresolver`", "`uricontrol`, `uriresolver`, `uriguard`"),
    ("uriresolver, uriguard, uricontrol, ", "uriresolver, uriguard, uricontrol, "),
    ("uriresolver, uriguard, uricontrol", "uriresolver, uriguard, uricontrol"),
    ("COPY uriresolver", "COPY uriresolver"),
    ("COPY uricontrol", "COPY uricontrol"),
    ("/build/uriresolver", "/build/uriresolver"),
    ("/build/uricontrol", "/build/uricontrol"),
    ("-e /build/uriresolver", "-e /build/uriresolver -e /build/uriguard"),
    ("-e /build/uricontrol", "-e /build/uricontrol"),
    ("&& (candidate / \"uriresolver\")", "&& (candidate / \"uriresolver\")"),
    ("uriguard_install", "uriguard_install"),
    ("diagnose_uriguard", "diagnose_uriguard"),
    ("test_uriguard_install", "test_uriguard_install"),
]

# Whole-word uriresolver → uriresolver only when not already handled
WORD_URIRouter = re.compile(r"\burirouter\b")


def should_skip(path: Path) -> bool:
    rel = str(path.relative_to(TELLMESH)).replace("\\", "/")
    if any(rel.endswith(s) for s in PROTECTED_SUFFIXES):
        return True
    parts = set(path.parts)
    if any(p in parts for p in SKIP_PARTS):
        return True
    if path.name in SKIP_PARTS:
        return True
    if path.suffix in {".pyc", ".png", ".jpg", ".whl"}:
        return True
    return False


def transform(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    # Remaining bare uriresolver (e.g. dependency lists)
    text = WORD_URIRouter.sub("uriresolver", text)
    return text


def main() -> None:
    updated = 0
    for path in TELLMESH.rglob("*"):
        if not path.is_file() or should_skip(path):
            continue
        if path.suffix not in {
            ".md",
            ".py",
            ".sh",
            ".yml",
            ".yaml",
            ".toml",
            ".less",
            ".txt",
            "Dockerfile",
        } and path.name not in {"Dockerfile", "Dockerfile.gui"}:
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if "uriresolver" not in original and "uri_resolver" not in original:
            continue
        new = transform(original)
        if new != original:
            path.write_text(new, encoding="utf-8")
            updated += 1
            print("updated", path.relative_to(TELLMESH))
    print(f"Done: {updated} files")


if __name__ == "__main__":
    main()
