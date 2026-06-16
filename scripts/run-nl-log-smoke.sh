#!/usr/bin/env bash
# Smoke test: log:// → llm decide → conditional branches (host-side uri3).
set -euo pipefail

URISYS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
URI3_ROOT="$(cd "$URISYS_ROOT/../uri3" && pwd)"
TELLMESH_ROOT="${TELLMESH_ROOT:-$(cd "$URISYS_ROOT/../tellmesh" 2>/dev/null && pwd || echo "$URISYS_ROOT")}"
FLOW="$URI3_ROOT/examples/nl-log-decision.uri.flow.yaml"

if [[ ! -f "$FLOW" ]]; then
  echo "missing flow: $FLOW" >&2
  exit 1
fi

LOG_DIR="$TELLMESH_ROOT/output/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/hypervisor.log"
if [[ ! -s "$LOG_FILE" ]] || ! grep -q '502' "$LOG_FILE" 2>/dev/null; then
  echo '{"timestamp":"2026-06-16T10:01:00Z","level":"ERROR","logger":"urisys.forward","message":"HTTP 502 Bad Gateway to urirdp"}' >> "$LOG_FILE"
fi

export URISYS_REPO_ROOT="$TELLMESH_ROOT"

echo "== nl-log-decision smoke (repo_root=$URISYS_REPO_ROOT) =="
cd "$URISYS_ROOT"
uv sync --group lab >/dev/null
uv run python3 -c "
from pathlib import Path
from uri2flow import expand_flow
from uri3.graph import run_workflow

flow = Path('$FLOW')
expanded = expand_flow(flow)
result = run_workflow(expanded, approve=True, root=Path('$TELLMESH_ROOT'), browser_mode='mock')
statuses = {s.id: s.status for s in result.steps}
print('ok:', result.ok)
print('steps:', statuses)
assert result.ok, statuses
assert statuses.get('nl_decide') == 'completed'
assert statuses.get('retry_forward') == 'completed'
assert statuses.get('escalate') == 'skipped'
print('PASS nl-log-decision')
"
