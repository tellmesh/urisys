from __future__ import annotations
import base64
import os
import time
import webbrowser
from pathlib import Path


def _profile(context):
    return context.get('config', {}).get('browser', {})


def _session_state(context):
    session = context.get('params', {}).get('session', 'default')
    state = context.setdefault('state', {})
    sessions = state.setdefault('browser_sessions', {})
    return sessions.setdefault(session, {'url': None, 'title': None, 'html': '<html><body>empty</body></html>'})


def status(payload, context):
    profile = _profile(context)
    session = context.get('params', {}).get('session', 'default')
    sess = _session_state(context)
    return {
        'session': session,
        'driver': profile.get('driver', 'mock'),
        'url': sess.get('url'),
        'title': sess.get('title'),
        'supports': ['mock', 'system-open', 'playwright', 'remote-cdp'],
    }


def open_page(payload, context):
    profile = _profile(context)
    driver = payload.get('driver') or profile.get('driver', 'mock')
    url = payload.get('url')
    if not url:
        raise ValueError('payload.url is required')
    sess = _session_state(context)
    if context.get('dry_run'):
        return {'driver': driver, 'url': url, 'dry_run': True, 'would_open': True}

    if driver == 'system-open':
        if not context.get('allow_real') and not os.environ.get('URISYS_ALLOW_REAL'):
            raise PermissionError('system-open requires context.allow_real=true or URISYS_ALLOW_REAL=1')
        webbrowser.open(url)
        title = 'Opened by system browser'
        html = '<html><body>Opened in external browser</body></html>'
    elif driver == 'playwright':
        # Optional dependency. Keep the example portable by failing clearly if missing.
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except Exception as exc:
            raise RuntimeError('playwright driver requires: pip install playwright && playwright install chromium') from exc
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=bool(profile.get('headless', True)))
            page = browser.new_page()
            page.goto(url)
            title = page.title()
            html = page.content()
            browser.close()
    elif driver == 'remote-cdp':
        # Placeholder: route to a remote Chrome DevTools Protocol bridge in a real deployment.
        cdp_url = profile.get('remote_cdp_url', 'ws://chrome:9222/devtools/browser')
        title = 'Remote CDP placeholder'
        html = f'<html><body>Would call remote CDP at {cdp_url}</body></html>'
    else:
        title = payload.get('title') or 'Mock page'
        html = f'<html><head><title>{title}</title></head><body><h1>Mock Browser</h1><p>{url}</p></body></html>'

    sess.update({'url': url, 'title': title, 'html': html, 'opened_at': time.time(), 'driver': driver})
    return {'session': context.get('params', {}).get('session'), 'driver': driver, 'url': url, 'title': title}


def get_dom(payload, context):
    sess = _session_state(context)
    return {'html': sess.get('html'), 'url': sess.get('url'), 'title': sess.get('title')}


def submit_form(payload, context):
    profile = _profile(context)
    driver = payload.get('driver') or profile.get('driver', 'mock')
    form_id = str(payload.get('form_id') or payload.get('id') or 'default')
    fields = payload.get('fields') or {}
    sess = _session_state(context)
    if context.get('dry_run'):
        return {
            'dry_run': True,
            'driver': driver,
            'form_id': form_id,
            'fields': fields,
            'url': sess.get('url'),
        }
    return {
        'submitted': True,
        'driver': driver,
        'form_id': form_id,
        'fields': fields,
        'url': sess.get('url'),
        'mock': driver == 'mock',
    }

    sess = _session_state(context)
    if context.get('dry_run'):
        return {'dry_run': True, 'would_capture': True}
    # Portable mock screenshot artifact. Real playwright implementation can be plugged into this same URI.
    data = f"Screenshot placeholder for {sess.get('url') or 'about:blank'}".encode('utf-8')
    b64 = base64.b64encode(data).decode('ascii')
    return {'mime': 'text/plain', 'base64': b64, 'url': sess.get('url'), 'driver': sess.get('driver', 'mock')}
