#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${PORT:-8088}"

echo "Serving http://127.0.0.1:${PORT}/index.html"
cd "$DIR"
python3 -m http.server "$PORT" --bind 127.0.0.1
