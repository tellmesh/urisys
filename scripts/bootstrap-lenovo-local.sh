#!/usr/bin/env bash
# Run ON lenovo (console or SSH) — bootstrap slave venv without git credentials.
#
#   curl -fsSL https://raw.githubusercontent.com/tellmesh/urisys/main/scripts/bootstrap-lenovo-local.sh | bash
#   # or copy from dev:
#   scp scripts/bootstrap-lenovo-local.sh tom@192.168.188.201:~/
#   bash ~/bootstrap-lenovo-local.sh
set -euo pipefail

PYTHON="${URISYS_PYTHON:-python3.12}"
VENV="${URISYS_VENV:-$HOME/venv312}"
URISYS_MIN="${URISYS_MIN_VERSION:-0.1.25}"
NODE_VER="${URISYS_NODE_VERSION:-0.1.3}"
URICORE_VER="${URISYS_URICORE_VERSION:-0.1.8}"

log() { echo "[bootstrap-lenovo] $*"; }

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  log "WARN: $PYTHON not found — falling back to python3"
  PYTHON=python3
fi

log "venv=$VENV python=$($PYTHON --version 2>&1)"
"$PYTHON" -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install -U pip

URICORE_WHL="${URISYS_URICORE_WHEEL_URL:-https://github.com/tellmesh/uricore/releases/download/v${URICORE_VER}/uricore-${URICORE_VER}-py3-none-any.whl}"
NODE_WHL="${URISYS_NODE_WHEEL_URL:-https://github.com/tellmesh/urisys-node/releases/download/v${NODE_VER}/urisys_node-${NODE_VER}-py3-none-any.whl}"

log "install uricore + uricore + urisys[real]"
python -m pip install -U "$URICORE_WHL" "uricore>=0.1.0" "urisys[real]>=${URISYS_MIN}"

log "install urisys-node wheel"
if ! python -m pip install -U "$NODE_WHL"; then
  log "WARN: GitHub wheel failed — try: export URISYS_NODE_WHEEL_URL=file:///path/to/urisys_node-${NODE_VER}-py3-none-any.whl"
fi

python -c "import uri_control, urisysnode; print('imports OK')" || {
  log "FAIL: missing imports — run: urisys doctor"
  exit 1
}

urisys init --skip-pip || true
mkdir -p "$HOME/.config/urisys"
cat > "$HOME/.config/urisys/node.env" <<EOF
export URISYS_ALLOW_REAL="1"
export URISYS_NODE_AUTO_INSTALL="1"
# start desktop slave:
urisys node serve --host 0.0.0.0 --port 8790
EOF

log "OK — next:"
log "  source $VENV/bin/activate"
log "  urisys node serve --host 0.0.0.0 --port 8790   # NOT ~/.local/bin/urisys-node (system python)"
log "  urisys doctor"
