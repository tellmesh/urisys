#!/usr/bin/env bash
# Strict operation names on standalone Markpact packs in markpact-contracts (not thin-generated).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck source=paths.sh
source "$ROOT/scripts/paths.sh"

PACKS_DIR="$(markpact_contracts_packs 2>/dev/null || echo "${MARKPACT_CONTRACTS_PACKS:-}")"
if [ -z "$PACKS_DIR" ] || [ ! -d "$PACKS_DIR" ]; then
  echo "SKIP: markpact-contracts/packs not found"
  exit 0
fi

LEGACY=(
  uribrowser.markpact.md
  uribrowser.showcase.markpact.md
  uristepper.pack.markpact.md
  uriprinter.markpact.md
  uridocker.markpact.md
  urisystemd.markpact.md
  uriusb.markpact.md
  uridom-js.markpact.md
)

pass=0
fail=0
for name in "${LEGACY[@]}"; do
  file="$PACKS_DIR/$name"
  [ -f "$file" ] || { echo "SKIP missing $name"; continue; }
  if urisys markpact analyze "$file" --strict-operations >/dev/null 2>&1; then
    pass=$((pass + 1))
    echo "OK  $name"
  else
    echo "FAIL $name"
    urisys markpact analyze "$file" --strict-operations 2>&1 | head -8
    fail=$((fail + 1))
  fi
done

echo "SUMMARY legacy-contract-operations pass=$pass fail=$fail total=${#LEGACY[@]}"
[ "$fail" -eq 0 ]
