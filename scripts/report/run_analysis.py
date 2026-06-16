from __future__ import annotations

import json
import statistics
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .lab_checks import analyze_lab_flows
from .models import RunAnalysis
from .run_markdown import render_run_analysis_markdown
from .session_io import write_session_report
from .util import host_id, now_iso, read_json

_LOG_HINTS = ("Can't open X display", "port is already allocated", "parse error", "assert")


def _session_row(data: dict[str, Any], report_path: Path, run_dir: Path) -> dict[str, Any]:
    steps = data.get("steps") or []
    return {
        "session_name": data.get("session_name"),
        "suite": data.get("suite"),
        "status": str(data.get("status") or "error"),
        "duration_s": data.get("duration_s"),
        "steps_pass": data.get("passed") if "passed" in data else sum(1 for s in steps if s.get("status") == "pass"),
        "steps_fail": data.get("failed") if "failed" in data else sum(1 for s in steps if s.get("status") == "fail"),
        "report": str(report_path.relative_to(run_dir)),
    }


def _findings_for_session(data: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    status = str(data.get("status") or "error")
    if status != "pass":
        findings.append(f"Session `{data.get('session_name')}` ({data.get('suite')}) **FAILED**.")
        log_tail = data.get("log_tail") or ""
        for needle in _LOG_HINTS:
            if needle.lower() in log_tail.lower():
                findings.append(f"  - log hint: `{needle}` in {data.get('session_name')}")
    for step in data.get("steps") or []:
        if step.get("status") == "fail":
            findings.append(f"  - step `{step.get('name')}` failed: {(step.get('detail') or '')[:120]}")
    for fail in (data.get("events_summary") or {}).get("failures") or []:
        findings.append(
            f"  - event failure in `{data.get('session_name')}`: {fail.get('event_type')} — "
            f"{fail.get('error')[:100]}"
        )
    return findings


def _run_recommendations(findings: list[str], summary: dict[str, int]) -> list[str]:
    recommendations: list[str] = []
    if any("Can't open X display" in f for f in findings):
        recommendations.append(
            "Uruchamiaj `bootstrap-rdp-session.sh` przed realnymi testami GUI lub dodaj auto-bootstrap do compose healthcheck."
        )
    if any("port is already allocated" in f for f in findings):
        recommendations.append(
            "Zatrzymaj stack labu (`docker-down.sh`) przed testami urirdp na portach 3389/8795."
        )
    if summary.get("fail", 0) == 0 and summary.get("pass", 0) > 0:
        if any("screenshot identyczny" in f or "shell/TUI bez efektu" in f for f in findings):
            recommendations.append(
                "Sesja PASS transportowo, ale analiza wykryła duplikaty screenshotów — "
                "przejrzyj Findings i kontrakty `expect:` przed uznaniem runu za w pełni wiarygodny."
            )
        else:
            recommendations.append(
                "Wszystkie sesje przeszły — rozważ dodanie tych testów do CI jako nightly job z archiwizacją raportów."
            )
    return recommendations


def analyze_run(run_dir: Path) -> RunAnalysis:
    run_dir = run_dir.resolve()
    manifest = read_json(run_dir / "manifest.json") or {}
    run_id = str(manifest.get("run_id") or run_dir.name)

    sessions: list[dict[str, Any]] = []
    summary = {"pass": 0, "fail": 0, "error": 0, "total": 0}
    findings: list[str] = []
    recommendations: list[str] = []
    durations: list[float] = []

    for child in sorted(run_dir.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        report_path = child / "report.json"
        if not report_path.is_file():
            report_path, _ = write_session_report(child)
        data = read_json(report_path) or {}
        status = str(data.get("status") or "error")
        summary["total"] += 1
        summary[status] = summary.get(status, 0) + 1
        durations.append(float(data.get("duration_s") or 0))
        sessions.append(_session_row(data, report_path, run_dir))
        findings.extend(_findings_for_session(data))
        flow_findings, flow_recs = analyze_lab_flows(child)
        findings.extend(flow_findings)
        for rec in flow_recs:
            if rec not in recommendations:
                recommendations.append(rec)

    recommendations.extend(_run_recommendations(findings, summary))
    if durations:
        findings.append(
            f"Czas sesji: min={min(durations):.1f}s, max={max(durations):.1f}s, "
            f"avg={statistics.mean(durations):.1f}s"
        )

    return RunAnalysis(
        run_id=run_id,
        generated_at=now_iso(),
        host=host_id(),
        sessions=sessions,
        summary=summary,
        findings=findings,
        recommendations=recommendations,
    )


def write_run_analysis(run_dir: Path, analysis: RunAnalysis | None = None) -> tuple[Path, Path]:
    run_dir = run_dir.resolve()
    analysis = analysis or analyze_run(run_dir)
    json_path = run_dir / "analysis.json"
    md_path = run_dir / "analysis.md"
    json_path.write_text(json.dumps(asdict(analysis), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_run_analysis_markdown(analysis), encoding="utf-8")
    return json_path, md_path
