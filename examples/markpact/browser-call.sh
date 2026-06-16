#!/usr/bin/env bash
set -euo pipefail
urisys --packs none \
  --markpact markpacts/packs/uribrowser.markpact.md \
  call browser://default/page/open \
  --payload '{"url":"https://example.com"}' \
  --approve \
  --dry-run
