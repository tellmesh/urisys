#!/usr/bin/env bash
# Real RDP/KVM integration test — runs inside the rdp-client container.
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y --no-install-recommends \
  freerdp2-x11 \
  xvfb \
  curl \
  jq \
  procps \
  ca-certificates

Xvfb :99 -screen 0 1280x720x24 -ac >/tmp/xvfb.log 2>&1 &
XVFB_PID=$!

cleanup() {
  kill "$XVFB_PID" 2>/dev/null || true
  pkill -f xfreerdp 2>/dev/null || true
}
trap cleanup EXIT

sleep 2

echo "[e2e-rdp-real] connecting xfreerdp to urirdp:3389"
xfreerdp \
  /v:urirdp:3389 \
  /u:"${RDP_USER:-urisys}" \
  /p:"${RDP_PASSWORD:-urisys}" \
  /cert:ignore \
  /size:1280x720 \
  +clipboard \
  /t:urisys-e2e \
  >/tmp/xfreerdp.log 2>&1 &

RDP_PID=$!

echo "[e2e-rdp-real] waiting for RDP display..."
for i in $(seq 1 60); do
  if curl -fsS http://urirdp:8795/uri/call \
    -H 'Content-Type: application/json' \
    -d '{"uri":"rdp://local/display/query/status","payload":{},"context":{"approved":true,"allow_real":true}}' \
    | tee /tmp/rdp-status.json \
    | jq -e '.ok == true and (.result.display_exists == true) and (.result.xdpyinfo_ok == true)' >/dev/null; then
    echo "[e2e-rdp-real] RDP display is ready"
    break
  fi

  if ! kill -0 "$RDP_PID" 2>/dev/null; then
    echo "[e2e-rdp-real] xfreerdp exited unexpectedly"
    cat /tmp/xfreerdp.log || true
    exit 1
  fi

  if [ "$i" = "60" ]; then
    echo "[e2e-rdp-real] RDP display not ready in time"
    cat /tmp/rdp-status.json || true
    cat /tmp/xfreerdp.log || true
    exit 1
  fi

  sleep 2
done

echo "[e2e-rdp-real] preparing OK target on RDP desktop..."
curl -fsS http://urirdp:8795/uri/call \
  -H 'Content-Type: application/json' \
  -d '{"uri":"rdp://local/session/command/prepare-target","payload":{"text":"OK"},"context":{"approved":true,"allow_real":true}}' \
  | jq -e '.ok == true and .result.prepared == true' >/dev/null

sleep 2

echo "[e2e-rdp-real] running real kvm click-text..."
RESULT="$(curl -fsS http://urirdp:8795/uri/call \
  -H 'Content-Type: application/json' \
  -d '{
    "uri": "kvm://local/task/command/click-text",
    "payload": {"text": "OK"},
    "context": {
      "approved": true,
      "allow_real": true
    }
  }')"

echo "$RESULT" | jq .

echo "$RESULT" | jq -e '
  .ok == true and
  .result.clicked == true and
  .result.pipeline.screenshot.ok == true and
  .result.pipeline.ocr.ok == true and
  .result.pipeline.llm.ok == true and
  .result.pipeline.him.ok == true and
  .result.pipeline.him.result.driver == "xdotool" and
  (.result.pipeline.llm.result.model | test("mock-vision") | not)
'

echo "[e2e-rdp-real] ALL PASSED"
