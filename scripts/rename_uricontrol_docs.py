#!/usr/bin/env python3
"""Rename legacy uricore references to uricontrol in docs and CI (not Python modules)."""

from __future__ import annotations

import re
from pathlib import Path

TELLMESH = Path(__file__).resolve().parents[2]

# Only touch documentation / CI — never rename uricore_install.py etc.
GLOBS = (
    "**/docs/**/*.md",
    "**/README.md",
    "**/.github/workflows/*.yml",
    "**/.github/workflows/*.yaml",
    "markpact-contracts/**/*.md",
    "uri-packs/README.md",
)

SKIP_FILES = frozenset(
    {
        "urisys/docs/MIGRATION-STEP1.md",  # historical migration narrative
        "urisys/docs/MIGRATION-STEP2.md",
        "urisys/docs/MIGRATION-STEP3.md",
    }
)

REPLACEMENTS: list[tuple[str, str]] = [
    ("tellmesh/uricore", "tellmesh/uricontrol"),
    ("../uricore/", "../uricontrol/"),
    ("`uricore` (`uri_control.edge`)", "`uricontrol` (`uri_control.edge`)"),
    ("w pakiecie **`uricore`**", "w pakiecie **`uricontrol`**"),
    ("pakiet **`uricore`**", "pakiet **`uricontrol`**"),
    ("pakiecie `uricore`", "pakiecie `uricontrol`"),
    ("Runtime: `uri_control.edge` via `uricore`", "Runtime: `uri_control.edge` via `uricontrol`"),
    ("`uri_control.edge` (`uricore`)", "`uri_control.edge` (`uricontrol`)"),
    ("urirouter, uricore,", "urirouter, uricontrol,"),
    ("urirouter, uricore ", "urirouter, uricontrol "),
    ("Zależności** | `uricore`", "Zależności** | `uricontrol`"),
    ("Zależność** | `uricore", "Zależność** | `uricontrol"),
    ('pip install "uricore>=', 'pip install "uricontrol>='),
    ("pip install uricore", "pip install uricontrol"),
    ("uricore>=0.1.", "uricontrol>=0.1."),
    ("**[uricore]", "**[uricontrol]"),
    ("runtime to **uricore**", "runtime to **uricontrol**"),
    ("Runtime: **[uricore]", "Runtime: **[uricontrol]"),
    ("# uricore", "# uricontrol"),
    ("repos: `uricore`", "repos: `uricontrol`"),
    ("`uricore`, `urirouter`", "`uricontrol`, `urirouter`"),
    ("Wymaga sklonowanych sąsiadujących repozytoriów: `uricore`", "Wymaga sklonowanych sąsiadujących repozytoriów: `uricontrol`"),
    ("packages/python/urisysedge", "uricontrol/core/python/uri_control/edge"),
    ("tellmesh/urisysedge", "tellmesh/uricontrol"),
    ("urisysedge", "`uri_control.edge`"),
]

# Fix over-replacement in migration docs path - handled by SKIP

REPO_KEY_RE = re.compile(r'\b"uricore"\s*:')


def should_process(path: Path) -> bool:
    try:
        rel = path.relative_to(TELLMESH).as_posix()
    except ValueError:
        return False
    if rel in SKIP_FILES:
        return False
    if "/src/" in rel or "/tests/" in rel:
        return False
    if rel.endswith("uricore_install.py"):
        return False
    return True


def apply(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text


def main() -> None:
    updated = 0
    for pattern in GLOBS:
        for path in TELLMESH.glob(pattern):
            if not path.is_file() or not should_process(path):
                continue
            original = path.read_text(encoding="utf-8")
            new = apply(original)
            if new != original:
                path.write_text(new, encoding="utf-8")
                updated += 1
                print("updated", path.relative_to(TELLMESH))
    print(f"Done: {updated} files")


if __name__ == "__main__":
    main()
