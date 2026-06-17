#!/usr/bin/env bash
# Test urisys install + doctor across available Python versions (3.10–3.14).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
URICORE="${URICORE_ROOT:-$(dirname "$ROOT")/uricore}"
TMP="${TMPDIR:-/tmp}/urisys-python-matrix-$$"
mkdir -p "$TMP"
trap 'rm -rf "$TMP"' EXIT

log() { echo "[python-matrix] $*"; }
failures=0

run_one() {
  local py="$1"
  if ! command -v "$py" >/dev/null 2>&1; then
    log "skip $py (not installed)"
    return 0
  fi
  if ! "$py" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' >/dev/null 2>&1; then
    log "skip $py (interpreter not runnable)"
    return 0
  fi
  local ver
  ver="$("$py" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  log "== $py ($ver) =="
  local venv="$TMP/venv-$ver"
  "$py" -m venv "$venv"
  # shellcheck disable=SC1091
  source "$venv/bin/activate"
  python -m pip install -U pip wheel >/dev/null
  if [ -d "$URICORE" ]; then
    pip install -q -e "$URICORE"
  else
    pip install -q "uricore>=0.1.2"
  fi
  pip install -q -e "$ROOT/packages/python/urisysedge" 2>/dev/null || pip install -q "urisysedge>=0.1.0"
  pip install -q -e "$ROOT[real]"
  python -m urisys.bootstrap doctor --min-version 0.1.0 >/dev/null
  python -c "import uri_control; import urisys; print('imports ok', uri_control.__name__)"
  deactivate || true
  log "PASS $py"
  return 0
}

for py in python3.10 python3.11 python3.12 python3.13 python3.14 python3; do
  if ! run_one "$py"; then
    failures=$((failures + 1))
    log "FAIL $py"
  fi
done

if [ "$failures" -gt 0 ]; then
  log "$failures python version(s) failed"
  exit 1
fi
log "all available versions passed"
exit 0
