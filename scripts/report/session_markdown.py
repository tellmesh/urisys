from __future__ import annotations

from .models import SessionReport


def render_session_markdown(report: SessionReport) -> str:
    lines = [
        f"# Session report: {report.session_name}",
        "",
        f"- **Suite:** `{report.suite}`",
        f"- **Status:** **{report.status.upper()}**",
        f"- **Host:** {report.host}",
        f"- **Started:** {report.started_at}",
        f"- **Finished:** {report.finished_at}",
        f"- **Duration:** {report.duration_s:.1f}s",
        f"- **Steps:** PASS={report.passed} FAIL={report.failed}",
        "",
    ]
    lines.extend(_environment_section(report))
    lines.extend(_steps_section(report))
    lines.extend(_screenshots_section(report))
    lines.extend(_events_section(report))
    lines.extend(_log_errors_section(report))
    lines.extend(_duplicate_screenshots_section(report))
    lines.extend(_log_tail_section(report))
    return "\n".join(lines) + "\n"


def _environment_section(report: SessionReport) -> list[str]:
    if not (report.meta.get("display") or report.meta.get("ports")):
        return []
    lines = ["## Environment", ""]
    if d := report.meta.get("display"):
        lines.append(f"- Display: `{d}`")
    if ports := report.meta.get("ports"):
        lines.append(f"- Ports: `{ports}`")
    lines.append("")
    return lines


def _steps_section(report: SessionReport) -> list[str]:
    if not report.steps:
        return []
    lines = ["## Steps", "", "| Status | Step | URI | Metrics | Detail |", "|--------|------|-----|---------|--------|"]
    for s in report.steps:
        metrics = ", ".join(f"{k}={v}" for k, v in s.metrics.items()) if s.metrics else ""
        uri = f"`{s.uri}`" if s.uri else ""
        detail = (s.detail or "")[:80]
        lines.append(f"| {s.status} | {s.name} | {uri} | {metrics} | {detail} |")
    lines.append("")
    return lines


def _screenshots_section(report: SessionReport) -> list[str]:
    if not report.artifacts.get("screenshots"):
        return []
    lines = ["## Screenshots", ""]
    for shot in report.artifacts["screenshots"]:
        lines.append(f"- `{shot}`")
    lines.append("")
    return lines


def _events_section(report: SessionReport) -> list[str]:
    es = report.events_summary
    if not es.get("count"):
        return []
    lines = [
        "## Events (JSONL)",
        "",
        f"- Total events: **{es['count']}**",
        f"- Failures logged: **{len(es.get('failures') or [])}**",
        "",
    ]
    if kinds := es.get("kinds"):
        top = sorted(kinds.items(), key=lambda x: -x[1])[:8]
        lines.append("Top event types:")
        for k, n in top:
            lines.append(f"- `{k}`: {n}")
        lines.append("")
    return lines


def _log_errors_section(report: SessionReport) -> list[str]:
    if not report.meta.get("log_errors"):
        return []
    le = report.meta["log_errors"]
    lines = [
        "## HTTP / process log errors",
        "",
        f"- HTTP 502 (lab forward fail): **{le.get('http_502', 0)}**",
        f"- HTTP 400 (urirdp reject): **{le.get('http_400', 0)}**",
        "",
    ]
    for entry in le.get("lines") or []:
        lines.append(f"- `{entry}`")
    lines.append("")
    return lines


def _duplicate_screenshots_section(report: SessionReport) -> list[str]:
    if not report.meta.get("screenshot_hashes"):
        return []
    dups = [
        f"{step.name} duplicate of {dup}"
        for step in report.steps
        if (dup := (step.metrics or {}).get("duplicate_of"))
    ]
    if not dups:
        return []
    lines = ["## Duplicate screenshots", ""]
    lines.extend(f"- {d}" for d in dups)
    lines.append("")
    return lines


def _log_tail_section(report: SessionReport) -> list[str]:
    if not report.log_tail:
        return []
    return ["## Log tail", "", "```", report.log_tail.rstrip(), "```", ""]
