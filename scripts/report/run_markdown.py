from __future__ import annotations

from .models import RunAnalysis


def render_run_analysis_markdown(analysis: RunAnalysis) -> str:
    lines = [
        f"# urisys test run analysis — `{analysis.run_id}`",
        "",
        f"- **Generated:** {analysis.generated_at}",
        f"- **Host:** {analysis.host}",
        f"- **Overall:** {'PASS' if analysis.all_passed else 'FAIL'}",
        "",
        "## Summary",
        "",
        "| Pass | Fail | Error | Total |",
        "|------|------|-------|-------|",
        f"| {analysis.summary.get('pass', 0)} | {analysis.summary.get('fail', 0)} | "
        f"{analysis.summary.get('error', 0)} | {analysis.summary.get('total', 0)} |",
        "",
        "## Sessions",
        "",
        "| Status | Session | Suite | Duration | Steps | Report |",
        "|--------|---------|-------|----------|-------|--------|",
    ]
    for s in analysis.sessions:
        steps_pass = s.get("steps_pass", 0)
        steps_fail = s.get("steps_fail", 0)
        lines.append(
            f"| {s['status']} | {s['session_name']} | {s['suite']} | {s.get('duration_s', 0):.1f}s | "
            f"{steps_pass}/{steps_pass + steps_fail} | `{s['report']}` |"
        )
    lines.append("")
    if analysis.findings:
        lines.extend(["## Findings", ""])
        lines.extend(f"- {f}" for f in analysis.findings)
        lines.append("")
    if analysis.recommendations:
        lines.extend(["## Recommendations", ""])
        lines.extend(f"- {r}" for r in analysis.recommendations)
        lines.append("")
    return "\n".join(lines) + "\n"
