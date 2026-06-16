from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import Any

from .display import allow_real, detect_display, ensure_screenshot_dir, run_cmd


def display_info(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    display = detect_display(context)
    res = run_cmd(['xdpyinfo'], {**context, 'display': display}, timeout=5)
    screen_line = None
    for line in res.stdout.splitlines():
        if 'dimensions:' in line:
            screen_line = line.strip()
            break
    return {
        'display': display,
        'available': res.returncode == 0,
        'dimensions': screen_line,
        'error': res.stderr.strip() if res.returncode != 0 else None,
    }


def screenshot(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    out_dir = ensure_screenshot_dir(context)
    latest = out_dir / 'latest.png'
    tmp = Path('/tmp/urirdp-latest.png')
    if context.get('dry_run') or not allow_real(context):
        latest.write_bytes(_tiny_png())
        return {'driver': 'mock', 'path': str(latest), 'display': detect_display(context), 'captured': True}

    res = run_cmd(['scrot', str(tmp)], context, timeout=10)
    if res.returncode != 0:
        res2 = run_cmd(['import', '-window', 'root', str(tmp)], context, timeout=10)
        if res2.returncode != 0:
            raise RuntimeError(res.stderr.strip() or res2.stderr.strip() or 'screenshot failed')
    if not tmp.exists() or tmp.stat().st_size < 128:
        raise RuntimeError('screenshot produced empty image')
    shutil.copy2(tmp, latest)
    tmp.unlink(missing_ok=True)
    return {
        'driver': 'scrot/import',
        'path': str(latest),
        'display': detect_display(context),
        'captured': True,
        'size_bytes': latest.stat().st_size,
    }


def click_text(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    text = str(payload.get('text', 'OK'))
    runtime = context['runtime']
    target = context.get('params', {}).get('target', 'local')
    step_ctx = {**context, 'approved': True}

    screenshot_result = runtime.call(f'kvm://{target}/monitor/primary/query/screenshot', {}, step_ctx)
    if not screenshot_result.get('ok'):
        return {
            'clicked': False,
            'target_text': text,
            'reason': 'screenshot failed',
            'error': screenshot_result.get('error'),
            'screenshot': screenshot_result,
        }

    ocr_result = runtime.call(f'ocr://{target}/image/latest/query/text', {}, step_ctx)
    if not ocr_result.get('ok'):
        return {
            'clicked': False,
            'target_text': text,
            'reason': 'ocr failed',
            'error': ocr_result.get('error'),
            'screenshot': screenshot_result.get('result'),
            'ocr': ocr_result,
        }

    tokens = (ocr_result.get('result') or {}).get('tokens') or []
    llm_result = runtime.call(
        f'llm://{target}/vision/query/analyze',
        {'target_text': text, 'tokens': tokens},
        step_ctx,
    )
    if not llm_result.get('ok'):
        return {
            'clicked': False,
            'target_text': text,
            'reason': 'llm failed',
            'error': llm_result.get('error'),
            'screenshot': screenshot_result.get('result'),
            'ocr': ocr_result.get('result'),
            'llm': llm_result,
        }

    action = llm_result.get('result') or {'x': 160, 'y': 120}
    click_result = runtime.call(
        f'him://{target}/mouse/command/click',
        {'x': action.get('x', 160), 'y': action.get('y', 120), 'button': 1},
        step_ctx,
    )
    clicked = bool(click_result.get('ok'))
    return {
        'clicked': clicked,
        'target_text': text,
        'reason': None if clicked else (click_result.get('error') or click_result.get('reason') or 'click failed'),
        'screenshot': screenshot_result.get('result'),
        'ocr': ocr_result.get('result'),
        'llm': action,
        'click': click_result.get('result'),
        'pipeline': {
            'screenshot': {'ok': bool(screenshot_result.get('ok')), 'result': screenshot_result.get('result')},
            'ocr': {'ok': bool(ocr_result.get('ok')), 'result': ocr_result.get('result')},
            'llm': {'ok': bool(llm_result.get('ok')), 'result': action},
            'him': {'ok': bool(click_result.get('ok')), 'result': click_result.get('result')},
        },
    }


def type_text(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    runtime = context['runtime']
    target = context.get('params', {}).get('target', 'local')
    text = str(payload.get('text', 'Hello from urisys RDP'))
    return runtime.call(f'him://{target}/keyboard/command/type', {'text': text}, context).get('result') or {}


def _tiny_png() -> bytes:
    # 1x1 transparent PNG
    return bytes.fromhex(
        '89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489'
        '0000000a49444154789c636000000200015d0b2a0000000049454e44ae426082'
    )
