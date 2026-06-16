#!/usr/bin/env bash
# Install uricore + urisys inside lab containers.
set -euo pipefail

export PIP_DISABLE_PIP_VERSION_CHECK=1

WORKSPACE="${WORKSPACE:-/workspace}"

python3 -m pip install --upgrade pip -q 2>/dev/null || true

if [ -n "${URICORE_PATH:-}" ] && [ -d "$URICORE_PATH" ]; then
  pip install "$URICORE_PATH" -q
elif [ -d "$WORKSPACE/../uricore" ]; then
  pip install "$WORKSPACE/../uricore" -q
else
  echo "INFO: sibling uricore not mounted — installing from PyPI" >&2
  pip install "uricore>=0.1.2" -q
fi

pip install -e "$WORKSPACE" -q
