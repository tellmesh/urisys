from __future__ import annotations

import argparse
import fnmatch
import importlib
import json
import os
import re
import sys
import time
import uuid
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse, unquote

from .env import load_env_policy


@dataclass
class Route:
    pattern: str
    kind: str
    operation: str
    handler_ref: str
    approval: str = "not_required"
    side_effects: bool = False
    _regex: re.Pattern | None = None

    def compile(self):
        parts = []
        i = 0
        pattern = self.pattern
        while i < len(pattern):
            ch = pattern[i]
            if ch == "{":
                j = pattern.index("}", i)
                name = pattern[i+1:j]
                parts.append(f"(?P<{name}>[^/]+)")
                i = j + 1
            else:
                parts.append(re.escape(ch))
                i += 1
        self._regex = re.compile("^" + "".join(parts) + "$")
        return self

    def match(self, uri: str) -> dict[str, str] | None:
        if self._regex is None:
            self.compile()
        m = self._regex.match(uri)
        if not m:
            return None
        return {k: unquote(v) for k, v in m.groupdict().items()}


class JsonlEventStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: dict[str, Any]):
        with self.path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')


class Runtime:
    def __init__(self, events_path='data/events.jsonl', config: dict[str, Any] | None = None):
        self.routes: list[Route] = []
        self.events = JsonlEventStore(events_path)
        self.config = config or {}
        self.state: dict[str, Any] = {}

    def register(self, pattern: str, handler: str, *, kind='command', operation=None, approval='not_required', side_effects=False):
        op = operation or pattern.rsplit('/', 1)[-1]
        self.routes.append(Route(pattern, kind, op, handler, approval, side_effects).compile())

    def resolve(self, uri: str) -> tuple[Route, dict[str, str]]:
        for route in self.routes:
            params = route.match(uri)
            if params is not None:
                return route, params
        raise KeyError(f'No route for URI: {uri}')

    def _load_handler(self, ref: str) -> Callable[[dict, dict], dict]:
        # python://module:function
        if ref.startswith('python://'):
            ref = ref[len('python://'):]
        module_name, func_name = ref.split(':', 1)
        mod = importlib.import_module(module_name)
        return getattr(mod, func_name)

    def call(self, uri: str, payload: dict[str, Any] | None = None, context: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        context = context or {}
        try:
            route, params = self.resolve(uri)
        except Exception as exc:
            return {'ok': False, 'uri': uri, 'type': 'route_not_found', 'error': str(exc)}

        approved = bool(context.get('approved'))
        if route.side_effects and route.approval == 'required' and not approved:
            return {'ok': False, 'uri': uri, 'type': 'policy_denied', 'reason': 'approval required'}

        ctx = dict(context)
        ctx.update({
            'uri': uri,
            'params': params,
            'config': self.config,
            'runtime': self,
            'state': self.state,
            'event_store': self.events,
        })
        if 'env_config' not in ctx:
            policy = load_env_policy()
            if policy:
                ctx['env_config'] = policy
        event_base = {
            'event_id': str(uuid.uuid4()),
            'source_uri': uri,
            'operation': route.operation,
            'kind': route.kind,
            'params': params,
            'occurred_at_unix_ms': int(time.time() * 1000),
        }
        self.events.append({**event_base, 'event_type': 'operation.accepted', 'payload': payload})
        try:
            handler = self._load_handler(route.handler_ref)
            result = handler(payload, ctx)
            event = {**event_base, 'event_id': str(uuid.uuid4()), 'event_type': f'{route.operation}.completed', 'result': result}
            self.events.append(event)
            return {'ok': True, 'uri': uri, 'operation': route.operation, 'params': params, 'result': result, 'event': event}
        except Exception as exc:
            event = {**event_base, 'event_id': str(uuid.uuid4()), 'event_type': f'{route.operation}.failed', 'error': str(exc)}
            self.events.append(event)
            return {'ok': False, 'uri': uri, 'operation': route.operation, 'error': str(exc), 'event': event}


def load_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    return json.loads(p.read_text(encoding='utf-8'))


def load_yaml_flow(path: str | Path) -> dict[str, Any]:
    text = Path(path).read_text(encoding='utf-8')
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except Exception:
        # ultra-small fallback for the simple examples in this repository
        data = {'do': [], 'defaults': {}}
        current = None
        for raw in text.splitlines():
            line = raw.rstrip()
            if not line or line.strip().startswith('#'):
                continue
            if line.startswith('defaults:'):
                current = 'defaults'
                continue
            if line.startswith('do:'):
                current = 'do'
                continue
            if current == 'do' and line.strip().startswith('- '):
                item = line.strip()[2:]
                if item.endswith(':'):
                    data['do'].append({item[:-1]: {}})
                else:
                    data['do'].append(item)
        return data


def run_flow(runtime: Runtime, path: str, context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    flow = load_yaml_flow(path)
    defaults = dict(flow.get('defaults') or {})
    if context:
        defaults.update(context)
    results = []
    for step in flow.get('do', []):
        if isinstance(step, str):
            uri, payload = step, {}
        elif isinstance(step, dict):
            uri, payload = next(iter(step.items()))
            payload = payload or {}
        else:
            raise ValueError(f'Invalid flow step: {step!r}')
        results.append(runtime.call(uri, payload, defaults))
    return results


def make_handler(runtime: Runtime):
    class Handler(BaseHTTPRequestHandler):
        def _json(self, status: int, data: dict[str, Any]):
            raw = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            if self.path == '/health':
                return self._json(200, {'ok': True, 'service': 'urisys-edge'})
            if self.path == '/uri/routes':
                return self._json(200, {'ok': True, 'routes': [r.pattern for r in runtime.routes]})
            return self._json(404, {'ok': False, 'error': 'not found'})

        def do_POST(self):
            if self.path != '/uri/call':
                return self._json(404, {'ok': False, 'error': 'not found'})
            length = int(self.headers.get('Content-Length') or '0')
            body = self.rfile.read(length).decode('utf-8')
            req = json.loads(body or '{}')
            result = runtime.call(req.get('uri', ''), req.get('payload') or {}, req.get('context') or {})
            return self._json(200 if result.get('ok') else 400, result)
    return Handler


def serve(runtime: Runtime, host: str, port: int):
    server = ThreadingHTTPServer((host, port), make_handler(runtime))
    print(f'urisys-edge listening on http://{host}:{port}')
    print('routes:')
    for r in runtime.routes:
        print(' -', r.pattern)
    server.serve_forever()
