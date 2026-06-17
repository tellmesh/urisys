#!/usr/bin/env bash
# Build wheels for tellmesh URI packs and upload to GitHub Releases (tag vX.Y.Z).
#
# Usage:
#   bash scripts/publish-tellmesh-wheels.sh                    # all default packs
#   bash scripts/publish-tellmesh-wheels.sh urirdp urirdpedge  # subset
#   CREATE_REPOS=1 bash scripts/publish-tellmesh-wheels.sh     # gh repo create if missing
#
set -euo pipefail

URISYS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TELLMESH_ROOT="${TELLMESH_ROOT:-$(dirname "$URISYS_ROOT")}"
ORG="${URISYS_PACK_GITHUB_OWNER:-tellmesh}"

DEFAULT_PACKS=(
  urirdp urirdpedge urishell urichat uristt uriwebrtc urimessage
  urikvmedge urienv urikvm urihim uriocr urillm
)

PACKS=("${@:-${DEFAULT_PACKS[@]}}")

pip install -q build 2>/dev/null || python3 -m pip install -q build

publish_one() {
  local repo="$1"
  local dir="${TELLMESH_ROOT}/${repo}"
  if [ ! -f "${dir}/pyproject.toml" ]; then
    echo "skip ${repo}: no pyproject.toml at ${dir}" >&2
    return 0
  fi

  local version
  version="$(python3 -c "import tomllib; print(tomllib.load(open('${dir}/pyproject.toml','rb'))['project']['version'])")"
  local tag="v${version}"

  if ! gh repo view "${ORG}/${repo}" >/dev/null 2>&1; then
    if [ "${CREATE_REPOS:-0}" != "1" ]; then
      echo "skip ${repo}: GitHub repo ${ORG}/${repo} missing (set CREATE_REPOS=1 to create)" >&2
      return 0
    fi
    if [ ! -f "${dir}/.gitignore" ]; then
      cat > "${dir}/.gitignore" <<'EOF'
__pycache__/
*.py[cod]
*.egg-info/
.venv/
.pytest_cache/
dist/
build/
EOF
    fi
    echo "creating ${ORG}/${repo}..."
    if [ ! -d "${dir}/.git" ]; then
      git -C "${dir}" init -b main
      git -C "${dir}" add -A
      git -C "${dir}" commit -m "Initial ${repo} ${version}" || true
    fi
    gh repo create "${ORG}/${repo}" --public \
      --description "${repo} URI capability pack" \
      --source "${dir}" --remote origin --push
  fi

  echo "building ${repo} ${version}..."
  rm -rf "${dir}/dist"
  python3 -m build -w "${dir}"
  local wheel
  wheel="$(ls "${dir}/dist/"*.whl | head -1)"
  test -f "${wheel}" || { echo "missing wheel for ${repo}" >&2; return 1; }

  if ! gh release view "${tag}" --repo "${ORG}/${repo}" >/dev/null 2>&1; then
    gh release create "${tag}" --repo "${ORG}/${repo}" \
      --title "${repo} ${tag}" \
      --notes "Wheel release ${repo} ${version}"
  fi
  gh release upload "${tag}" "${wheel}" --repo "${ORG}/${repo}" --clobber
  echo "published ${wheel} -> ${ORG}/${repo} ${tag}"
}

for repo in "${PACKS[@]}"; do
  publish_one "${repo}"
done

echo "done."
