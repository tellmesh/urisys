#!/usr/bin/env python3
"""CI guard: no tellmesh package may appear in a ``[real]`` / ``[vision]`` extra.

The "real-backend" extras are meant for pip-installable hardware/runtime libraries
(``mss``, ``Pillow``, ``pyautogui``, ``litellm``, ``pytesseract``). tellmesh capability
packs (``uriscreen``, ``urishell``, ``urikvm`` …) are published only as GitHub release
wheels — not on PyPI — and are provided by the node bootstrap / soft-imported at runtime.

Declaring one in a ``[real]`` extra makes the extra unresolvable by pip/uv (the incident:
``urikvm[real]`` → ``uriscreen`` → ``urisys[kvm]`` unsatisfiable). This guard fails CI if
that pattern reappears. Cross-package *composition* deps elsewhere (uri3→uri2ops, edge packs)
are intentional and resolved via tool.uv.sources, so they are NOT flagged here.

Usage: python scripts/check_no_github_only_deps.py [TELLMESH_ROOT]
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

# Extras that must stay pip-resolvable (real backend libraries only — no tellmesh packs).
BACKEND_EXTRAS = {"real", "vision", "mss"}
TELLMESH_RE = re.compile(r"^(uri[a-z0-9_-]*|urisys[a-z0-9_-]*|nl2uri[a-z0-9_-]*)$")


def dep_name(spec: str) -> str:
    """Distribution name from a PEP 508 spec (strip extras/version/markers/url)."""
    head = spec.split(";", 1)[0].split("@", 1)[0].strip()
    return re.split(r"[<>=!~ \[]", head, maxsplit=1)[0].strip()


def find_violations(root: Path) -> list[tuple[str, str, str]]:
    """Return (project, extra, dep) for every tellmesh package found in a backend extra."""
    violations: list[tuple[str, str, str]] = []
    for pp in sorted(Path(root).glob("*/pyproject.toml")):
        try:
            data = tomllib.loads(pp.read_text(encoding="utf-8"))
        except Exception:
            continue
        proj = data.get("project", {}) or {}
        name = proj.get("name") or pp.parent.name
        for extra, specs in (proj.get("optional-dependencies", {}) or {}).items():
            if extra.lower() not in BACKEND_EXTRAS:
                continue
            for spec in specs or []:
                dn = dep_name(spec)
                if dn and dn != name and TELLMESH_RE.match(dn):
                    violations.append((name, extra, dn))
    return violations


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parents[2]
    violations = find_violations(root)
    if violations:
        print(f"FAIL: tellmesh packages in real-backend extras ({root}):")
        for proj, extra, dn in violations:
            print(f"  ✗ {proj}: [{extra}] -> {dn} (GitHub-only; not pip-resolvable — soft-import + node bootstrap instead)")
        return 1
    print(f"OK: no tellmesh packages in {sorted(BACKEND_EXTRAS)} extras under {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
