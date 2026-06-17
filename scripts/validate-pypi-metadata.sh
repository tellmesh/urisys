#!/usr/bin/env bash
# Fail if built wheel/sdist metadata contains direct URL deps (PyPI rejects them).
#
# Usage:
#   bash scripts/validate-pypi-metadata.sh
#   bash scripts/validate-pypi-metadata.sh dist/urisys-0.1.35*
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

shopt -s nullglob
artifacts=("$@")
if ((${#artifacts[@]} == 0)); then
  artifacts=(dist/urisys-*.whl dist/urisys-*.tar.gz)
fi
if ((${#artifacts[@]} == 0)); then
  echo "no dist/urisys-* artifacts — run: python -m build" >&2
  exit 1
fi

python3 - <<'PY' "${artifacts[@]}"
import email.policy
import sys
import tarfile
import zipfile
from pathlib import Path

bad: list[str] = []

def check_metadata(text: str, label: str) -> None:
    for line in text.splitlines():
        if not line.startswith("Requires-Dist:"):
            continue
        if " @ " in line:
            bad.append(f"{label}: {line.strip()}")

for path in map(Path, sys.argv[1:]):
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as zf:
            meta_name = next(n for n in zf.namelist() if n.endswith(".dist-info/METADATA"))
            check_metadata(zf.read(meta_name).decode(), str(path))
    elif path.suffix == ".gz":
        with tarfile.open(path, "r:gz") as tf:
            meta = next(m for m in tf.getmembers() if m.name.endswith("PKG-INFO"))
            check_metadata(tf.extractfile(meta).read().decode(), str(path))
    else:
        raise SystemExit(f"unsupported artifact: {path}")

if bad:
    print("PyPI metadata invalid (direct URL dependencies not allowed):", file=sys.stderr)
    for line in bad:
        print(f"  {line}", file=sys.stderr)
    print(
        "\nFix pyproject.toml: use version specifiers only. "
        "Install tellmesh uricore via `urisys init` (see uricore_install.py).",
        file=sys.stderr,
    )
    raise SystemExit(1)

print(f"OK: {len(sys.argv)-1} artifact(s) — no direct URL Requires-Dist")
PY
