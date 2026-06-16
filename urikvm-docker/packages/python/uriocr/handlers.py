from __future__ import annotations

import base64
import io
import re


def _ocr_cfg(context):
    return context.get('config', {}).get('ocr', {})


def _driver(context):
    return _ocr_cfg(context).get('driver', 'mock')


def _mock_boxes(context):
    cfg = _ocr_cfg(context)
    return cfg.get('mock_boxes') or [
        {'text': 'Start', 'x': 100, 'y': 120, 'w': 80, 'h': 30},
        {'text': 'OK', 'x': 320, 'y': 240, 'w': 60, 'h': 30},
        {'text': 'Cancel', 'x': 400, 'y': 240, 'w': 90, 'h': 30},
    ]


def _latest_screenshot(context):
    return context.get('state', {}).get('latest_screenshot') or {}


def _png_bytes(context):
    shot = _latest_screenshot(context)
    raw = base64.b64decode(shot.get('base64') or '')
    if shot.get('mime') == 'image/png' and raw:
        return raw
    return None


def _tesseract_boxes(png_bytes, lang='eng'):
    try:
        import pytesseract  # type: ignore
        from PIL import Image  # type: ignore
    except Exception as exc:
        raise RuntimeError('tesseract driver requires: pip install pytesseract pillow, and system tesseract-ocr') from exc
    img = Image.open(io.BytesIO(png_bytes))
    data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)
    boxes = []
    n = len(data.get('text') or [])
    for i in range(n):
        text = (data['text'][i] or '').strip()
        if not text:
            continue
        try:
            conf = float(data['conf'][i])
        except (TypeError, ValueError):
            conf = -1.0
        if conf < 0:
            continue
        boxes.append({
            'text': text,
            'x': int(data['left'][i]),
            'y': int(data['top'][i]),
            'w': int(data['width'][i]),
            'h': int(data['height'][i]),
            'confidence': conf / 100.0,
        })
    return boxes


def _merge_word_boxes(boxes):
    if not boxes:
        return boxes
    merged = []
    current = dict(boxes[0])
    for box in boxes[1:]:
        same_line = abs(box['y'] - current['y']) <= max(current.get('h', 0), box.get('h', 0))
        close_x = box['x'] <= current['x'] + current.get('w', 0) + 12
        if same_line and close_x:
            current['text'] = f"{current['text']} {box['text']}".strip()
            right = max(current['x'] + current['w'], box['x'] + box['w'])
            bottom = max(current['y'] + current['h'], box['y'] + box['h'])
            current['x'] = min(current['x'], box['x'])
            current['y'] = min(current['y'], box['y'])
            current['w'] = right - current['x']
            current['h'] = bottom - current['y']
            current['confidence'] = max(current.get('confidence', 0.0), box.get('confidence', 0.0))
        else:
            merged.append(current)
            current = dict(box)
    merged.append(current)
    return merged


def _extract_text(context):
    driver = _driver(context)
    if driver == 'tesseract':
        png = _png_bytes(context)
        if not png:
            raise RuntimeError('tesseract OCR requires a PNG screenshot in state.latest_screenshot')
        lang = _ocr_cfg(context).get('lang', 'eng')
        boxes = _merge_word_boxes(_tesseract_boxes(png, lang=lang))
        if not boxes:
            return {'text': '', 'boxes': [], 'driver': driver, 'warning': 'no text detected'}
        return {'text': ' '.join(b['text'] for b in boxes), 'boxes': boxes, 'driver': driver}
    boxes = _mock_boxes(context)
    return {'text': ' '.join(b['text'] for b in boxes), 'boxes': boxes, 'driver': driver}


def latest_text(payload, context):
    data = _extract_text(context)
    return {'image_id': 'latest', **data}


def image_text(payload, context):
    image_id = context.get('params', {}).get('image_id')
    data = _extract_text(context)
    return {'image_id': image_id, **data}
