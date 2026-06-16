#!/usr/bin/env bash
# Wrapper: urisys-node Docker GUI host-control E2E with session report.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
exec python3 scripts/run_test_sessions.py --sessions urisys-node-docker-gui "$@"
