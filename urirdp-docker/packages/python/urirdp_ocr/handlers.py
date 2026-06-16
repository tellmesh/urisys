from __future__ import annotations

import csv
import io
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from urirdp_kvm.display import allow_real, run_cmd


def _mock_ocr() -> dict[str, Any]:
    return {
        'engine': 'mock',
        'text': 'OK\nCancel\nSettings',
        'tokens': [
            {'text': 'OK', 'x': 110, 'y': 110, 'w': 50, 'h': 24},
            {'text': 'Cancel', 'x': 220, 'y': 110, 'w': 90, 'h': 24},
            {'text': 'Settings', 'x': 110, 'y': 170, 'w': 120, 'h': 24},
        ],
    }


def _parse_tesseract_tsv(tsv_text: str) -> list[dict[str, Any]]:
    tokens: list[dict[str, Any]] = []
    reader = csv.DictReader(io.StringIO(tsv_text), delimiter='\t')
    for row in reader:
        text = (row.get('text') or '').strip()
        if not text or text == '':
            continue
        try:
            conf = float(row.get('conf', -1))
        except (TypeError, ValueError):
            conf = -1.0
        if conf < 0:
            continue
        tokens.append({
            'text': text,
            'x': int(float(row.get('left', 0))),
            'y': int(float(row.get('top', 0))),
            'w': int(float(row.get('width', 0))),
            'h': int(float(row.get('height', 0))),
            'confidence': conf / 100.0,
        })
    return tokens


def _tesseract_ocr(path: Path, context: dict[str, Any]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        out_base = Path(tmp) / 'ocr'
        res = run_cmd(['tesseract', str(path), str(out_base), '-l', 'eng', 'tsv'], context, timeout=30)
        if res.returncode != 0:
            raise RuntimeError(res.stderr.strip() or 'tesseract failed')
        tsv_path = Path(str(out_base) + '.tsv')
        txt_path = Path(str(out_base) + '.txt')
        if not tsv_path.exists():
            text_res = run_cmd(['tesseract', str(path), 'stdout', '-l', 'eng'], context, timeout=30)
            if text_res.returncode != 0:
                raise RuntimeError(text_res.stderr.strip() or 'tesseract failed')
            return {'engine': 'tesseract', 'path': str(path), 'text': text_res.stdout, 'tokens': []}
        text = txt_path.read_text(encoding='utf-8', errors='replace') if txt_path.exists() else ''
        tokens = _parse_tesseract_tsv(tsv_path.read_text(encoding='utf-8', errors='replace'))
        if not text:
            text = ' '.join(t['text'] for t in tokens)
        return {'engine': 'tesseract', 'path': str(path), 'text': text, 'tokens': tokens}


def latest_text(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    screenshot_dir = Path((context.get('config') or {}).get('screenshot_dir', 'data/screenshots'))
    image_path = screenshot_dir / 'latest.png'
    return image_text({'path': str(image_path)}, context)


def image_text(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    path = Path(payload.get('path') or payload.get('image') or '')
    if context.get('dry_run') or not allow_real(context) or not path.exists():
        return _mock_ocr()
    return _tesseract_ocr(path, context)
