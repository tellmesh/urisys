#!/usr/bin/env bash
set -euo pipefail

WORKER_PORT="${WORKER_PORT:-8796}"
BASE="http://127.0.0.1:${WORKER_PORT}"

echo "== health =="
curl -fsS "${BASE}/health"
echo

echo "== routes =="
curl -fsS "${BASE}/uri/routes" | python3 -m json.tool | head -30
echo

echo "== call stepper status =="
curl -fsS -X POST "${BASE}/uri/call" \
  -H 'Content-Type: application/json' \
  -d '{
    "uri": "stepper://machine-01/axis/x/query/status",
    "payload": {},
    "context": {"dry_run": true}
  }' | python3 -m json.tool
echo

echo "== call stepper move-relative (dry-run) =="
curl -fsS -X POST "${BASE}/uri/call" \
  -H 'Content-Type: application/json' \
  -d '{
    "uri": "stepper://machine-01/axis/x/command/move-relative",
    "payload": {"steps": 200, "direction": "cw", "speed_sps": 250},
    "context": {"approved": true, "dry_run": true}
  }' | python3 -m json.tool
echo

echo "PASS smoke"
