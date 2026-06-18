#!/usr/bin/env bash
# Local Markpact CI: drift guard + validate + unit tests.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck source=paths.sh
source "$ROOT/scripts/paths.sh"

export TELLMESH_ROOT="${TELLMESH_ROOT:-$(tellmesh_root 2>/dev/null || cd "$ROOT/.." && pwd)}"

echo "== generate_pack_markpacts --check =="
python3 scripts/generate_pack_markpacts.py --check

echo "== check_contract_drift =="
python3 scripts/check_contract_drift.py

echo "== validate-all-markpacts =="
bash scripts/validate-all-markpacts.sh

echo "== markpact pytest =="
python -m pytest \
  tests/test_markpact.py \
  tests/test_markpact_run.py \
  tests/test_markpact_run_flow.py \
  tests/test_markpact_materialize.py \
  tests/test_markpact_pack_deps.py \
  tests/test_markpact_contract_materialize.py \
  tests/test_markpact_session_isolation.py \
  tests/test_pack_gen.py \
  tests/test_contract_gen.py \
  tests/test_pack_manager_sibling.py \
  tests/test_urisys_flow_handler.py \
  tests/test_machine_cycle_process.py \
  tests/test_desktop_automation_processes.py \
  tests/test_platform_export.py \
  tests/test_showcase.py \
  -q

if [ "${MARKPACT_SMOKE:-}" = "1" ]; then
  echo "== showcase run-flow smoke =="
  bash examples/markpact/showcase-run-flow.sh
fi

echo "PASS markpact-ci"
