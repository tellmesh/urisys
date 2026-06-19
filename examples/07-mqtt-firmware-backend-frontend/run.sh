#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-}"
MQTT_HOST="${MQTT_HOST:-127.0.0.1}"
HTTP_HOST="${HTTP_HOST:-127.0.0.1}"

free_port() {
  python3 - <<'PY'
import socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("127.0.0.1", 0))
    print(s.getsockname()[1])
PY
}

if [ "$MODE" = "--smoke" ]; then
  MQTT_PORT="${MQTT_PORT:-$(free_port)}"
  HTTP_PORT="${HTTP_PORT:-$(free_port)}"
else
  MQTT_PORT="${MQTT_PORT:-18883}"
  HTTP_PORT="${HTTP_PORT:-8097}"
fi

LOG_DIR="${TMPDIR:-/tmp}/urisys-mqtt-example-${MQTT_PORT}-${HTTP_PORT}"
mkdir -p "$LOG_DIR"

pids=()
cleanup() {
  for pid in "${pids[@]:-}"; do
    kill "$pid" >/dev/null 2>&1 || true
  done
  for pid in "${pids[@]:-}"; do
    wait "$pid" >/dev/null 2>&1 || true
  done
}
trap cleanup EXIT INT TERM

wait_tcp() {
  local host="$1" port="$2" name="$3"
  python3 - "$host" "$port" "$name" <<'PY'
import socket
import sys
import time

host, port, name = sys.argv[1], int(sys.argv[2]), sys.argv[3]
deadline = time.time() + 8
while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=0.2):
            sys.exit(0)
    except OSError:
        time.sleep(0.1)
print(f"{name} did not start on {host}:{port}", file=sys.stderr)
sys.exit(1)
PY
}

wait_http() {
  local url="$1"
  python3 - "$url" <<'PY'
import json
import sys
import time
import urllib.request

url = sys.argv[1]
deadline = time.time() + 8
while time.time() < deadline:
    try:
        with urllib.request.urlopen(url, timeout=0.3) as res:
            body = json.loads(res.read().decode("utf-8"))
            if body.get("ok"):
                sys.exit(0)
    except Exception:
        time.sleep(0.1)
print(f"HTTP backend did not start: {url}", file=sys.stderr)
sys.exit(1)
PY
}

python3 "$DIR/mqtt_codec.py" broker --host "$MQTT_HOST" --port "$MQTT_PORT" >"$LOG_DIR/broker.log" 2>&1 &
broker_pid="$!"
pids+=("$broker_pid")
wait_tcp "$MQTT_HOST" "$MQTT_PORT" "MQTT broker"

python3 "$DIR/firmware.py" --mqtt-host "$MQTT_HOST" --mqtt-port "$MQTT_PORT" >"$LOG_DIR/firmware.log" 2>&1 &
firmware_pid="$!"
pids+=("$firmware_pid")

python3 "$DIR/backend.py" \
  --mqtt-host "$MQTT_HOST" \
  --mqtt-port "$MQTT_PORT" \
  --host "$HTTP_HOST" \
  --port "$HTTP_PORT" \
  --static "$DIR/frontend" >"$LOG_DIR/backend.log" 2>&1 &
backend_pid="$!"
pids+=("$backend_pid")
wait_http "http://${HTTP_HOST}:${HTTP_PORT}/health"

if [ "$MODE" = "--smoke" ]; then
  python3 - "$HTTP_HOST" "$HTTP_PORT" <<'PY'
import json
import sys
import time
import urllib.request

host, port = sys.argv[1], sys.argv[2]
base = f"http://{host}:{port}"

def request(method, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        base + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=3) as res:
        return json.loads(res.read().decode("utf-8"))

request("POST", "/api/device/led", {"on": True})
deadline = time.time() + 5
state = {}
while time.time() < deadline:
    state = request("GET", "/api/device/state")
    if state.get("state", {}).get("led") is True:
        break
    time.sleep(0.2)
else:
    raise SystemExit(f"LED state did not update: {state}")

request("POST", "/api/device/ping", {"source": "smoke"})
telemetry = request("GET", "/api/device/telemetry")
if "uptime_ms" not in telemetry.get("telemetry", {}):
    raise SystemExit(f"Telemetry missing uptime_ms: {telemetry}")

topics = request("GET", "/api/mqtt/topics")
if not topics.get("topics", {}).get("command_led"):
    raise SystemExit(f"Topics endpoint broken: {topics}")

with urllib.request.urlopen(base + "/", timeout=3) as res:
    html = res.read().decode("utf-8")
    if "MQTT device bridge" not in html:
        raise SystemExit("Frontend HTML did not render expected title")

print(json.dumps({"ok": True, "state": state["state"], "telemetry": telemetry["telemetry"]}, indent=2, sort_keys=True))
PY
  exit 0
fi

echo "MQTT broker: ${MQTT_HOST}:${MQTT_PORT}"
echo "Frontend:    http://${HTTP_HOST}:${HTTP_PORT}/"
echo "Logs:        $LOG_DIR"
echo "Press Ctrl-C to stop."
wait "$backend_pid"
