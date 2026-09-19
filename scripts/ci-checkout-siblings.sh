#!/usr/bin/env bash
# Clone tellmesh sibling repos next to urisys (CI + fresh checkout).
#
# Layout after run:
#   ${TELLMESH_ROOT}/urisys/
#   ${TELLMESH_ROOT}/uricontrol/
#   ${TELLMESH_ROOT}/urikvm/
#   ...
#
# Usage (from urisys repo):
#   bash scripts/ci-checkout-siblings.sh
#   TELLMESH_ROOT=/home/runner/work/urisys bash scripts/ci-checkout-siblings.sh
set -euo pipefail

URISYS_ROOT="${URISYS_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
TELLMESH_ROOT="${TELLMESH_ROOT:-$(dirname "$URISYS_ROOT")}"
ORG="${TELLMESH_ORG:-tellmesh}"
BRANCH="${TELLMESH_BRANCH:-main}"
# main still publishes the old uricore distribution; use the renamed release.
URICONTROL_REF="${TELLMESH_URICONTROL_REF:-v0.1.14}"

# Minimal set for urisys pip install + drift guard
CORE_REPOS=(
  uriguard uriresolver uritransport
  uricontrol
  urioperators
  urisys-node urisys-dev
)

# kvm / rdp docker builds + handler unit tests
KVM_REPOS=(
  urikvm urihim uriocr urillm urimail urioffice urivql urikvmedge
  urirdp urirdpedge urienv uribrowser uristepper uristepperedge urisys-automation-lab
  urikvm-docker urirdp-docker
)

# Markpact capability packs (thin generated copies + legacy showcase archive)
MARKPACT_REPOS=(
  urishell uriscreen urimessage uriwebrtc uristt urikv uriimg2nl
  markpact-contracts
)

REPOS=("${CORE_REPOS[@]}" "${KVM_REPOS[@]}" "${MARKPACT_REPOS[@]}")

clone_repo() {
  local name="$1"
  local dest="${TELLMESH_ROOT}/${name}"
  local ref="${BRANCH}"
  if [ "${name}" = uricontrol ]; then ref="${URICONTROL_REF}"; fi
  if [ -e "${dest}/.git" ] || [ -f "${dest}/pyproject.toml" ]; then
    echo "skip ${name}: already present at ${dest}"
    return 0
  fi
  echo "clone ${ORG}/${name} → ${dest}"
  git clone --depth 1 --branch "${ref}" "https://github.com/${ORG}/${name}.git" "${dest}"
}

missing=0
for repo in "${REPOS[@]}"; do
  clone_repo "${repo}" || missing=$((missing + 1))
done
if [ "${missing}" -ne 0 ]; then
  echo "error: ${missing} required sibling repositories unavailable" >&2
  exit 1
fi
echo "sibling checkout done"

echo "tellmesh workspace ready at ${TELLMESH_ROOT}"
