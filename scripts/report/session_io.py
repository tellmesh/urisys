from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .session import generate_report
from .session_markdown import render_session_markdown
from .models import SessionReport


def write_session_report(session_dir: Path, report: SessionReport | None = None) -> tuple[Path, Path]:
    session_dir = session_dir.resolve()
    report = report or generate_report(session_dir)
    json_path = session_dir / "report.json"
    md_path = session_dir / "report.md"
    json_path.write_text(json.dumps(asdict(report), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_session_markdown(report), encoding="utf-8")
    return json_path, md_path
