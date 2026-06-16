from uribrowseredge.runtime import Runtime
import uribrowserdocker


def runtime():
    rt = Runtime(events_path='/tmp/uribrowser-test-events.jsonl', config={'browser': {'driver': 'mock'}})
    uribrowserdocker.register(rt)
    return rt


def test_open_requires_approval():
    res = runtime().call('browser://default/page/command/open', {'url': 'https://example.com'})
    assert not res['ok']
    assert res['type'] == 'policy_denied'


def test_open_and_dom():
    rt = runtime()
    res = rt.call('browser://default/page/command/open', {'url': 'https://example.com'}, {'approved': True})
    assert res['ok']
    dom = rt.call('browser://default/page/query/dom')
    assert dom['ok']
    assert 'https://example.com' in dom['result']['html']
