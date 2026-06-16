#!/usr/bin/env bash
# Initialize Nexus: set admin password + create raw hosted repos (idempotent).
set -euo pipefail

NEXUS_URL="${NEXUS_URL:-http://nexus:8081}"
NEXUS_USER="${NEXUS_USER:-admin}"
NEXUS_PASSWORD="${NEXUS_PASSWORD:-admin123}"
NEXUS_RAW_CONTRACTS="${NEXUS_RAW_CONTRACTS:-markpact-contracts-release}"
NEXUS_RAW_ARTIFACTS="${NEXUS_RAW_ARTIFACTS:-markpact-artifacts-release}"

log() { echo "[init-nexus] $*"; }

wait_nexus() {
  for i in $(seq 1 60); do
    if curl -fsS "${NEXUS_URL}/service/rest/v1/status" >/dev/null 2>&1; then
      return 0
    fi
    sleep 3
  done
  echo "Nexus not ready at ${NEXUS_URL}" >&2
  exit 1
}

auth_curl() {
  curl -fsS -u "${NEXUS_USER}:${NEXUS_PASSWORD}" "$@"
}

create_raw_repo() {
  local name="$1"
  if auth_curl "${NEXUS_URL}/service/rest/v1/repositories/${name}" >/dev/null 2>&1; then
    log "repo exists: ${name}"
    return 0
  fi
  log "creating raw repo: ${name}"
  auth_curl -X POST "${NEXUS_URL}/service/rest/v1/repositories/raw/hosted" \
    -H 'Content-Type: application/json' \
    -d "$(cat <<EOF
{
  "name": "${name}",
  "online": true,
  "storage": {
    "blobStoreName": "default",
    "strictContentTypeValidation": true,
    "writePolicy": "ALLOW_ONCE"
  }
}
EOF
)"
}

wait_nexus
log "Nexus is up"

# First boot may still use generated password — try login; on fail read from container.
if ! auth_curl "${NEXUS_URL}/service/rest/v1/status" >/dev/null 2>&1; then
  if docker exec markpact-nexus test -f /nexus-data/admin.password 2>/dev/null; then
    INIT_PASS="$(docker exec markpact-nexus cat /nexus-data/admin.password)"
    log "using initial Nexus password from container"
    curl -fsS -u "admin:${INIT_PASS}" -X PUT "${NEXUS_URL}/service/rest/v1/security/users/admin/change-password" \
      -H 'Content-Type: text/plain' \
      --data "${NEXUS_PASSWORD}" || true
  fi
fi

auth_curl "${NEXUS_URL}/service/rest/v1/status" | jq .
create_raw_repo "${NEXUS_RAW_CONTRACTS}"
create_raw_repo "${NEXUS_RAW_ARTIFACTS}"
log "OK"
