#!/usr/bin/env bash
# Editable install of urisysedge + kvm/him/ocr/llm from urisys monorepo (vendored copies).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
pip install -e packages/python/urisysedge
for pkg in urikvm urihim uriocr; do
  pip install -e "urikvm-docker/packages/python/${pkg}[real]" 2>/dev/null || \
  pip install -e "urikvm-docker/packages/python/${pkg}"
done
pip install -e "urikvm-docker/packages/python/urillm[vision]" 2>/dev/null || \
  pip install -e "urikvm-docker/packages/python/urillm"
echo "OK: urisysedge + urikvm urihim uriocr urillm (editable, monorepo)"
echo "Start node: URISYS_NODE_ALLOW_PACK_LOAD=1 URISYS_NODE_PACKS=node,screen,kvm,him urisys-node serve --port 8790"
