import base64
import io
import shutil

import pytest

pytest.importorskip("PIL", reason="Pillow not installed")
if shutil.which("tesseract") is None:
    pytest.skip("tesseract OCR binary not installed", allow_module_level=True)

from PIL import Image, ImageDraw, ImageFont

from urikvmedge.runtime import Runtime
import uriocr, urillm


def _png_with_labels(labels):
    img = Image.new('RGB', (640, 360), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
    except OSError:
        font = ImageFont.load_default()
    positions = [(80, 80, 'Start'), (260, 180, 'OK'), (420, 180, 'Cancel')]
    for x, y, text in positions:
        if text not in labels:
            continue
        draw.rectangle((x - 8, y - 8, x + 90, y + 36), outline=(20, 20, 20), width=2, fill=(255, 255, 255))
        draw.text((x, y), text, fill=(0, 0, 0), font=font)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


def _runtime(ocr_driver='tesseract', llm_driver='heuristic'):
    rt = Runtime(events_path='/tmp/urikvm-ocr-test-events.jsonl', config={
        'ocr': {'driver': ocr_driver, 'lang': 'eng'},
        'llm': {'driver': llm_driver, 'model': 'gpt-4o-mini'},
    })
    uriocr.register(rt)
    urillm.register(rt)
    return rt


def _inject_png(rt, png_bytes):
    rt.state['latest_screenshot'] = {
        'monitor': 'primary',
        'driver': 'test',
        'mime': 'image/png',
        'base64': base64.b64encode(png_bytes).decode('ascii'),
        'width': 640,
        'height': 360,
    }


def test_tesseract_finds_ok():
    rt = _runtime()
    _inject_png(rt, _png_with_labels(['Start', 'OK', 'Cancel']))
    res = rt.call('ocr://local/image/latest/query/text')
    assert res['ok']
    assert 'OK' in res['result']['text']
    ok_boxes = [b for b in res['result']['boxes'] if 'OK' in b['text']]
    assert ok_boxes


def test_heuristic_llm_clicks_ok_from_ocr():
    rt = _runtime(llm_driver='heuristic')
    _inject_png(rt, _png_with_labels(['Start', 'OK', 'Cancel']))
    ocr = rt.call('ocr://local/image/latest/query/text')
    analysis = rt.call('llm://local/vision/query/analyze', {'goal': 'click OK', 'target_text': 'OK', 'ocr': ocr['result']})
    assert analysis['ok']
    assert analysis['result']['action'] == 'click'
    assert analysis['result']['target_text'] == 'OK'
    assert analysis['result']['x'] > 200
    assert analysis['result']['y'] > 100


@pytest.mark.skipif(not __import__('os').environ.get('OPENAI_API_KEY'), reason='OPENAI_API_KEY not set')
def test_openai_vision_clicks_ok_from_image():
    rt = _runtime(llm_driver='openai')
    _inject_png(rt, _png_with_labels(['OK']))
    ocr = rt.call('ocr://local/image/latest/query/text')
    analysis = rt.call('llm://local/vision/query/analyze', {'goal': 'click OK', 'target_text': 'OK', 'ocr': ocr['result']})
    assert analysis['ok']
    assert analysis['result']['action'] == 'click'
    assert 'openai' in analysis['result']['source']
