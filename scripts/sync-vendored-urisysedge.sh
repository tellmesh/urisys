#!/usr/bin/env bash
# Copy canonical urisysedge into urisys-node vendored path (standalone wheel builds).
# Tellmesh repo sync: bash scripts/sync-vendored-pack.sh urisysedge
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${ROOT}/packages/python/urisysedge"
DST="${ROOT}/urisys-node/packages/python/urisysedge"
if [ ! -d "${SRC}" ]; then
  echo "error: canonical urisysedge missing at ${SRC}" >&2
  exit 1
fi
mkdir -p "${DST}"
for f in __init__.py runtime.py env.py; do
  cp "${SRC}/${f}" "${DST}/${f}"
done
echo "synced urisysedge → ${DST}"
