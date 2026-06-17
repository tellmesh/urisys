#!/usr/bin/env bash
# Sync vendored capability packs: urisys monorepo → tellmesh/{pack} repos.
#
# Usage:
#   bash scripts/sync-vendored-pack.sh urihim urillm
#   bash scripts/sync-vendored-pack.sh --all
#   bash scripts/sync-vendored-pack.sh --check --all
#   bash scripts/sync-vendored-pack.sh --init urimail urioffice urivql
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

if [ "${1:-}" = "--check" ]; then
  shift
  exec python3 scripts/pack_sync.py check "$@"
fi

if [ "${1:-}" = "--promote" ]; then
  shift
  exec python3 scripts/pack_sync.py promote "$@"
fi

if [ "${1:-}" = "--init" ]; then
  shift
  exec python3 scripts/pack_sync.py init-repo "$@"
fi

if [ "${1:-}" = "--all" ]; then
  exec python3 scripts/pack_sync.py to-repo --all
fi

if [ $# -eq 0 ]; then
  echo "usage: sync-vendored-pack.sh [--all|--check|--init] [pack...]" >&2
  exit 1
fi

exec python3 scripts/pack_sync.py to-repo "$@"
