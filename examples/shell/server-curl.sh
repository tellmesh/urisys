#!/usr/bin/env bash
set -euo pipefail

curl -X POST http://127.0.0.1:8789/uri/call       -H 'Content-Type: application/json'       -d '{
    "uri": "llm://mock/chat/query/completion",
    "payload": {"messages":[{"role":"user","content":"Status systemu"}]},
    "context": {"approved": true, "environment": "mock"}
  }'
