#!/usr/bin/env bash
# Strict operation names on generated thin markpacts (manifest-aligned).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== generate_pack_markpacts --check =="
python3 scripts/generate_pack_markpacts.py --check

echo "== analyze thin markpacts (--strict-operations) =="
mapfile -t FILES < <(find "$TELLMESH_ROOT" -path '*/markpacts/*.markpact.md' \
  ! -path '*/legacy/*' ! -name '*.contract.markpact.md' ! -name '*.pack.markpact.md' 2>/dev/null | sort)

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
