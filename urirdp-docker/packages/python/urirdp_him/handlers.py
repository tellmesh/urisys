from __future__ import annotations

from typing import Any
from urirdp_kvm.display import allow_real, run_cmd, detect_display


def _mock(action: str, payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return {'driver': 'mock', 'action': action, 'payload': payload, 'display': detect_display(context)}


def mouse_move(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    x, y = int(payload.get('x', 0)), int(payload.get('y', 0))
    if context.get('dry_run') or not allow_real(context):
        return _mock('mousemove', {'x': x, 'y': y}, context)
    res = run_cmd(['xdotool', 'mousemove', str(x), str(y)], context)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or 'xdotool mousemove failed')
    return {'driver': 'xdotool', 'moved': True, 'x': x, 'y': y, 'display': detect_display(context)}


def mouse_click(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    x = int(payload.get('x', 0)) if 'x' in payload else None
    y = int(payload.get('y', 0)) if 'y' in payload else None
    button = str(payload.get('button', 1))
    if context.get('dry_run') or not allow_real(context):
        return _mock('click', {'x': x, 'y': y, 'button': button}, context)
    if x is not None and y is not None:
        move = run_cmd(['xdotool', 'mousemove', str(x), str(y)], context)
        if move.returncode != 0:
            raise RuntimeError(move.stderr.strip() or 'xdotool mousemove failed')
    res = run_cmd(['xdotool', 'click', button], context)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or 'xdotool click failed')
    return {'driver': 'xdotool', 'clicked': True, 'x': x, 'y': y, 'button': button, 'display': detect_display(context)}


def keyboard_type(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    text = str(payload.get('text', ''))
    delay = str(int(payload.get('delay_ms', 10)))
    if context.get('dry_run') or not allow_real(context):
        return _mock('type', {'text': text, 'delay_ms': delay}, context)
    res = run_cmd(['xdotool', 'type', '--delay', delay, text], context)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or 'xdotool type failed')
    return {'driver': 'xdotool', 'typed': True, 'length': len(text), 'display': detect_display(context)}


def keyboard_key(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    key = str(payload.get('key', 'Return'))
    if context.get('dry_run') or not allow_real(context):
        return _mock('key', {'key': key}, context)
    res = run_cmd(['xdotool', 'key', key], context)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or 'xdotool key failed')
    return {'driver': 'xdotool', 'pressed': key, 'display': detect_display(context)}


def keyboard_type_text(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return keyboard_type(payload, context)


def keyboard_hotkey(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    keys = payload.get('keys') or []
    if not keys:
        raise ValueError('payload.keys required for hotkey')
    combo = '+'.join(str(k) for k in keys)
    if context.get('dry_run') or not allow_real(context):
        return _mock('hotkey', {'keys': keys}, context)
    res = run_cmd(['xdotool', 'key', combo], context)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or 'xdotool hotkey failed')
    return {'driver': 'xdotool', 'hotkey': combo, 'display': detect_display(context)}
