#!/usr/bin/env bash
# Editable install kvm packs from tellmesh sibling repos (dev workstation).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TELLMESH="$(dirname "$ROOT")"

pip install -e "${TELLMESH}/urisysedge"
for pkg in urikvm urihim uriocr urillm urimail urioffice urivql; do
  pip install -e "${TELLMESH}/${pkg}[real]" 2>/dev/null || pip install -e "${TELLMESH}/${pkg}"
done
pip install -e "${TELLMESH}/urillm[vision]" 2>/dev/null || true
echo "OK: kvm packs installed editable from ${TELLMESH}"
