from __future__ import annotations

from typing import Any


def decision_from_parsed(parsed: dict[str, Any], model: str, question: str) -> dict[str, Any]:
    decision = str(parsed.get("decision") or ("retry" if parsed.get("ok") else "abort")).lower()
    ok = bool(parsed.get("ok")) if "ok" in parsed else decision == "retry"
    return {
        "ok": ok,
        "decision": decision,
        "reason": str(parsed.get("reason") or "llm-decide"),
        "confidence": float(parsed.get("confidence", 0.7)),
        "model": model,
        "question": question,
    }
