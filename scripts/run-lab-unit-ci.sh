#!/usr/bin/env bash
# CI-friendly lab unit tests (no Docker, no sibling uri3 required).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TELLMESH="$(cd "$ROOT/.." && pwd)"
cd "$ROOT"

export PYTHONPATH="${ROOT}/packages/python:${TELLMESH}/urirdp-docker/packages/python:${TELLMESH}/urisys-automation-lab/packages/python:${TELLMESH}/urisys-automation-lab/server"

pip install -q pytest pyyaml 2>/dev/null || true

python3 -m pytest \
  tests/test_kvm_pack_pyprojects.py \
  "${TELLMESH}/urisys-automation-lab/tests/test_flow_08_plan.py" \
  "${TELLMESH}/urisys-automation-lab/tests/test_flow_09_plan.py" \
  "${TELLMESH}/urisys-automation-lab/tests/test_lab_handlers.py" \
  "${TELLMESH}/urisys-automation-lab/tests/test_flow_expectations.py" \
  -q

echo "PASS lab-unit-ci"
