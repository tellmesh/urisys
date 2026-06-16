#!/usr/bin/env bash
# Run lab-10-flows E2E from repo root (must be tellmesh/urisys, not a nested urisys/).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -f "scripts/run_test_sessions.py" ] || [ ! -d "urisys-automation-lab" ]; then
  echo "error: run from tellmesh/urisys checkout (missing scripts/run_test_sessions.py)" >&2
  exit 1
fi

export PIP_DISABLE_PIP_VERSION_CHECK=1
exec python3 scripts/run_test_sessions.py --sessions lab-10-flows "$@"
