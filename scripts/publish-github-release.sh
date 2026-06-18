#!/usr/bin/env bash
# Upload dist/* for current VERSION to tellmesh/urisys GitHub Releases (parallel channel).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VER="$(tr -d '[:space:]' < "$ROOT/VERSION")"
TAG="v${VER}"
OWNER="${GITHUB_OWNER:-tellmesh}"
REPO="${GITHUB_REPO:-urisys}"

if ! command -v gh >/dev/null 2>&1; then
  echo "SKIP: gh CLI missing"
  exit 0
fi

shopt -s nullglob
assets=("$ROOT/dist/urisys-${VER}"*)
if [ "${#assets[@]}" -eq 0 ]; then
  echo "SKIP: no dist/urisys-${VER}* (run: python -m build)"
  exit 0
fi

gh release view "$TAG" -R "${OWNER}/${REPO}" >/dev/null 2>&1 || \
  gh release create "$TAG" -R "${OWNER}/${REPO}" \
    --title "urisys ${TAG}" \
    --notes "Parallel GitHub wheel channel for urisys ${VER} (PyPI + GitHub)."

gh release upload "$TAG" -R "${OWNER}/${REPO}" "${assets[@]}" --clobber
echo "OK GitHub ${OWNER}/${REPO} ${TAG}"
