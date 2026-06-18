#!/usr/bin/env bash
# Nightly / manual Docker E2E: lab-10-flows + urisys-node GUI slave.
# Requires tellmesh monorepo checkout (urisys + uricontrol + uri3 + uri2flow siblings).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -d "../uricontrol" ] && [ ! -d "../uricore" ] && [ ! -d "uricore" ]; then
  echo "error: uricontrol sibling required (tellmesh monorepo layout)" >&2
  exit 1
fi

export PIP_DISABLE_PIP_VERSION_CHECK=1
SESSIONS="${URISYS_NIGHTLY_SESSIONS:-lab-10-flows,urisys-node-docker-gui}"
exec python3 scripts/run_test_sessions.py --sessions "${SESSIONS}" "$@"
