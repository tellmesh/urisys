#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m pip install -e ".[real]" >/dev/null
python -m playwright install chromium >/dev/null 2>&1 || true

CFG=config/browser-profile.real.json
echo "== browser real: status =="
urisys-browser --config "$CFG" call browser://default/query/status

echo "== browser real: playwright open =="
urisys-browser --config "$CFG" call browser://default/page/command/open \
  --payload '{"url":"https://example.com"}' \
  --approve --allow-real

echo "== browser real: flow (open + dom + screenshot) =="
urisys-browser --config "$CFG" flow flows/browser-demo.uri.flow.yaml --approve --allow-real \
  | python3 -c "
import sys, json
steps = json.load(sys.stdin)
assert all(s['ok'] for s in steps), steps
dom = next(s for s in steps if s['uri'].endswith('/page/query/dom'))
assert dom['result']['title'] == 'Example Domain', dom['result']
assert dom['result']['url'] == 'https://example.com'
print('flow ok, steps:', len(steps), 'title:', dom['result']['title'])
"

echo "ALL REAL BROWSER TESTS PASSED"
