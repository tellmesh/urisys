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


def _decide_messages(question: str, context_value: Any) -> list[dict[str, str]]:
    context_text = json.dumps(context_value, ensure_ascii=False, default=str)
    if len(context_text) > 12000:
        context_text = context_text[:12000] + '…'
    prompt = (
        'You are a runtime judge for automation workflows. '
        'Return JSON only with keys: ok (bool), decision (retry|abort), reason (string), confidence (0-1). '
        f'Question: {question}\n'
        f'Context:\n{context_text}'
    )
    return [{'role': 'user', 'content': prompt}]


def _mock_decide(question: str, context_value: Any) -> dict[str, Any]:
    blob = json.dumps(context_value or {}, ensure_ascii=False, default=str).lower()
    retry = 'error' in blob or '502' in blob
    return {
        'ok': retry,
        'decision': 'retry' if retry else 'abort',
        'reason': 'mock-decide: critical pattern in context' if retry else 'mock-decide: no critical pattern',
        'confidence': 0.8 if retry else 0.9,
        'model': 'mock-decide',
        'question': question,
    }


def _decide_litellm(messages, model, context, *, temperature, max_tokens):
    if not str(model).startswith('openrouter/') and resolve_env_var('OPENROUTER_API_KEY', context, secret=True):
        model = f'openrouter/{model.lstrip("openrouter/")}'
    return _litellm_chat(messages, model, temperature=temperature, max_tokens=max_tokens), model


def _decide_openai(messages, model, api_key, base_url, context, *, temperature, max_tokens):
    if not base_url:
        base_url = 'https://openrouter.ai/api/v1' if resolve_env_var('OPENROUTER_API_KEY', context, secret=True) else 'https://api.openai.com/v1'
    return _openai_compatible_chat(messages, model, api_key, base_url, temperature, max_tokens), model


def _decision_from_parsed(parsed: dict[str, Any], model: str, question: str) -> dict[str, Any]:
    decision = str(parsed.get('decision') or ('retry' if parsed.get('ok') else 'abort')).lower()
    ok = bool(parsed.get('ok')) if 'ok' in parsed else decision == 'retry'
    return {
        'ok': ok,
        'decision': decision,
        'reason': str(parsed.get('reason') or 'llm-decide'),
        'confidence': float(parsed.get('confidence', 0.7)),
        'model': model,
        'question': question,
    }


def decide(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    cfg = _llm_cfg(context)
    driver = cfg.get('driver', 'mock')
    question = str(payload.get('question') or '')
    context_value = payload.get('context')

    if not question:
        return {'ok': False, 'error': 'payload.question is required'}

    if context.get('dry_run') or not allow_real(context) or driver in ('mock', 'heuristic', 'mock-vision'):
        return _mock_decide(question, context_value)

    model = _env('model', cfg, context)
    api_key = (
        _env('api_key', cfg, context)
        or resolve_env_var('OPENROUTER_API_KEY', context, secret=True)
        or resolve_env_var('OPENAI_API_KEY', context, secret=True)
    )
    base_url = _env('base_url', cfg, context)
    temperature = float(_env('temperature', cfg, context) or '0')
    max_tokens = int(_env('max_tokens', cfg, context) or '512')
    messages = _decide_messages(question, context_value)

    if not model or not api_key:
        return _mock_decide(question, context_value)

    try:
        if driver == 'litellm':
            parsed, model = _decide_litellm(messages, model, context, temperature=temperature, max_tokens=max_tokens)
        elif driver in ('openai', 'openrouter'):
            parsed, model = _decide_openai(messages, model, api_key, base_url, context, temperature=temperature, max_tokens=max_tokens)
        else:
            return _mock_decide(question, context_value)
        return _decision_from_parsed(parsed, model, question)
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError, ValueError, RuntimeError):
        return _mock_decide(question, context_value)


_PHRASE_MAP: list[tuple[str, str, dict[str, Any]]] = [
    ('kliknij ok', 'kvm://local/task/command/click-text', {'text': 'OK'}),
    ('otwórz przeglądark', 'browser://chrome/page/open', {'url': 'http://localhost:8101/health'}),
    ('zrób screenshot', 'kvm://local/monitor/primary/query/screenshot', {}),
    ('status rdp', 'rdp://local/display/query/status', {}),
]


def _match_transcript(text: str) -> tuple[str, dict[str, Any]]:
    lowered = (text or '').lower().strip()
    for phrase, uri, payload in _PHRASE_MAP:
        if phrase in lowered:
            return uri, dict(payload)
    return 'kvm://local/task/command/click-text', {'text': 'OK'}


def plan(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    transcript = str(payload.get('transcript') or payload.get('text') or '').strip()
    if not transcript:
        return {'ok': False, 'error': 'payload.transcript is required'}
    allowed = payload.get('allowed_schemes')
    schemes = [str(s).strip() for s in allowed] if isinstance(allowed, list) else None
    uri, inner_payload = _match_transcript(transcript)
    scheme = uri.split('://', 1)[0]
    if schemes and scheme not in schemes:
        return {
            'ok': False,
            'error': f'scheme {scheme!r} not in allowed_schemes',
            'uri': uri,
            'payload': inner_payload,
            'transcript': transcript,
        }
    return {
        'ok': True,
        'uri': uri,
        'payload': inner_payload,
        'transcript': transcript,
        'model': 'phrase-map',
    }
