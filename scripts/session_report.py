#!/usr/bin/env python3
"""Generate and analyze urisys Docker/RDP test session reports.

Each session directory should contain:
  session.log          — full runner stdout/stderr
  meta.json            — optional session metadata from runner
  responses/*.json     — URI call responses
  screenshots/*.png    — captured screenshots
  events.jsonl         — runtime event log (optional)
  docker-logs.txt      — docker compose logs (optional)

Usage:
  python3 scripts/session_report.py generate SESSION_DIR
  python3 scripts/session_report.py analyze RUN_DIR
  python3 scripts/session_report.py analyze RUN_DIR --write-md

Implementation lives in scripts/report/ (split per project/analysis.toon.yaml).
"""

from __future__ import annotations

from report import (  # noqa: F401
    BASELINE_LABEL,
    Finding,
    FlowOutcome,
    LAB_FLOW_CHECKS,
    MIN_VISION_CONFIDENCE,
    RunAnalysis,
    SessionReport,
    StepResult,
    analyze_run,
    check_declared_expectations,
    check_duplicate_screenshots,
    check_gui_no_effect,
    check_shell_baseline_duplicate,
    check_vision_never_decides,
    generate_report,
    load_flow_outcomes,
    merge_event_summaries,
    resolve_events_paths,
    summarize_events,
    write_run_analysis,
    write_session_report,
)
from report import _analyze_lab_flows, _load_flow_outcomes, _merge_event_summaries, _resolve_events_paths, _summarize_events  # noqa: F401
from report.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
