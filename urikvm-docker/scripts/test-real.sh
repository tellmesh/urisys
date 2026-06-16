#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m pip install -e ".[real]" >/dev/null

CFG=config/kvm-profile.real.json
export URISYS_ALLOW_REAL=1

echo "== kvm real: mss screenshot =="
urisys-kvm --config "$CFG" call kvm://local/monitor/primary/query/screenshot --approve --allow-real \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['ok'] and d['result']['driver']=='mss'; print('screenshot', d['result']['width'], 'x', d['result']['height'])"

if xdpyinfo -display "${DISPLAY:-:0}" >/dev/null 2>&1 && python3 -c "import pyautogui; pyautogui.position()" >/dev/null 2>&1; then
  HIM_ENV=()
  echo "== kvm real: him via host display ${DISPLAY:-:0} =="
else
  echo "== kvm real: him via xvfb (no X auth on host display) =="
  HIM_ENV=(xvfb-run -a)
fi

run_kvm() {
  if [ "${#HIM_ENV[@]}" -gt 0 ]; then
    "${HIM_ENV[@]}" urisys-kvm --config "$CFG" "$@"
  else
    urisys-kvm --config "$CFG" "$@"
  fi
}

echo "== kvm real: click-text (tesseract + llm + pyautogui, synthetic fixture on xvfb) =="
if [ "${#HIM_ENV[@]}" -gt 0 ]; then
  "${HIM_ENV[@]}" python3 scripts/real_pipeline.py --allow-real --synthetic --text OK \
    | python3 -c "import sys,json; d=json.load(sys.stdin); r=d['result']; assert d['ok'] and r['clicked']; assert r.get('ocr',{}).get('driver')=='tesseract'; print('click', r['target_text'], 'at', r['x'], r['y'], 'llm', r.get('analysis',{}).get('source'))"
else
  python3 scripts/real_pipeline.py --allow-real --text OK \
    | python3 -c "import sys,json; d=json.load(sys.stdin); r=d['result']; assert d['ok'] and r['clicked']; assert r.get('ocr',{}).get('driver')=='tesseract'; print('click', r['target_text'], 'at', r['x'], r['y'], 'llm', r.get('analysis',{}).get('source'))"
fi

echo "== kvm real: him mouse move =="
run_kvm call him://local/mouse/command/move \
  --payload '{"x":100,"y":100}' --approve --allow-real \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['ok']; print('move ok', d['result'])"

echo "== kvm real: flow =="
run_kvm flow flows/kvm-click-ok.uri.flow.yaml --approve --allow-real \
  | python3 -c "import sys,json; steps=json.load(sys.stdin); assert all(s['ok'] for s in steps); print('flow ok, steps:', len(steps))"

echo "ALL REAL KVM TESTS PASSED"
