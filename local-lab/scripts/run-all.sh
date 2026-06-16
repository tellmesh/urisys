#!/usr/bin/env bash
# Full local Markpact materialization lab (GitHub model: ghcr/raw, no Nexus).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/.."
COMPOSE="docker compose --profile lab -f local-lab/docker-compose.yml"

log() { echo "[local-lab] $*"; }

log "1/4 start oci-registry + artifacts-server"
$COMPOSE up -d oci-registry artifacts-server

log "2/4 validate markpact"
$COMPOSE run --rm builder bash local-lab/scripts/01-validate-markpact.sh

log "3/4 build + push + artifact-index + releases/"
$COMPOSE run --rm builder bash local-lab/scripts/02-build-publish.sh

log "4/4 resolve from URL + run worker"
$COMPOSE run --rm urisys-node-lab bash local-lab/scripts/05-resolve-from-url.sh

log "smoke from host (WORKER_PORT=${WORKER_PORT:-8796})"
WORKER_PORT="${WORKER_PORT:-8796}" bash local-lab/scripts/04-smoke.sh

log "ALL PASSED — artifacts in local-lab/generated/ (releases under local-lab/generated/releases/)"
