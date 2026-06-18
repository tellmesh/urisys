#!/usr/bin/env bash
# pip install -e tellmesh sibling packs required for urisys dev/CI tests.
set -euo pipefail

URISYS_ROOT="${URISYS_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
TELLMESH_ROOT="${TELLMESH_ROOT:-$(dirname "$URISYS_ROOT")}"

install_editable() {
  local name="$1"
  local path="${TELLMESH_ROOT}/${name}"
  if [ -f "${path}/pyproject.toml" ]; then
    pip install -q -e "${path}"
  else
    echo "warn: missing ${path}/pyproject.toml — run ci-checkout-siblings.sh first" >&2
  fi
}

# Core stack for urisys + node tests
for repo in uricontrol urioperators urisys-node; do
  install_editable "${repo}"
done

# Optional extras (kvm handler tests)
for repo in urikvm urihim uriocr urillm urikvmedge urirdp; do
  install_editable "${repo}" || true
done

echo "sibling packs installed from ${TELLMESH_ROOT}"
