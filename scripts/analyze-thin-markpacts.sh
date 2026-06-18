#!/usr/bin/env bash
# Strict operation names on generated thin markpacts (manifest-aligned).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== generate_pack_markpacts --check =="
python3 scripts/generate_pack_markpacts.py --check

echo "== analyze thin markpacts (--strict-operations) =="
mapfile -t FILES < <(python3 - <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, str(Path("scripts").resolve()))
from generate_pack_markpacts import EXTRA_PACK_DIRS, SKIP_PACKS, generate_for_spec, _extra_specs
from pack_registry import pack_specs

specs = {**pack_specs(), **_extra_specs()}
paths: list[Path] = []
for name, spec in sorted(specs.items()):
    if name in SKIP_PACKS:
        continue
    try:
        paths.extend(out for out, _ in generate_for_spec(spec))
    except Exception as exc:
        print(f"SKIP {name}: {exc}", file=sys.stderr)
for p in sorted(paths):
    if p.is_file():
        print(p)
PY
)

pass=0
fail=0
for file in "${FILES[@]}"; do
  if urisys markpact analyze "$file" --strict-operations >/dev/null 2>&1; then
    pass=$((pass + 1))
  else
    echo "FAIL $file"
    urisys markpact analyze "$file" --strict-operations 2>&1 | head -8
    fail=$((fail + 1))
  fi
done

echo "SUMMARY thin-operations pass=$pass fail=$fail total=${#FILES[@]}"
[ "$fail" -eq 0 ]
