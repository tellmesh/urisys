#!/usr/bin/env python3
"""Run real click-text pipeline in one process (shared screenshot state)."""
from __future__ import annotations

import argparse
import base64
import io
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'packages' / 'python'))

from urikvmedge.runtime import Runtime, load_json  # noqa: E402
import urihim, uriocr, urillm, urikvm  # noqa: E402


def _png_with_labels(labels):
    img = Image.new('RGB', (640, 360), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
    except OSError:
        font = ImageFont.load_default()
    for x, y, text in [(80, 80, 'Start'), (260, 180, 'OK'), (420, 180, 'Cancel')]:
        if text not in labels:
            continue
        draw.rectangle((x - 8, y - 8, x + 90, y + 36), outline=(20, 20, 20), width=2, fill=(255, 255, 255))
        draw.text((x, y), text, fill=(0, 0, 0), font=font)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


def _inject_png(rt, png_bytes):
    rt.state['latest_screenshot'] = {
        'monitor': 'primary',
        'driver': 'fixture',
        'mime': 'image/png',
        'base64': base64.b64encode(png_bytes).decode('ascii'),
        'width': 640,
        'height': 360,
    }


def build_runtime(config_path: str) -> Runtime:
    config = load_json(config_path)
    rt = Runtime(events_path='data/events-real-pipeline.jsonl', config=config)
    urihim.register(rt)
    uriocr.register(rt)
    urillm.register(rt)
    urikvm.register(rt)
    return rt


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--config', default='config/kvm-profile.real.json')
    p.add_argument('--text', default='OK', help='Target text to click')
    p.add_argument('--synthetic', action='store_true', help='Use synthetic PNG instead of mss screenshot')
    p.add_argument('--allow-real', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()

    ctx = {'approved': True, 'allow_real': args.allow_real, 'dry_run': args.dry_run}
    rt = build_runtime(str(ROOT / args.config))

    payload = {'text': args.text}
    if args.synthetic:
        _inject_png(rt, _png_with_labels(['Start', 'OK', 'Cancel']))
        payload['skip_screenshot'] = True
    else:
        shot = rt.call('kvm://local/monitor/primary/query/screenshot', {}, ctx)
        if not shot.get('ok'):
            print(json.dumps(shot, indent=2))
            return 1
        ocr = rt.call('ocr://local/image/latest/query/text', {}, ctx)
        boxes = (ocr.get('result') or {}).get('boxes') or []
        if boxes and args.text == 'OK':
            preferred = [b for b in boxes if (b.get('text') or '').upper() == 'OK']
            if preferred:
                payload['text'] = preferred[0]['text']
            else:
                payload['text'] = boxes[0]['text']

    res = rt.call('kvm://local/task/command/click-text', payload, ctx)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0 if res.get('ok') and (res.get('result') or {}).get('clicked') else 1


if __name__ == '__main__':
    raise SystemExit(main())
