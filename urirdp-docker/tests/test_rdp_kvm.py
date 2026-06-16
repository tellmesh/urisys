from urirdpedge.cli import build_runtime


class Args:
    packs = 'rdp,kvm,him,ocr,llm'
    config = 'config/rdp-kvm-profile.json'
    events = 'data/test-events.jsonl'


def test_routes_registered():
    rt = build_runtime(Args())
    routes = [r.pattern for r in rt.routes]
    assert 'rdp://{target}/session/query/status' in routes
    assert 'rdp://{target}/display/query/status' in routes
    assert 'kvm://{target}/task/command/click-text' in routes
    assert 'him://{target}/mouse/command/click' in routes


def test_rdp_display_status_mock():
    rt = build_runtime(Args())
    result = rt.call('rdp://local/display/query/status', {}, {'dry_run': True})
    assert result['ok'] is True
    assert 'display_exists' in result['result']
    assert 'xdpyinfo_ok' in result['result']
    assert 'screenshot_ok' in result['result']


def test_kvm_click_text_dry_run_pipeline():
    rt = build_runtime(Args())
    result = rt.call(
        'kvm://local/task/command/click-text',
        {'text': 'OK'},
        {'approved': True, 'dry_run': True},
    )
    assert result['ok'] is True
    pipe = result['result']['pipeline']
    assert all(pipe[k]['ok'] for k in ('screenshot', 'ocr', 'llm', 'him'))


def test_rdp_status():
    rt = build_runtime(Args())
    result = rt.call('rdp://local/session/query/status')
    assert result['ok'] is True
    assert 'xrdp' in result['result']


def test_kvm_click_text_dry_run():
    rt = build_runtime(Args())
    result = rt.call(
        'kvm://local/task/command/click-text',
        {'text': 'OK'},
        {'approved': True, 'dry_run': True},
    )
    assert result['ok'] is True
    assert result['result']['clicked'] is True
    assert result['result']['click']['driver'] == 'mock'


def test_kvm_click_text_real_without_display():
    rt = build_runtime(Args())
    result = rt.call(
        'kvm://local/task/command/click-text',
        {'text': 'OK'},
        {'approved': True, 'allow_real': True},
    )
    assert result['ok'] is True
    assert result['result']['clicked'] is False
    assert result['result']['reason'] in {'screenshot failed', 'ocr failed', 'click failed'}


def test_him_requires_approval():
    rt = build_runtime(Args())
    result = rt.call('him://local/mouse/command/click', {'x': 1, 'y': 2})
    assert result['ok'] is False
    assert result['type'] == 'policy_denied'
