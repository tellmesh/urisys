#!/usr/bin/env bash
set -euo pipefail
cd /workspace

ARTIFACT_INDEX="${ARTIFACT_INDEX:-local-lab/generated/artifact-index.json}"
NODE_PROFILE="${NODE_PROFILE:-local-lab/node-profile.local.yaml}"
WORKER_PORT="${WORKER_PORT:-8791}"
WORKER_NAME="${WORKER_NAME:-urisys-stepper-worker}"

pip install -e urisys-node -q

python3 -m urisysnode.cli artifact resolve-run \
  --index "$ARTIFACT_INDEX" \
  --profile "$NODE_PROFILE" \
  --port "$WORKER_PORT" \
  --container "$WORKER_NAME"
