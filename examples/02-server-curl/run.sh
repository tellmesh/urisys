#!/usr/bin/env bash
set -euo pipefail

ENDPOINT="${URISYS_ENDPOINT:-http://127.0.0.1:8789}"

curl -X POST "$ENDPOINT/uri/call" \
  -H 'Content-Type: application/json' \
  -d '{
    "uri": "llm://mock/chat/query/completion",
    "payload": {"messages":[{"role":"user","content":"Status systemu"}]},
    "context": {"approved": true, "environment": "mock"}
  }'
