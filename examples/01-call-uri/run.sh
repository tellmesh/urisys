#!/usr/bin/env bash
set -euo pipefail

urisys --packs browser call "browser://default/page/open" \
  --payload '{"url":"https://example.com"}' \
  --approve

urisys --packs docker call "docker://container/web/command/restart" \
  --approve \
  --dry-run
