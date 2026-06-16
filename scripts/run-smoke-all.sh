#!/usr/bin/env bash
# Fast smoke suite: uri3 NL pipeline + lab unit tests (no Docker).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
URI3="$(cd "$ROOT/../uri3" && pwd)"

echo "== nl-log-decision =="
bash "$ROOT/scripts/run-nl-log-smoke.sh"

echo "== uri3 tests =="
cd "$URI3"
uv run pytest tests/test_nl_log_decision.py tests/test_llm_plan.py tests/test_workflow_conditions.py -q

echo "== lab unit tests =="
cd "$ROOT"
uv sync --group lab >/dev/null
uv run pytest urisys-automation-lab/tests/test_flow_08_plan.py \
  urisys-automation-lab/tests/test_flow_09_plan.py \
  urisys-automation-lab/tests/test_lab_handlers.py -q

echo "PASS smoke-all"
