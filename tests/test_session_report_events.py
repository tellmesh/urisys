"""Unit tests for session_report event summarization."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from session_report import _summarize_events  # noqa: E402


def test_summarize_events_api_json(tmp_path: Path):
    events = {
        "ok": True,
        "events": [
            {
                "event_type": "screen.capture.completed",
                "operation": "screen.capture",
                "occurred_at_unix_ms": 1781642696201,
            },
            {
                "event_type": "node.indicator_on.completed",
                "operation": "node.indicator_on",
                "occurred_at_unix_ms": 1781642696414,
            },
        ],
    }
    path = tmp_path / "events.json"
    path.write_text(json.dumps(events), encoding="utf-8")

    summary = _summarize_events(path)

    assert summary["count"] == 2
    assert summary["kinds"]["screen.capture.completed"] == 1
    assert summary["kinds"]["node.indicator_on.completed"] == 1


def test_summarize_events_jsonl(tmp_path: Path):
    path = tmp_path / "events.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps({"event_type": "a.completed", "occurred_at_unix_ms": 1000}),
                json.dumps({"event_type": "b.failed", "error": "boom", "occurred_at_unix_ms": 2000}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = _summarize_events(path)

    assert summary["count"] == 2
    assert len(summary["failures"]) == 1
    assert summary["failures"][0]["event_type"] == "b.failed"
