#!/usr/bin/env bash
# Full tellmesh workspace regression (uricore + urisys + edge stacks).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TELLMESH="${TELLMESH_ROOT:-$(cd "$ROOT/.." && pwd)}"

export PYTHONPATH="${TELLMESH}/urisys/src:${TELLMESH}/urisysedge:${TELLMESH}/uricore/core/python"
export TELLMESH_ROOT="${TELLMESH}"

cd "${TELLMESH}"

echo "== markpact CI =="
bash urisys/scripts/run-markpact-ci.sh

echo "== full pytest =="
python3 -m pytest \
  uricore/tests \
  urisys/tests \
  urisysedge/tests \
  urikvmedge/tests \
  -q

echo "== pack_sync =="
python3 urisys/scripts/pack_sync.py check --all

echo "PASS full-regression"
