#!/usr/bin/env bash
# Validate all *.markpact.md files in the urisys monorepo.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mapfile -t FILES < <(find . -path './.urisys/*' -prune -o -name '*.markpact.md' -print | sort)

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
