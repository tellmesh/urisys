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

# Minimal set for urisys pip install + drift guard
CORE_REPOS=(
  uricontrol
  urioperators
  urisys-node
)

# kvm / rdp docker builds + handler unit tests
KVM_REPOS=(
  urikvm urihim uriocr urillm urimail urioffice urivql urikvmedge
  urirdp urienv uribrowser uristepper urisys-automation-lab
)

# Markpact capability packs (thin generated copies + legacy showcase archive)
MARKPACT_REPOS=(
  urichat urishell uriscreen urimessage uriwebrtc uristt urikv uriimg2nl
)

REPOS=("${CORE_REPOS[@]}" "${KVM_REPOS[@]}" "${MARKPACT_REPOS[@]}")

clone_repo() {
  local name="$1"
  local dest="${TELLMESH_ROOT}/${name}"
  if [ -d "${dest}/.git" ] || [ -f "${dest}/pyproject.toml" ]; then
    echo "skip ${name}: already present at ${dest}"
    return 0
  fi
  echo "clone ${ORG}/${name} → ${dest}"
  # Tolerant: a missing/private/renamed sibling (e.g. urioperators) must not abort the whole
  # checkout — callers run on whatever cloned. ``git clone`` failures are warned, not fatal.
  if ! git clone --depth 1 --branch "${BRANCH}" "https://github.com/${ORG}/${name}.git" "${dest}" 2>&1; then
    echo "::warning::skip ${ORG}/${name}: clone failed (missing/private/renamed) — continuing"
    return 0
  fi
}

missing=0
for repo in "${REPOS[@]}"; do
  clone_repo "${repo}" || missing=$((missing + 1))
done
echo "sibling checkout done (${missing} unavailable)"

echo "tellmesh workspace ready at ${TELLMESH_ROOT}"
