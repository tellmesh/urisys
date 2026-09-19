#!/usr/bin/env bash
# Resolve sibling dependencies together, including the local urisys candidate.
set -euo pipefail
URISYS_ROOT="${URISYS_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
TELLMESH_ROOT="${TELLMESH_ROOT:-$(dirname "$URISYS_ROOT")}"

args=(-e "${URISYS_ROOT}")
for repo in uriguard uriresolver uritransport uricontrol urioperators urisys-node urisys-dev \
  urikvm urihim uriocr urillm urikvmedge urirdp urishell uriscreen urimessage uristepper; do
  path="${TELLMESH_ROOT}/${repo}"
  if [ ! -f "${path}/pyproject.toml" ]; then
    echo "error: missing ${path}/pyproject.toml — run ci-checkout-siblings.sh first" >&2
    exit 1
  fi
  args+=(-e "${path}")
done
# A single resolver transaction prevents PyPI fallback for local dependencies.
python -m pip install -q pytest "${args[@]}"
echo "sibling packs installed from ${TELLMESH_ROOT}"
