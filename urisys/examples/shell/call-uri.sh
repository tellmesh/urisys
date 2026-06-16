#!/usr/bin/env bash
set -euo pipefail

urisys call "browser://default/page/open"       --packs browser       --payload '{"url":"https://example.com"}'       --approve

urisys call "docker://container/web/command/restart"       --packs docker       --approve       --dry-run
