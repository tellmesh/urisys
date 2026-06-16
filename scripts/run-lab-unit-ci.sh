#!/usr/bin/env bash
# CI-friendly lab unit tests (no Docker, no sibling uri3 required).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export PYTHONPATH="${ROOT}/packages/python:${ROOT}/urirdp-docker/packages/python:${ROOT}/urisys-automation-lab/packages/python:${ROOT}/urisys-automation-lab/server"

pip install -q pytest pyyaml 2>/dev/null || true

python3 -m pytest \
  tests/test_kvm_pack_pyprojects.py \
  urisys-automation-lab/tests/test_flow_08_plan.py \
  urisys-automation-lab/tests/test_flow_09_plan.py \
  urisys-automation-lab/tests/test_lab_handlers.py \
  urisys-automation-lab/tests/test_flow_expectations.py \
  -q

echo "PASS lab-unit-ci"
