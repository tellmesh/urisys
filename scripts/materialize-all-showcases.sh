#!/usr/bin/env bash
# Materialize thin pack markpacts → .markpact/{package_id}/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=paths.sh
source "$ROOT/scripts/paths.sh"

export TELLMESH_ROOT="${TELLMESH_ROOT:-$(tellmesh_root 2>/dev/null || cd "$ROOT/.." && pwd)}"
MARKPACT_ROOT="${MARKPACT_ROOT:-.markpact}"
cd "$ROOT"

pass=0
fail=0

collect_thin() {
  if tm="$(tellmesh_root 2>/dev/null)"; then
    for repo in "$tm"/uri* "$tm"/uriimg2nl; do
      [ -d "$repo/markpacts" ] || continue
      find "$repo/markpacts" -name '*.markpact.md' \
        ! -path '*/legacy/*' \
        ! -name '*.contract.markpact.md' \
        ! -name '*.bundle.markpact.md' \
        ! -name '*.pack.markpact.md' \
        ! -name '*.showcase.markpact.md' \
        -print 2>/dev/null || true
    done
  fi
  if packs="$(markpact_contracts_packs 2>/dev/null)"; then
    find "$packs" -maxdepth 1 -name '*.markpact.md' \
      ! -name '*.showcase.markpact.md' -print 2>/dev/null || true
  fi
}

mapfile -t FILES < <(collect_thin | sort -u)

for file in "${FILES[@]}"; do
  [ -f "$file" ] || continue
  name=$(basename "$file")
  if urisys markpact materialize "$file" --root "$MARKPACT_ROOT" --force >/tmp/mat-$$.json 2>&1; then
    id=$(python3 -c "import json; print(json.load(open('/tmp/mat-$$.json'))['materialized']['package_id'])")
    echo "OK  $name → $MARKPACT_ROOT/$id"
    pass=$((pass + 1))
  else
    echo "FAIL $name"
    cat /tmp/mat-$$.json
    fail=$((fail + 1))
  fi
done
rm -f /tmp/mat-$$.json

echo "SUMMARY materialized=$pass failed=$fail root=$MARKPACT_ROOT"
exit $(( fail > 0 ? 1 : 0 ))
