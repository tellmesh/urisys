#!/usr/bin/env bash
# Resolve sibling repo paths in tellmesh workspace (urisys checkout may be standalone).
set -euo pipefail

_urisys_root() {
  cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd
}

urisys_root() {
  _urisys_root
}

# tellmesh workspace root (urisys + uricore siblings), or TELLMESH_ROOT env.
tellmesh_root() {
  local root
  root="$(_urisys_root)"
  if [ -n "${TELLMESH_ROOT:-}" ] && [ -d "$TELLMESH_ROOT" ]; then
    echo "$TELLMESH_ROOT"
    return 0
  fi
  if [ -d "$root/../uricontrol" ]; then
    cd "$root/.." && pwd
    return 0
  fi
  return 1
}

# tellmesh/markpact-contracts/packs when urisys lives in tellmesh/urisys
markpact_contracts_packs() {
  local root
  root="$(_urisys_root)"
  if [ -d "$root/../markpact-contracts/packs" ]; then
    echo "$root/../markpact-contracts/packs"
    return 0
  fi
  if [ -d "$root/markpacts/packs" ]; then
    echo "$root/markpacts/packs"
    return 0
  fi
  return 1
}

# tellmesh/uricontrol when present; empty if missing (use pip install uricontrol)
uricontrol_root() {
  local root
  root="$(_urisys_root)"
  if [ -d "$root/../uricontrol/core/python" ]; then
    echo "$root/../uricontrol"
    return 0
  fi
  return 1
}

uricontrol_pythonpath() {
  local root
  root="$(uricontrol_root)" || return 1
  echo "$root/core/python"
}

# Local release artifacts (CI may override RELEASES_DIR=releases for git commit).
releases_dir() {
  local root
  root="$(_urisys_root)"
  if [ -n "${RELEASES_DIR:-}" ]; then
    echo "$RELEASES_DIR"
    return 0
  fi
  echo "$root/local-lab/generated/releases"
}
