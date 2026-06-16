#!/usr/bin/env bash
# Build and upload kvm capability packs to PyPI (urisysedge first, then urikvm/him/ocr/llm).
#
# Usage:
#   bash scripts/publish-pypi-packs.sh              # build only (no token)
#   PYPI_TOKEN=... bash scripts/publish-pypi-packs.sh
#   PYPI_REPOSITORY=testpypi PYPI_TOKEN=... bash scripts/publish-pypi-packs.sh
#
# Requires: python -m build, twine (uv sync --group dev or pip install build twine)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="${PYPI_REPOSITORY:-pypi}"
DRY_RUN="${DRY_RUN:-0}"

PACK_DIRS=(
  "packages/python/urisysedge"
  "urikvm-docker/packages/python/urikvm"
  "urikvm-docker/packages/python/urihim"
  "urikvm-docker/packages/python/uriocr"
  "urikvm-docker/packages/python/urillm"
)

echo "== build kvm PyPI packs =="
for rel in "${PACK_DIRS[@]}"; do
  dir="$ROOT/$rel"
  name="$(python3 -c "import tomllib; print(tomllib.load(open('$dir/pyproject.toml','rb'))['project']['name'])")"
  echo "-- $name ($rel)"
  rm -rf "$dir/dist" "$dir/build" "$dir"/*.egg-info 2>/dev/null || true
  (cd "$dir" && python3 -m build)
done

if [[ -z "${PYPI_TOKEN:-}" ]]; then
  echo ""
  echo "PYPI_TOKEN not set — wheels built under each pack's dist/ (upload skipped)."
  echo "TestPyPI: PYPI_REPOSITORY=testpypi PYPI_TOKEN=pypi-... $0"
  exit 0
fi

if ! command -v twine >/dev/null 2>&1; then
  echo "twine not found; install with: pip install twine" >&2
  exit 1
fi

export TWINE_USERNAME="${TWINE_USERNAME:-__token__}"
export TWINE_PASSWORD="$PYPI_TOKEN"

echo ""
echo "== upload to $REPO =="
for rel in "${PACK_DIRS[@]}"; do
  dir="$ROOT/$rel"
  name="$(python3 -c "import tomllib; print(tomllib.load(open('$dir/pyproject.toml','rb'))['project']['name'])")"
  echo "-- $name"
  if [[ "$DRY_RUN" == "1" ]]; then
    twine check "$dir/dist"/*
    echo "(dry-run: skipping upload)"
  else
    twine upload --repository "$REPO" "$dir/dist"/*
    sleep 2
  fi
done

echo ""
echo "OK: published ${#PACK_DIRS[@]} packs to $REPO"
