from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from .events import merge_event_summaries, resolve_events_paths
from .models import SessionReport, StepResult
from .util import host_id, now_iso, read_json, tail


def _extract_metrics(result: dict[str, Any]) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    for key in ("driver", "engine", "clicked", "captured", "size_bytes", "model"):
        if key in result:
            metrics[key] = result[key]
    if pipeline := result.get("pipeline"):
        metrics["pipeline_ok"] = all(
            (v or {}).get("ok") for v in pipeline.values() if isinstance(v, dict)
        )
    return metrics


def _resolve_screenshot(data: dict[str, Any], result: dict[str, Any]) -> str | None:
    shots = data.get("screenshots")
    if isinstance(shots, list) and shots:
        return str(shots[0])
    if isinstance(result, dict) and result.get("screenshot_file"):
        return str(result["screenshot_file"])
    return None


def _response_to_step_result(path: Path, session_dir: Path) -> StepResult:
    data = read_json(path) or {}
    ok = bool(data.get("ok"))
    uri = data.get("uri")
    resp = data.get("response") if isinstance(data.get("response"), dict) else {}
    result = data.get("result") or resp.get("result") or {}
    metrics = _extract_metrics(result) if isinstance(result, dict) else {}
    screenshot = _resolve_screenshot(data, result)
    return StepResult(
        name=path.stem,
        status="pass" if ok else "fail",
        uri=str(uri) if uri else None,
        response_file=str(path.relative_to(session_dir)),
        screenshot=screenshot,
        detail="" if ok else str(data.get("error") or resp.get("error") or result.get("error") or "not ok")[:300],
        metrics=metrics,
    )


def infer_steps(session_dir: Path, meta: dict[str, Any]) -> list[StepResult]:
    if steps := meta.get("steps"):
        return [StepResult(**s) if isinstance(s, dict) else s for s in steps]

    responses_dir = session_dir / "responses"
    if not responses_dir.is_dir():
        return []
    return [
        _response_to_step_result(path, session_dir)
        for path in sorted(responses_dir.glob("*.json"))
        if not path.name.startswith("_")
    ]


def collect_artifacts(session_dir: Path) -> dict[str, list[str]]:
    artifacts: dict[str, list[str]] = {}
    for sub, label in (("screenshots", "screenshots"), ("responses", "responses")):
        d = session_dir / sub
        if d.is_dir():
            artifacts[label] = sorted(str(p.relative_to(session_dir)) for p in d.iterdir() if p.is_file())
    for name in ("session.log", "docker-logs.txt", "events.jsonl", "meta.json"):
        p = session_dir / name
        if p.is_file():
            artifacts.setdefault("logs", []).append(name)
    return artifacts


def session_status(steps: list[StepResult], meta: dict[str, Any]) -> str:
    if status := meta.get("status"):
        return str(status)
    if any(s.status == "fail" for s in steps):
        return "fail"
    if steps and all(s.status == "pass" for s in steps):
        return "pass"
    if meta.get("exit_code") not in (None, 0):
        return "fail"
    return "pass" if steps else "error"


def session_duration(meta: dict[str, Any]) -> float:
    started = str(meta.get("started_at") or now_iso())
    finished = str(meta.get("finished_at") or now_iso())
    try:
        t0 = datetime.fromisoformat(started.replace("Z", "+00:00"))
        t1 = datetime.fromisoformat(finished.replace("Z", "+00:00"))
        return max(0.0, (t1 - t0).total_seconds())
    except ValueError:
        return float(meta.get("duration_s") or 0.0)


def generate_report(session_dir: Path) -> SessionReport:
    session_dir = session_dir.resolve()
    meta = read_json(session_dir / "meta.json") or {}
    log_path = session_dir / "session.log"
    log_tail = tail(log_path.read_text(encoding="utf-8", errors="replace")) if log_path.is_file() else ""
    steps = infer_steps(session_dir, meta)
    started = str(meta.get("started_at") or now_iso())
    finished = str(meta.get("finished_at") or now_iso())
    return SessionReport(
        session_id=str(meta.get("session_id") or session_dir.name),
        session_name=str(meta.get("session_name") or session_dir.name),
        suite=str(meta.get("suite") or session_dir.name),
        started_at=started,
        finished_at=finished,
        duration_s=session_duration(meta),
        status=session_status(steps, meta),
        host=str(meta.get("host") or host_id()),
        steps=steps,
        artifacts=collect_artifacts(session_dir),
        events_summary=merge_event_summaries(resolve_events_paths(session_dir), since_iso=started),
        meta=meta,
        log_tail=log_tail,
    )
