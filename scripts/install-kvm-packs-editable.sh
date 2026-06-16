#!/usr/bin/env bash
# Editable install of urisysedge + kvm/him/ocr/llm from tellmesh sibling repos.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TELLMESH="$(cd "$ROOT/.." && pwd)"
cd "$ROOT"
pip install -e "$TELLMESH/urisysedge"
for pkg in urikvm urihim uriocr; do
  pip install -e "$TELLMESH/${pkg}[real]" 2>/dev/null || \
  pip install -e "$TELLMESH/$pkg"
done
pip install -e "$TELLMESH/urillm[vision]" 2>/dev/null || \
  pip install -e "$TELLMESH/urillm"
echo "OK: urisysedge + urikvm urihim uriocr urillm (editable from tellmesh/*)"
echo "Start node: URISYS_NODE_ALLOW_PACK_LOAD=1 URISYS_NODE_PACKS=node,screen,kvm,him urisys-node serve --port 8790"
