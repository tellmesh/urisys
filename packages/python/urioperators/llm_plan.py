from __future__ import annotations

from typing import Any


def plan_from_parsed(parsed: dict[str, Any], model: str, transcript: str) -> dict[str, Any]:
    uri = str(parsed.get("uri") or "").strip()
    inner_payload = parsed.get("payload") if isinstance(parsed.get("payload"), dict) else {}
    if not uri:
        raise ValueError("missing uri in LLM plan response")
    return {
        "ok": True,
        "uri": uri,
        "payload": inner_payload,
        "transcript": transcript,
        "model": model,
    }
