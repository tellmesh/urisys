#!/usr/bin/env bash
# Build wheels and publish to PyPI + GitHub Releases (parallel channel when PyPI blocks).
#
# Usage:
#   bash scripts/publish-uri-releases.sh uricontrol urihim urimail
#   PACKS="uricontrol urihim" bash scripts/publish-uri-releases.sh
#   PYPI_ONLY=1 bash scripts/publish-uri-releases.sh uricontrol
#   GITHUB_ONLY=1 bash scripts/publish-uri-releases.sh uricontrol
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TELLMESH="$(dirname "$ROOT")"
SLEEP_SEC="${PUBLISH_SLEEP_SEC:-90}"
GITHUB_OWNER="${GITHUB_OWNER:-tellmesh}"

packs=("$@")
if [ "${#packs[@]}" -eq 0 ]; then
  if [ -n "${PACKS:-}" ]; then
    read -r -a packs <<< "${PACKS}"
  else
  packs=(uricontrol urihim urillm uriocr urioffice urimail urivql urisys-node)
  fi
fi

pypi_upload() {
  local dir="$1" name="$2" ver="$3"
  if [ "${GITHUB_ONLY:-0}" = "1" ]; then
    return 0
  fi
  if goal publish 2>&1; then
    echo "OK PyPI $name $ver"
    return 0
  fi
  echo "WARN PyPI upload failed for $name — use GitHub wheel (see urisys uricore_install.py)"
  return 1
}

github_repo_for() {
  local name="$1"
  case "$name" in
    uricontrol) echo "uricontrol" ;;
    nl2uricontrol) echo "nl2uricontrol" ;;
    *) echo "$name" ;;
  esac
}

github_release() {
  local dir="$1" name="$2" ver="$3"
  if [ "${PYPI_ONLY:-0}" = "1" ]; then
    return 0
  fi
  local repo
  repo="$(github_repo_for "$name")"
  local tag="v${ver}"
  if ! command -v gh >/dev/null 2>&1; then
    echo "SKIP GitHub release (gh CLI missing) for $name"
    return 0
  fi
  gh release view "$tag" -R "${GITHUB_OWNER}/${repo}" >/dev/null 2>&1 || \
    gh release create "$tag" -R "${GITHUB_OWNER}/${repo}" --title "$name $tag" --notes "Automated release $tag"
  gh release upload "$tag" -R "${GITHUB_OWNER}/${repo}" dist/"${name}-${ver}"* --clobber
  echo "OK GitHub ${GITHUB_OWNER}/${repo} $tag"
}

for pkg in "${packs[@]}"; do
  dir="${TELLMESH}/${pkg}"
  if [ ! -f "${dir}/pyproject.toml" ]; then
    echo "SKIP missing $dir"
    continue
  fi
  name="$(python3 -c "import tomllib; print(tomllib.load(open('${dir}/pyproject.toml','rb'))['project']['name'])")"
  ver="$(python3 -c "import tomllib; print(tomllib.load(open('${dir}/pyproject.toml','rb'))['project']['version'])")"
  echo "== $name $ver ($dir) =="
  rm -rf "${dir}/dist" "${dir}/build" "${dir}"/*.egg-info 2>/dev/null || true
  (cd "$dir" && python3 -m build)
  (cd "$dir" && pypi_upload "$dir" "$name" "$ver") || true
  (cd "$dir" && github_release "$dir" "$name" "$ver") || true
  echo "sleep ${SLEEP_SEC}s (PyPI rate limit)"
  sleep "$SLEEP_SEC"
done

echo "DONE packs=${#packs[@]}"
