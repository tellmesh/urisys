from __future__ import annotations

import base64
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from urirdp_kvm.display import allow_real
from urirdpedge.env import is_secret_env, resolve_env_var


def _config(context: dict[str, Any]) -> dict[str, Any]:
    return context.get('config') or {}


def _llm_cfg(context: dict[str, Any]) -> dict[str, Any]:
    cfg = _config(context)
    llm = dict(cfg.get('llm') or {})
    drivers = cfg.get('drivers') or {}
    driver = llm.get('driver') or drivers.get('llm') or 'mock-vision'
    if driver == 'mock-vision':
        driver = 'mock'
    llm.setdefault('driver', driver)
    return llm


def _env(name: str, cfg: dict[str, Any], context: dict[str, Any], default: str | None = None) -> str | None:
    env_name = cfg.get(f'{name}_env') or name.upper()
    explicit = cfg.get(name)
    if explicit is not None:
        return str(explicit)
    return resolve_env_var(env_name, context, secret=is_secret_env(env_name), default=default)


def _target(payload: dict[str, Any]) -> str:
    return str(payload.get('target_text') or payload.get('text') or '').lower()


def _heuristic(tokens: list[dict[str, Any]], target: str, source: str) -> dict[str, Any]:
    for tok in tokens:
        text = str(tok.get('text', ''))
        if target and target in text.lower():
            return {
                'model': source,
                'action': 'click',
                'target_text': text,
                'x': int(tok.get('x', 0)) + int(tok.get('w', 0)) // 2,
                'y': int(tok.get('y', 0)) + int(tok.get('h', 0)) // 2,
                'confidence': float(tok.get('confidence', 0.9)),
                'reason': f"Found text {text!r}",
            }
    if tokens:
        tok = tokens[0]
        return {
            'model': source,
            'action': 'click',
            'target_text': tok.get('text'),
            'x': int(tok.get('x', 0)) + int(tok.get('w', 0)) // 2,
            'y': int(tok.get('y', 0)) + int(tok.get('h', 0)) // 2,
            'confidence': 0.35,
            'reason': 'Fallback first token',
        }
    return {'model': source, 'action': 'none', 'confidence': 0.0, 'reason': 'No OCR tokens'}


def _parse_json_response(text: str) -> dict[str, Any]:
    text = (text or '').strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def _screenshot_b64(context: dict[str, Any]) -> str | None:
    cfg = _config(context)
    shot_dir = Path(cfg.get('screenshot_dir', 'data/screenshots'))
    path = shot_dir / 'latest.png'
    if not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode('ascii')


def _vision_messages(target: str, tokens: list[dict[str, Any]], png_b64: str | None) -> list[dict[str, Any]]:
    prompt = (
        f'You are a UI automation assistant. Click the UI element matching target text: {target or "unspecified"}. '
        'Return JSON only with keys action, x, y, target_text, confidence. '
        'Use action=click when found, otherwise action=none. '
        'Coordinates must be pixel center in the screenshot.'
    )
    if tokens:
        prompt += f' OCR tokens: {json.dumps(tokens[:40])}.'
    content: list[dict[str, Any]] = [{'type': 'text', 'text': prompt}]
    if png_b64:
        content.append({'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{png_b64}'}})
    return [{'role': 'user', 'content': content}]


def _openai_compatible_chat(messages, model, api_key, base_url, temperature=0.0, max_tokens=1024):
    url = base_url.rstrip('/') + '/chat/completions'
    body = json.dumps({
        'model': model,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
    }).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=body,
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    return _parse_json_response(data['choices'][0]['message']['content'])


def _litellm_chat(messages, model, temperature=0.0, max_tokens=1024):
    try:
        import litellm  # type: ignore
    except Exception as exc:
        raise RuntimeError('litellm driver requires: pip install litellm') from exc
    response = litellm.completion(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return _parse_json_response(response.choices[0].message.content)


def _normalize(parsed: dict[str, Any], model: str) -> dict[str, Any]:
    action = (parsed.get('action') or 'none').lower()
    if action != 'click':
        return {'model': model, 'action': 'none', 'confidence': float(parsed.get('confidence', 0.0)), 'reason': 'llm-no-click'}
    return {
        'model': model,
        'action': 'click',
        'target_text': parsed.get('target_text'),
        'x': int(parsed['x']),
        'y': int(parsed['y']),
        'confidence': float(parsed.get('confidence', 0.8)),
        'reason': parsed.get('reason') or 'llm-vision',
    }


def analyze(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    cfg = _llm_cfg(context)
    driver = cfg.get('driver', 'mock')
    target = _target(payload)
    tokens = payload.get('tokens') or []

    if context.get('dry_run') or not allow_real(context):
        return _heuristic(tokens, target, 'mock-vision')

    if driver in ('mock', 'heuristic'):
        return _heuristic(tokens, target, 'mock-vision')

    model = _env('model', cfg, context)
    api_key = (
        _env('api_key', cfg, context)
        or resolve_env_var('OPENROUTER_API_KEY', context, secret=True)
        or resolve_env_var('OPENAI_API_KEY', context, secret=True)
    )
    base_url = _env('base_url', cfg, context)
    temperature = float(_env('temperature', cfg, context) or '0')
    max_tokens = int(_env('max_tokens', cfg, context) or '1024')
    png_b64 = _screenshot_b64(context)
    messages = _vision_messages(target, tokens, png_b64)

    if not model or not api_key:
        return _heuristic(tokens, target, 'heuristic-fallback')

    try:
        if driver == 'litellm':
            if not str(model).startswith('openrouter/') and resolve_env_var('OPENROUTER_API_KEY', context, secret=True):
                model = f'openrouter/{model.lstrip("openrouter/")}'
            parsed = _litellm_chat(messages, model, temperature=temperature, max_tokens=max_tokens)
            return _normalize(parsed, model)
        if driver in ('openai', 'openrouter'):
            if not base_url:
                base_url = 'https://openrouter.ai/api/v1' if resolve_env_var('OPENROUTER_API_KEY', context, secret=True) else 'https://api.openai.com/v1'
            parsed = _openai_compatible_chat(messages, model, api_key, base_url, temperature, max_tokens)
            return _normalize(parsed, model)
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError, ValueError, RuntimeError):
        return _heuristic(tokens, target, 'heuristic-fallback')

    return _heuristic(tokens, target, 'heuristic-fallback')
