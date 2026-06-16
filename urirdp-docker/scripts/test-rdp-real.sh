#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[test-rdp-real] building and running RDP e2e (urirdp + rdp-client)..."
docker compose -f docker-compose.rdp-e2e.yml down -v 2>/dev/null || true
docker compose -f docker-compose.rdp-e2e.yml up \
  --build \
  --abort-on-container-exit \
  --exit-code-from rdp-client

echo "[test-rdp-real] passed"
