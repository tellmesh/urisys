#!/usr/bin/env bash
set -euo pipefail
curl -X POST http://127.0.0.1:8794/uri/call \
  -H 'Content-Type: application/json' \
  -d '{"uri":"kvm://local/task/command/click-text","payload":{"text":"OK"},"context":{"approved":true}}'
