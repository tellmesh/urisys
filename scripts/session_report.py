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
"""

from __future__ import annotations

import argparse
import json
import platform
import socket
import statistics
import textwrap
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class StepResult:
    name: str
    status: str  # pass | fail | skip
    uri: str | None = None
    duration_s: float | None = None
    response_file: str | None = None
    screenshot: str | None = None
    detail: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionReport:
    session_id: str
    session_name: str
    suite: str
    started_at: str
    finished_at: str
    duration_s: float
    status: str  # pass | fail | error
    host: str
    steps: list[StepResult] = field(default_factory=list)
    artifacts: dict[str, list[str]] = field(default_factory=dict)
    events_summary: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)
    log_tail: str = ""

    @property
    def passed(self) -> int:
        return sum(1 for s in self.steps if s.status == "pass")

    @property
    def failed(self) -> int:
        return sum(1 for s in self.steps if s.status == "fail")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _host_id() -> str:
    return f"{socket.gethostname()} ({platform.system()} {platform.machine()})"


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _tail(text: str, limit: int = 4000) -> str:
    return text[-limit:] if text else ""


def _summarize_events(events_path: Path, *, since_iso: str | None = None) -> dict[str, Any]:
    if not events_path.is_file():
        return {"count": 0, "kinds": {}, "failures": []}
    since_ms = 0
    if since_iso:
        try:
            since_ms = int(
                datetime.fromisoformat(since_iso.replace("Z", "+00:00")).timestamp() * 1000
            )
        except ValueError:
            since_ms = 0
    kinds: dict[str, int] = {}
    failures: list[dict[str, str]] = []
    count = 0
    for line in events_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = int(ev.get("occurred_at_unix_ms") or 0)
        if since_ms and ts and ts < since_ms:
            continue
        count += 1
        et = str(ev.get("event_type") or ev.get("operation") or "unknown")
        kinds[et] = kinds.get(et, 0) + 1
        if ".failed" in et or ev.get("error"):
            failures.append(
                {
                    "event_type": et,
                    "operation": str(ev.get("operation") or ""),
                    "error": str(ev.get("error") or ev.get("result", {}).get("error") or "")[:200],
                }
            )
    return {"count": count, "kinds": kinds, "failures": failures[:20]}


def _infer_steps(session_dir: Path, meta: dict[str, Any]) -> list[StepResult]:
    if steps := meta.get("steps"):
        return [StepResult(**s) if isinstance(s, dict) else s for s in steps]

    steps: list[StepResult] = []
    responses_dir = session_dir / "responses"
    if responses_dir.is_dir():
        for path in sorted(responses_dir.glob("*.json")):
            data = _read_json(path) or {}
            ok = bool(data.get("ok"))
            uri = data.get("uri")
            result = data.get("result") or {}
            metrics: dict[str, Any] = {}
            if isinstance(result, dict):
                for key in ("driver", "engine", "clicked", "captured", "size_bytes", "model"):
                    if key in result:
                        metrics[key] = result[key]
                if pipeline := result.get("pipeline"):
                    metrics["pipeline_ok"] = all(
                        (v or {}).get("ok") for v in pipeline.values() if isinstance(v, dict)
                    )
            steps.append(
                StepResult(
                    name=path.stem,
                    status="pass" if ok else "fail",
                    uri=str(uri) if uri else None,
                    response_file=str(path.relative_to(session_dir)),
                    detail="" if ok else str(data.get("error") or result.get("error") or "not ok")[:300],
                    metrics=metrics,
                )
            )
    return steps


def _collect_artifacts(session_dir: Path) -> dict[str, list[str]]:
    artifacts: dict[str, list[str]] = {}
    for sub, label in (
        ("screenshots", "screenshots"),
        ("responses", "responses"),
    ):
        d = session_dir / sub
        if d.is_dir():
            artifacts[label] = sorted(str(p.relative_to(session_dir)) for p in d.iterdir() if p.is_file())
    for name in ("session.log", "docker-logs.txt", "events.jsonl", "meta.json"):
        p = session_dir / name
        if p.is_file():
            artifacts.setdefault("logs", []).append(name)
    return artifacts


def _session_status(steps: list[StepResult], meta: dict[str, Any]) -> str:
    if status := meta.get("status"):
        return str(status)
    if any(s.status == "fail" for s in steps):
        return "fail"
    if steps and all(s.status == "pass" for s in steps):
        return "pass"
    log = (meta.get("exit_code"),)
    if meta.get("exit_code") not in (None, 0):
        return "fail"
    return "pass" if steps else "error"


def generate_report(session_dir: Path) -> SessionReport:
    session_dir = session_dir.resolve()
    meta = _read_json(session_dir / "meta.json") or {}
    log_path = session_dir / "session.log"
    log_tail = _tail(log_path.read_text(encoding="utf-8", errors="replace")) if log_path.is_file() else ""

    steps = _infer_steps(session_dir, meta)
    events_path = session_dir / "events.jsonl"
    if not events_path.is_file() and (session_dir / "data" / "events.jsonl").is_file():
        events_path = session_dir / "data" / "events.jsonl"

    started = str(meta.get("started_at") or _now_iso())
    finished = str(meta.get("finished_at") or _now_iso())
    try:
        t0 = datetime.fromisoformat(started.replace("Z", "+00:00"))
        t1 = datetime.fromisoformat(finished.replace("Z", "+00:00"))
        duration = max(0.0, (t1 - t0).total_seconds())
    except ValueError:
        duration = float(meta.get("duration_s") or 0.0)

    return SessionReport(
        session_id=str(meta.get("session_id") or session_dir.name),
        session_name=str(meta.get("session_name") or session_dir.name),
        suite=str(meta.get("suite") or session_dir.name),
        started_at=started,
        finished_at=finished,
        duration_s=duration,
        status=_session_status(steps, meta),
        host=str(meta.get("host") or _host_id()),
        steps=steps,
        artifacts=_collect_artifacts(session_dir),
        events_summary=_summarize_events(events_path, since_iso=started),
        meta=meta,
        log_tail=log_tail,
    )


def write_session_report(session_dir: Path, report: SessionReport | None = None) -> tuple[Path, Path]:
    session_dir = session_dir.resolve()
    report = report or generate_report(session_dir)
    json_path = session_dir / "report.json"
    md_path = session_dir / "report.md"

    payload = asdict(report)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

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

    if report.meta.get("display") or report.meta.get("ports"):
        lines.extend(["## Environment", ""])
        if d := report.meta.get("display"):
            lines.append(f"- Display: `{d}`")
        if ports := report.meta.get("ports"):
            lines.append(f"- Ports: `{ports}`")
        lines.append("")

    if report.steps:
        lines.extend(["## Steps", "", "| Status | Step | URI | Metrics | Detail |", "|--------|------|-----|---------|--------|"])
        for s in report.steps:
            metrics = ", ".join(f"{k}={v}" for k, v in s.metrics.items()) if s.metrics else ""
            uri = f"`{s.uri}`" if s.uri else ""
            detail = (s.detail or "")[:80]
            lines.append(f"| {s.status} | {s.name} | {uri} | {metrics} | {detail} |")
        lines.append("")

    if report.artifacts.get("screenshots"):
        lines.extend(["## Screenshots", ""])
        for shot in report.artifacts["screenshots"]:
            lines.append(f"- `{shot}`")
        lines.append("")

    es = report.events_summary
    if es.get("count"):
        lines.extend(
            [
                "## Events (JSONL)",
                "",
                f"- Total events: **{es['count']}**",
                f"- Failures logged: **{len(es.get('failures') or [])}**",
                "",
            ]
        )
        if kinds := es.get("kinds"):
            top = sorted(kinds.items(), key=lambda x: -x[1])[:8]
            lines.append("Top event types:")
            for k, n in top:
                lines.append(f"- `{k}`: {n}")
            lines.append("")

    if report.meta.get("log_errors"):
        le = report.meta["log_errors"]
        lines.extend(
            [
                "## HTTP / process log errors",
                "",
                f"- HTTP 502 (lab forward fail): **{le.get('http_502', 0)}**",
                f"- HTTP 400 (urirdp reject): **{le.get('http_400', 0)}**",
                "",
            ]
        )
        for entry in le.get("lines") or []:
            lines.append(f"- `{entry}`")
        lines.append("")

    if hashes := report.meta.get("screenshot_hashes"):
        dups = []
        for step in report.steps:
            if dup := (step.metrics or {}).get("duplicate_of"):
                dups.append(f"{step.name} duplicate of {dup}")
        if dups:
            lines.extend(["## Duplicate screenshots", ""])
            for d in dups:
                lines.append(f"- {d}")
            lines.append("")

    if report.log_tail:
        lines.extend(["## Log tail", "", "```", report.log_tail.rstrip(), "```", ""])

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


@dataclass
class RunAnalysis:
    run_id: str
    generated_at: str
    host: str
    sessions: list[dict[str, Any]] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)
    findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return self.summary.get("fail", 0) == 0 and self.summary.get("error", 0) == 0


def analyze_run(run_dir: Path) -> RunAnalysis:
    run_dir = run_dir.resolve()
    manifest = _read_json(run_dir / "manifest.json") or {}
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
            json_path, _ = write_session_report(child)
            report_path = json_path
        data = _read_json(report_path) or {}
        status = str(data.get("status") or "error")
        summary["total"] += 1
        summary[status] = summary.get(status, 0) + 1
        durations.append(float(data.get("duration_s") or 0))
        sessions.append(
            {
                "session_name": data.get("session_name"),
                "suite": data.get("suite"),
                "status": status,
                "duration_s": data.get("duration_s"),
                "steps_pass": data.get("passed") if "passed" in data else sum(
                    1 for s in data.get("steps", []) if s.get("status") == "pass"
                ),
                "steps_fail": data.get("failed") if "failed" in data else sum(
                    1 for s in data.get("steps", []) if s.get("status") == "fail"
                ),
                "report": str(report_path.relative_to(run_dir)),
            }
        )

        if status != "pass":
            findings.append(f"Session `{data.get('session_name')}` ({data.get('suite')}) **FAILED**.")
            log_tail = data.get("log_tail") or ""
            for needle in ("Can't open X display", "port is already allocated", "parse error", "assert"):
                if needle.lower() in log_tail.lower():
                    findings.append(f"  - log hint: `{needle}` in {data.get('session_name')}")

        for step in data.get("steps") or []:
            if step.get("status") == "fail":
                findings.append(
                    f"  - step `{step.get('name')}` failed: {(step.get('detail') or '')[:120]}"
                )

        ev = data.get("events_summary") or {}
        for fail in ev.get("failures") or []:
            findings.append(
                f"  - event failure in `{data.get('session_name')}`: {fail.get('event_type')} — {fail.get('error')[:100]}"
            )

    if any("Can't open X display" in f for f in findings):
        recommendations.append(
            "Uruchamiaj `bootstrap-rdp-session.sh` przed realnymi testami GUI lub dodaj auto-bootstrap do compose healthcheck."
        )
    if any("port is already allocated" in f for f in findings):
        recommendations.append(
            "Zatrzymaj stack labu (`docker-down.sh`) przed testami urirdp na portach 3389/8795."
        )
    if summary.get("fail", 0) == 0 and summary.get("pass", 0) > 0:
        recommendations.append("Wszystkie sesje przeszły — rozważ dodanie tych testów do CI jako nightly job z archiwizacją raportów.")

    if durations:
        findings.append(
            f"Czas sesji: min={min(durations):.1f}s, max={max(durations):.1f}s, "
            f"avg={statistics.mean(durations):.1f}s"
        )

    return RunAnalysis(
        run_id=run_id,
        generated_at=_now_iso(),
        host=_host_id(),
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

    lines = [
        f"# urisys test run analysis — `{analysis.run_id}`",
        "",
        f"- **Generated:** {analysis.generated_at}",
        f"- **Host:** {analysis.host}",
        f"- **Overall:** {'PASS' if analysis.all_passed else 'FAIL'}",
        "",
        "## Summary",
        "",
        f"| Pass | Fail | Error | Total |",
        f"|------|------|-------|-------|",
        f"| {analysis.summary.get('pass', 0)} | {analysis.summary.get('fail', 0)} | {analysis.summary.get('error', 0)} | {analysis.summary.get('total', 0)} |",
        "",
        "## Sessions",
        "",
        "| Status | Session | Suite | Duration | Steps | Report |",
        "|--------|---------|-------|----------|-------|--------|",
    ]
    for s in analysis.sessions:
        lines.append(
            f"| {s['status']} | {s['session_name']} | {s['suite']} | {s.get('duration_s', 0):.1f}s | "
            f"{s.get('steps_pass', 0)}/{s.get('steps_pass', 0) + s.get('steps_fail', 0)} | `{s['report']}` |"
        )
    lines.append("")

    if analysis.findings:
        lines.extend(["## Findings", ""])
        for f in analysis.findings:
            lines.append(f"- {f}")
        lines.append("")

    if analysis.recommendations:
        lines.extend(["## Recommendations", ""])
        for r in analysis.recommendations:
            lines.append(f"- {r}")
        lines.append("")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="urisys session report generator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    gen = sub.add_parser("generate", help="Generate report for one session directory")
    gen.add_argument("session_dir", type=Path)

    ana = sub.add_parser("analyze", help="Analyze all sessions in a run directory")
    ana.add_argument("run_dir", type=Path)
    ana.add_argument("--write-md", action="store_true")

    args = parser.parse_args()

    if args.cmd == "generate":
        report = generate_report(args.session_dir)
        json_path, md_path = write_session_report(args.session_dir, report)
        print(f"report: {json_path}")
        print(f"markdown: {md_path}")
        print(f"status: {report.status.upper()} steps={report.passed}/{len(report.steps)}")
        return 0 if report.status == "pass" else 1

    analysis = analyze_run(args.run_dir)
    json_path, md_path = write_run_analysis(args.run_dir, analysis)
    print(f"analysis: {json_path}")
    print(f"markdown: {md_path}")
    print(
        f"SUMMARY pass={analysis.summary.get('pass', 0)} "
        f"fail={analysis.summary.get('fail', 0)} "
        f"error={analysis.summary.get('error', 0)}"
    )
    return 0 if analysis.all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
