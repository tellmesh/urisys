#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHONPATH="vendor/uricore/core/python:packages/python/urisysedge/src:packages/python/urienv/src" python -m pytest tests/test_urienv.py -q
