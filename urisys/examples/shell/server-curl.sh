#!/usr/bin/env bash
set -euo pipefail

curl -X POST http://127.0.0.1:8789/uri/call       -H 'Content-Type: application/json'       -d '{
    "uri": "llm://mock/chat/complete",
    "payload": {"prompt":"Status systemu"},
    "context": {"approved": true, "environment": "mock"}
  }'
