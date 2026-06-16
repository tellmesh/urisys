#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose up -d --build urirdp
trap 'docker compose logs --tail=100 urirdp; docker compose down -v' EXIT
for i in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:${URISYS_RDP_PORT:-8795}/health >/dev/null; then
    break
  fi
  sleep 1
done
curl -fsS http://127.0.0.1:${URISYS_RDP_PORT:-8795}/uri/routes | python3 -m json.tool
curl -fsS -X POST http://127.0.0.1:${URISYS_RDP_PORT:-8795}/uri/call \
  -H 'Content-Type: application/json' \
  -d '{"uri":"kvm://local/task/command/click-text","payload":{"text":"OK"},"context":{"approved":true,"dry_run":true}}' \
  | python3 -m json.tool
echo "docker smoke passed"
