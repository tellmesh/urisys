from __future__ import annotations

from typing import Any

from .common import mock_result, var


def chat_complete(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    provider = var(context, "provider", "mock")
    messages = payload.get("messages") or []
    prompt = payload.get("prompt") or (messages[-1].get("content") if messages and isinstance(messages[-1], dict) else "")
    return mock_result(
        "llm.chat_complete",
        context,
        provider=provider,
        model=payload.get("model", "mock-model"),
        text=f"Mock completion for: {prompt}",
    )


def embedding_create(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    text = str(payload.get("text") or "")
    vector = [float((ord(ch) % 10) / 10) for ch in text[:8]] or [0.0]
    return mock_result("llm.embedding_create", context, provider=var(context, "provider", "mock"), vector=vector, dimensions=len(vector))


def model_list(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return mock_result("llm.model_list", context, provider=var(context, "provider", "mock"), models=["mock-model", "mock-embedding"])
