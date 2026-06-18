#!/usr/bin/env bash
# Strict v1alpha analyze for UriProcess Markpacts (warnings = fail).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck source=paths.sh
source "$ROOT/scripts/paths.sh"

PACKS_DIR="${MARKPACT_CONTRACTS_PACKS:-$(markpact_contracts_packs 2>/dev/null || true)}"
if [ -z "$PACKS_DIR" ] || [ ! -d "$PACKS_DIR" ]; then
  echo "ERROR: markpact-contracts/packs not found (set MARKPACT_CONTRACTS_PACKS)" >&2
  exit 1
fi

mapfile -t PROCESS_MARKPACTS < <(
  find "$PACKS_DIR" -maxdepth 1 -name '*process*.markpact.md' | sort
)

if [ "${#PROCESS_MARKPACTS[@]}" -eq 0 ]; then
  echo "WARN: no *process*.markpact.md in $PACKS_DIR" >&2
  exit 0
fi

pass=0
fail=0
for file in "${PROCESS_MARKPACTS[@]}"; do
  if urisys markpact analyze "$file" --strict >/dev/null 2>&1; then
    echo "OK  [strict] $file"
    pass=$((pass + 1))
  else
    echo "FAIL [strict] $file"
    urisys markpact analyze "$file" --strict 2>&1 | head -20
    fail=$((fail + 1))
  fi
done

echo "SUMMARY strict-analyze pass=$pass fail=$fail total=${#PROCESS_MARKPACTS[@]}"
[ "$fail" -eq 0 ]
