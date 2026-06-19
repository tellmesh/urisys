#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck source=../../scripts/paths.sh
source "$ROOT/scripts/paths.sh"
PACK="$(markpact_contracts_packs)/uribrowser.markpact.md"
urisys --packs none \
  --markpact "$PACK" \
  call browser://default/page/open \
  --payload '{"url":"https://example.com"}' \
  --approve \
  --dry-run
