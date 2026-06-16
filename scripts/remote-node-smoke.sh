# DEV/CI ONLY — on slave use URI probe; see docs/NODE-SETUP.md
#!/usr/bin/env bash
# Smoke test urisys-node over HTTP (local Docker or remote host e.g. lenovo).
#
# Usage:
#   bash scripts/remote-node-smoke.sh
#   URISYS_NODE_BASE=http://192.168.1.2:8790 bash scripts/remote-node-smoke.sh
#   URISYS_NODE_BASE=http://192.168.1.2:8790 URISYS_NODE_EXPECT_KVM=1 bash scripts/remote-node-smoke.sh
set -euo pipefail

BASE="${URISYS_NODE_BASE:-http://127.0.0.1:8790}"
EXPECT_KVM="${URISYS_NODE_EXPECT_KVM:-0}"
EXPECT_REAL="${URISYS_NODE_EXPECT_REAL:-0}"
TIMEOUT="${URISYS_NODE_TIMEOUT:-30}"

pass=0
fail=0
warn=0

log() { echo "[remote-node-smoke] $*"; }
ok() { log "PASS: $*"; pass=$((pass + 1)); }
bad() { log "FAIL: $*"; fail=$((fail + 1)); }
note() { log "WARN: $*"; warn=$((warn + 1)); }

http_get() {
  curl -fsS -m "${TIMEOUT}" "$1"
}

http_post() {
  curl -sS -m "${TIMEOUT}" -X POST "$1" -H 'Content-Type: application/json' -d "$2"
}

log "target=${BASE}"

# health
if HEALTH="$(http_get "${BASE}/health" 2>&1)"; then
  echo "${HEALTH}" | grep -q '"service": "urisys-node"' && ok "GET /health" || bad "GET /health unexpected body"
  NODE_ID="$(python3 -c "import json,sys; print(json.load(sys.stdin).get('node_id',''))" <<<"${HEALTH}")"
  log "node_id=${NODE_ID}"
else
  bad "GET /health unreachable: ${HEALTH}"
  echo "SUMMARY pass=${pass} fail=${fail} warn=${warn}"
  exit 1
fi

# routes
if ROUTES="$(http_get "${BASE}/uri/routes" 2>&1)"; then
  echo "${ROUTES}" | grep -q 'node://' && ok "routes include node://" || bad "node routes missing"
  echo "${ROUTES}" | grep -q 'screen://' && ok "routes include screen://" || bad "screen routes missing"
  if echo "${ROUTES}" | grep -q 'kvm://'; then
    ok "routes include kvm://"
  elif [ "${EXPECT_KVM}" = "1" ]; then
    bad "kvm routes missing (expected URISYS_NODE_PACKS with kvm + installed urikvm)"
  else
    note "kvm routes absent (install packs or hot-load POST /uri/pack)"
  fi
else
  bad "GET /uri/routes: ${ROUTES}"
fi

# identity call
if ID="$(http_post "${BASE}/uri/call" '{"uri":"node://local/query/identity","payload":{},"context":{"approved":true}}' 2>&1)"; then
  echo "${ID}" | grep -q '"ok": true' && ok "POST /uri/call identity" || bad "identity call: ${ID}"
else
  bad "POST /uri/call identity: ${ID}"
fi

# screen capture (needs [real] / mss on node)
if CAP="$(http_post "${BASE}/uri/call" '{"uri":"screen://local/monitor/primary/command/capture","payload":{"monitor":1},"context":{"approved":true,"allow_real":true}}' 2>&1)"; then
  if echo "${CAP}" | grep -q '"ok": true'; then
    ok "screen capture"
  elif echo "${CAP}" | grep -q 'mss backend requires'; then
    if [ "${EXPECT_REAL}" = "1" ]; then
      bad "screen capture needs pip install mss pillow ([real])"
    else
      note "screen capture skipped — install urisys-node[real] on node"
    fi
  else
    bad "screen capture: ${CAP}"
  fi
else
  bad "screen capture request failed: ${CAP}"
fi

# pack hot-load probe
if PACK="$(curl -sS -m 10 -X POST "${BASE}/uri/pack" -H 'Content-Type: application/json' -d '{"pack":"kvm"}' 2>&1)"; then
  if echo "${PACK}" | grep -q 'pack loading disabled'; then
    note "POST /uri/pack disabled — set URISYS_NODE_ALLOW_PACK_LOAD=1 on node"
  elif echo "${PACK}" | grep -q '"ok": true'; then
    ok "hot-load kvm pack"
  elif echo "${PACK}" | grep -q 'not installed'; then
    note "hot-load kvm failed — pip install urikvm urisysedge on node"
  else
    note "hot-load kvm: ${PACK}"
  fi
fi

log "SUMMARY pass=${pass} fail=${fail} warn=${warn} base=${BASE}"
[ "${fail}" -eq 0 ]
