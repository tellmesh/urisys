from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .util import read_json


def summarize_event_records(
    records: list[dict[str, Any]], *, since_ms: int
) -> tuple[int, dict[str, int], list[dict[str, str]]]:
    kinds: dict[str, int] = {}
    failures: list[dict[str, str]] = []
    count = 0
    for ev in records:
        if not isinstance(ev, dict):
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
    return count, kinds, failures[:20]


def load_event_records(events_path: Path) -> list[dict[str, Any]]:
    raw = events_path.read_text(encoding="utf-8")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        records: list[dict[str, Any]] = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(ev, dict):
                records.append(ev)
        return records
    if isinstance(parsed, dict) and isinstance(parsed.get("events"), list):
        return [ev for ev in parsed["events"] if isinstance(ev, dict)]
    if isinstance(parsed, list):
        return [ev for ev in parsed if isinstance(ev, dict)]
    if isinstance(parsed, dict):
        return [parsed]
    return []


def summarize_events(events_path: Path, *, since_iso: str | None = None) -> dict[str, Any]:
    if not events_path.is_file():
        return {"count": 0, "kinds": {}, "failures": [], "source": str(events_path)}

    records = load_event_records(events_path)
    since_ms = 0
    if since_iso:
        try:
            since_ms = int(datetime.fromisoformat(since_iso.replace("Z", "+00:00")).timestamp() * 1000)
        except ValueError:
            since_ms = 0

    count, kinds, failures = summarize_event_records(records, since_ms=since_ms)
    stale_log = False
    if count == 0 and since_ms and records:
        count, kinds, failures = summarize_event_records(records, since_ms=0)
        stale_log = count > 0

    out: dict[str, Any] = {
        "count": count,
        "kinds": kinds,
        "failures": failures,
        "source": str(events_path.name),
    }
    if stale_log:
        out["stale_log"] = True
        out["note"] = "event timestamps predate session started_at; showing full file"
    return out


def resolve_events_paths(session_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for name in ("events.jsonl", "events-urirdp.jsonl", "events-lab.jsonl"):
        path = session_dir / name
        if path.is_file():
            paths.append(path)
    data_events = session_dir / "data" / "events.jsonl"
    if data_events.is_file() and data_events not in paths:
        paths.append(data_events)
    if not paths:
        api_events = session_dir / "responses" / "events.json"
        if api_events.is_file():
            paths.append(api_events)
    return paths


def merge_event_summaries(paths: list[Path], *, since_iso: str | None) -> dict[str, Any]:
    if not paths:
        return {"count": 0, "kinds": {}, "failures": [], "sources": []}
    merged_kinds: dict[str, int] = {}
    merged_failures: list[dict[str, str]] = []
    total = 0
    sources: list[str] = []
    stale = False
    notes: list[str] = []
    for path in paths:
        part = summarize_events(path, since_iso=since_iso)
        total += int(part.get("count") or 0)
        sources.append(str(path.name))
        for kind, n in (part.get("kinds") or {}).items():
            merged_kinds[kind] = merged_kinds.get(kind, 0) + int(n)
        merged_failures.extend(part.get("failures") or [])
        if part.get("stale_log"):
            stale = True
            if note := part.get("note"):
                notes.append(note)
    out: dict[str, Any] = {
        "count": total,
        "kinds": merged_kinds,
        "failures": merged_failures[:20],
        "sources": sources,
    }
    if stale:
        out["stale_log"] = True
        out["note"] = "; ".join(dict.fromkeys(notes))
    return out
