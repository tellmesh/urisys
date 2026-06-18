#!/usr/bin/env bash
# Materialize a UriProcess Markpact + export platform resolver stubs.
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 PATH.markpact.md [--root .markpact] [--platforms linux,server,esp32]" >&2
  exit 1
fi

MARKPACT="$1"
shift
ROOT=".markpact"
PLATFORMS="linux,server,esp32"

while [ $# -gt 0 ]; do
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    --platforms) PLATFORMS="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

export TELLMESH_ROOT="${TELLMESH_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"

echo "== materialize =="
urisys markpact materialize "$MARKPACT" --root "$ROOT" --platforms "$PLATFORMS" --force

echo "== export-platform (standalone index) =="
urisys markpact export-platform "$MARKPACT" --out "${ROOT}/_export" --platforms "$PLATFORMS"

echo "PASS marksync-materialize $MARKPACT"
