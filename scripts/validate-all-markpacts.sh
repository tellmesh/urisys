#!/usr/bin/env bash
# Validate all *.markpact.md files (contracts + in-repo docker/node markpacts).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck source=paths.sh
source "$ROOT/scripts/paths.sh"

mapfile -t FILES < <(
  {
    if packs="$(markpact_contracts_packs 2>/dev/null)"; then
      find "$packs" -maxdepth 1 -name '*.markpact.md' -print
    elif [ -n "${MARKPACT_CONTRACTS_PACKS:-}" ] && [ -d "$MARKPACT_CONTRACTS_PACKS" ]; then
      find "$MARKPACT_CONTRACTS_PACKS" -maxdepth 1 -name '*.markpact.md' -print
    else
      echo "WARN: markpact-contracts/packs not found — skipping shared packs" >&2
    fi
    find . -path './.urisys/*' -prune -o -path './markpacts/packs/*' -prune -o -name '*.markpact.md' -print
  } | sort -u
)

pass=0
fail=0
failed=()

for file in "${FILES[@]}"; do
  if result="$(urisys markpact validate "$file" 2>&1)"; then
    if echo "$result" | grep -q '"ok": true'; then
      pass=$((pass + 1))
      kind=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin).get('kind','pack'))" 2>/dev/null || echo pack)
      echo "OK  [$kind] $file"
    else
      fail=$((fail + 1))
      failed+=("$file")
      echo "FAIL $file"
      echo "$result" | head -5
    fi
  else
    fail=$((fail + 1))
    failed+=("$file")
    echo "FAIL $file"
    echo "$result" | head -5
  fi
done

echo
echo "SUMMARY pass=$pass fail=$fail total=${#FILES[@]}"
if (( fail > 0 )); then
  printf 'Failed:\n'
  printf ' - %s\n' "${failed[@]}"
  exit 1
fi
