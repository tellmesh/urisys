#!/usr/bin/env bash
# Bootstrap an active xrdp X session and show a visible "OK" target for OCR/KVM tests.
set -euo pipefail

USER_NAME="${RDP_USER:-urisys}"
USER_PASS="${RDP_PASSWORD:-urisys}"
PORT="${RDP_PORT:-3389}"
TIMEOUT="${BOOTSTRAP_TIMEOUT:-120}"
CLIENT_DISPLAY="${CLIENT_DISPLAY:-:99}"

log() { echo "[bootstrap-rdp] $*"; }

wait_xrdp() {
  for _ in $(seq 1 "$TIMEOUT"); do
    pgrep -x xrdp >/dev/null && pgrep -x xrdp-sesman >/dev/null && return 0
    sleep 1
  done
  log "xrdp did not start in time"
  return 1
}

start_client_display() {
  if sudo -u "$USER_NAME" env DISPLAY="$CLIENT_DISPLAY" xdpyinfo >/dev/null 2>&1; then
    log "client display ${CLIENT_DISPLAY} already up"
    return 0
  fi
  log "starting Xvfb on ${CLIENT_DISPLAY} for xfreerdp client"
  Xvfb "$CLIENT_DISPLAY" -screen 0 1024x768x24 -ac >/tmp/xvfb-client.log 2>&1 &
  echo $! >/tmp/xvfb-client.pid
  for _ in $(seq 1 30); do
    if sudo -u "$USER_NAME" env DISPLAY="$CLIENT_DISPLAY" xdpyinfo >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  log "Xvfb failed"; tail -20 /tmp/xvfb-client.log 2>/dev/null || true
  return 1
}

detect_session_display() {
  local sock
  for sock in /tmp/.X11-unix/X*; do
    [ -e "$sock" ] || continue
    local display=":${sock##*/X}"
    [ "$display" = "$CLIENT_DISPLAY" ] && continue
    if sudo -u "$USER_NAME" env DISPLAY="$display" xdpyinfo >/dev/null 2>&1; then
      echo "$display"
      return 0
    fi
  done
  echo ""
}

start_rdp_client() {
  if pgrep -f "xfreerdp.*127.0.0.1" >/dev/null 2>&1; then
    log "xfreerdp already running"
    return 0
  fi
  log "connecting xfreerdp to 127.0.0.1:${PORT} as ${USER_NAME}"
  sudo -u "$USER_NAME" env DISPLAY="$CLIENT_DISPLAY" \
    nohup xfreerdp \
      /v:"127.0.0.1:${PORT}" \
      /u:"${USER_NAME}" \
      /p:"${USER_PASS}" \
      /size:1024x768 \
      /cert:ignore \
      +clipboard \
      /t:urisys-bootstrap \
      >/tmp/xfreerdp.log 2>&1 &
  echo $! >/tmp/xfreerdp.pid
}

wait_session_display() {
  local display=""
  for _ in $(seq 1 "$TIMEOUT"); do
    display="$(detect_session_display)"
    if [ -n "$display" ]; then
      echo "$display"
      return 0
    fi
    sleep 1
  done
  log "no RDP X session found; xfreerdp log:"
  tail -30 /tmp/xfreerdp.log 2>/dev/null || true
  return 1
}

show_ok_target() {
  local display="$1"
  log "showing OK target on DISPLAY=${display}"
  sudo -u "$USER_NAME" env DISPLAY="$display" \
    zenity --info --title="Automation Target" --text="OK" --no-wrap --width=320 --height=120 \
    >/tmp/ok-window.log 2>&1 &
  sleep 2
  sudo -u "$USER_NAME" env DISPLAY="$display" xdotool search --name "Automation Target" windowactivate 2>/dev/null || true
  sleep 1
}

main() {
  wait_xrdp
  start_client_display
  start_rdp_client
  DISPLAY="$(wait_session_display)"
  export URISYS_KVM_DISPLAY="$DISPLAY"
  echo "DISPLAY=${DISPLAY}" >/tmp/urirdp-display.env
  echo "XAUTHORITY=/home/${USER_NAME}/.Xauthority" >> /tmp/urirdp-display.env
  show_ok_target "$DISPLAY"
  log "ready display=${DISPLAY}"
}

main "$@"
