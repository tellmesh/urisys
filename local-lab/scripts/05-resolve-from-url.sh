#!/usr/bin/env bash
# Resolve worker using artifact-index from HTTP URL (local nginx simulates GitHub raw).
set -euo pipefail
cd /workspace

ARTIFACT_INDEX_URL="${ARTIFACT_INDEX_URL:-http://127.0.0.1:8190/artifact-index.json}"
NODE_PROFILE="${NODE_PROFILE:-local-lab/node-profile.local.yaml}"
WORKER_PORT="${WORKER_PORT:-8796}"
WORKER_NAME="${WORKER_NAME:-urisys-stepper-worker}"

pip install -e urisys-node -q

echo "== artifact-index URL =="
echo "$ARTIFACT_INDEX_URL"
curl -fsS "$ARTIFACT_INDEX_URL" | python3 -m json.tool | head -20

python3 -m urisysnode.cli artifact resolve-run \
  --index "$ARTIFACT_INDEX_URL" \
  --profile "$NODE_PROFILE" \
  --port "$WORKER_PORT" \
  --container "$WORKER_NAME"

echo "PASS resolve-from-url"
