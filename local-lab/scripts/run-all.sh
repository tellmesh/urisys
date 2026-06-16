#!/usr/bin/env bash
# Full local Markpact materialization lab (3 levels).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/.."
COMPOSE="docker compose --profile lab -f local-lab/docker-compose.yml"

log() { echo "[local-lab] $*"; }

log "1/5 start nexus + oci-registry"
$COMPOSE up -d nexus oci-registry

log "2/5 init nexus repos"
$COMPOSE run --rm builder bash local-lab/scripts/00-init-nexus.sh

log "3/5 validate markpact"
$COMPOSE run --rm builder bash local-lab/scripts/01-validate-markpact.sh

log "4/5 build + push + artifact-index"
$COMPOSE run --rm builder bash local-lab/scripts/02-build-publish.sh

log "5/5 resolve + run worker"
$COMPOSE run --rm urisys-node-lab bash local-lab/scripts/03-resolve-run.sh

log "smoke from host (WORKER_PORT=${WORKER_PORT:-8796})"
WORKER_PORT="${WORKER_PORT:-8796}" bash local-lab/scripts/04-smoke.sh

log "ALL PASSED — artifacts in local-lab/generated/"
