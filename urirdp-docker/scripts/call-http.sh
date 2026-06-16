#!/usr/bin/env bash
set -euo pipefail
PORT="${URISYS_RDP_PORT:-8795}"
curl -sS -X POST "http://127.0.0.1:${PORT}/uri/call" \
  -H 'Content-Type: application/json' \
  -d '{
    "uri": "kvm://local/task/command/click-text",
    "payload": {"text":"OK"},
    "context": {"approved":true,"dry_run":true}
  }' | python3 -m json.tool
