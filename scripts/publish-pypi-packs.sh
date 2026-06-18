#!/usr/bin/env bash
# Build and upload kvm capability packs to PyPI (from tellmesh sibling repos).
#
# Usage:
#   bash scripts/publish-pypi-packs.sh
#   PYPI_TOKEN=... bash scripts/publish-pypi-packs.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TELLMESH="$(dirname "$ROOT")"
REPO="${PYPI_REPOSITORY:-pypi}"
DRY_RUN="${DRY_RUN:-0}"

PACK_DIRS=(
  "${TELLMESH}/uricore"
  "${TELLMESH}/urikvm"
  "${TELLMESH}/urihim"
  "${TELLMESH}/uriocr"
  "${TELLMESH}/urillm"
)

echo "== build kvm PyPI packs (tellmesh siblings) =="
for dir in "${PACK_DIRS[@]}"; do
  name="$(python3 -c "import tomllib; print(tomllib.load(open('$dir/pyproject.toml','rb'))['project']['name'])")"
  echo "-- $name ($dir)"
  rm -rf "$dir/dist" "$dir/build" "$dir"/*.egg-info 2>/dev/null || true
  (cd "$dir" && python3 -m build)
done

if [[ -z "${PYPI_TOKEN:-}" ]]; then
  echo ""
  echo "PYPI_TOKEN not set — wheels built under each pack's dist/ (upload skipped)."
  exit 0
fi

export TWINE_USERNAME="${TWINE_USERNAME:-__token__}"
export TWINE_PASSWORD="$PYPI_TOKEN"

echo ""
echo "== upload to $REPO =="
for dir in "${PACK_DIRS[@]}"; do
  name="$(python3 -c "import tomllib; print(tomllib.load(open('$dir/pyproject.toml','rb'))['project']['name'])")"
  echo "-- $name"
  if [[ "$DRY_RUN" == "1" ]]; then
    twine check "$dir/dist"/*
  else
    twine upload --repository "$REPO" "$dir/dist"/*
    sleep 2
  fi
done

echo ""
echo "OK: published ${#PACK_DIRS[@]} packs to $REPO"
