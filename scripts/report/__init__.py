"""Session report generation and run analysis."""

from __future__ import annotations

from .cli import main
from .events import merge_event_summaries, resolve_events_paths, summarize_events
from .lab_checks import (
    LAB_FLOW_CHECKS,
    analyze_lab_flows,
    check_declared_expectations,
    check_duplicate_screenshots,
    check_gui_no_effect,
    check_shell_baseline_duplicate,
    check_vision_never_decides,
    load_flow_outcomes,
)
from .models import (
    BASELINE_LABEL,
    MIN_VISION_CONFIDENCE,
    Finding,
    FlowOutcome,
    RunAnalysis,
    SessionReport,
    StepResult,
)
from .run_analysis import analyze_run, write_run_analysis
from .session import generate_report
from .session_io import write_session_report

__all__ = [
    "BASELINE_LABEL",
    "Finding",
    "FlowOutcome",
    "LAB_FLOW_CHECKS",
    "MIN_VISION_CONFIDENCE",
    "RunAnalysis",
    "SessionReport",
    "StepResult",
    "analyze_lab_flows",
    "analyze_run",
    "check_declared_expectations",
    "check_duplicate_screenshots",
    "check_gui_no_effect",
    "check_shell_baseline_duplicate",
    "check_vision_never_decides",
    "generate_report",
    "load_flow_outcomes",
    "main",
    "merge_event_summaries",
    "resolve_events_paths",
    "summarize_events",
    "write_run_analysis",
    "write_session_report",
]

# Backward-compatible private aliases for tests importing from session_report.py
_summarize_events = summarize_events
_resolve_events_paths = resolve_events_paths
_merge_event_summaries = merge_event_summaries
_load_flow_outcomes = load_flow_outcomes
_analyze_lab_flows = analyze_lab_flows
