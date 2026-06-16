#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${URISYS_RDP_PORT:-8795}"
export URISYS_ALLOW_REAL=1
export RDP_USER="${RDP_USER:-urisys}"
export RDP_PASSWORD="${RDP_PASSWORD:-urisys}"

log() { echo "[test-real-docker] $*"; }

cleanup() {
  docker compose logs --tail=80 urirdp 2>/dev/null || true
  docker compose down -v 2>/dev/null || true
}
trap cleanup EXIT

log "starting urirdp with URISYS_ALLOW_REAL=1"
docker compose up -d --build urirdp

for i in $(seq 1 60); do
  if curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
curl -fsS "http://127.0.0.1:${PORT}/health" | python3 -m json.tool

log "bootstrapping RDP X session inside container"
docker exec urirdp-gui bash /opt/urirdp/docker/bootstrap-rdp-session.sh

DISPLAY="$(docker exec urirdp-gui bash -lc 'grep ^DISPLAY= /tmp/urirdp-display.env | cut -d= -f2')"
XAUTHORITY="$(docker exec urirdp-gui bash -lc 'grep ^XAUTHORITY= /tmp/urirdp-display.env | cut -d= -f2')"
log "detected display ${DISPLAY} xauthority ${XAUTHORITY}"

ctx="{\"approved\":true,\"allow_real\":true,\"display\":\"${DISPLAY}\",\"xauthority\":\"${XAUTHORITY}\"}"

log "real screenshot"
curl -fsS -X POST "http://127.0.0.1:${PORT}/uri/call" \
  -H 'Content-Type: application/json' \
  -d "{\"uri\":\"kvm://local/monitor/primary/query/screenshot\",\"payload\":{},\"context\":${ctx}}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['ok'], d; r=d['result']; print('screenshot', r.get('driver'), r.get('size_bytes')); assert r.get('captured')"

log "real ocr"
curl -fsS -X POST "http://127.0.0.1:${PORT}/uri/call" \
  -H 'Content-Type: application/json' \
  -d "{\"uri\":\"ocr://local/image/latest/query/text\",\"payload\":{},\"context\":${ctx}}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['ok'], d; r=d['result']; tokens=r.get('tokens') or []; has_ok='OK' in (r.get('text') or '').upper() or any('OK' in (t.get('text') or '').upper() for t in tokens); print('ocr', r.get('engine'), 'tokens', len(tokens), 'has_ok', has_ok); assert has_ok"

log "real click-text"
curl -fsS -X POST "http://127.0.0.1:${PORT}/uri/call" \
  -H 'Content-Type: application/json' \
  -d "{\"uri\":\"kvm://local/task/command/click-text\",\"payload\":{\"text\":\"OK\"},\"context\":${ctx}}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['ok'], d; r=d['result']; print('clicked', r.get('clicked'), 'at', r.get('llm',{}).get('x'), r.get('llm',{}).get('y'), 'driver', (r.get('click') or {}).get('driver'), 'reason', (r.get('llm') or {}).get('reason')); assert r.get('clicked') is True; assert (r.get('click') or {}).get('driver') == 'xdotool'"

log "real flow"
docker exec -e URISYS_ALLOW_REAL=1 urirdp-gui \
  urisys-rdp --config /opt/urirdp/config/rdp-kvm-profile.json \
  flow /opt/urirdp/flows/real-rdp-click-text.uri.flow.yaml \
  --approve --allow-real --display "${DISPLAY}" \
  | python3 -c "import sys,json; steps=json.load(sys.stdin); assert all(s.get('ok') for s in steps), steps; print('flow steps', len(steps), 'all ok')"

log "ALL REAL DOCKER TESTS PASSED"
