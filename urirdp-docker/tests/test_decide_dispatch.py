"""Characterization tests for urirdp_llm.handlers.decide dispatch (no network).

Pin the decision behaviour across every branch reachable without a live LLM
(guard / mock / heuristic / dry-run / missing-credentials / unknown-driver), so
the driver-table refactor cannot silently change retry-vs-abort decisions.
"""

from __future__ import annotations

import sys
from pathlib import Path

PKG = Path(__file__).resolve().parents[1] / "packages" / "python"
CANONICAL = Path(__file__).resolve().parents[2] / "packages" / "python"
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(CANONICAL))

import urirdp_llm.handlers as h  # noqa: E402


def _cfg(driver: str, **extra) -> dict:
    return {"config": {"llm": {"driver": driver, **extra}}}


def test_missing_question_errors():
    assert h.decide({}, {}) == {"ok": False, "error": "payload.question is required"}


def test_mock_retry_on_critical_pattern():
    out = h.decide({"question": "retry?", "context": {"log": "error 502"}}, _cfg("mock"))
    assert out["decision"] == "retry" and out["ok"] is True
    assert out["model"] == "mock-decide"


def test_mock_abort_on_clean_context():
    out = h.decide({"question": "retry?", "context": {"log": "all good"}}, _cfg("mock"))
    assert out["decision"] == "abort" and out["ok"] is False


def test_dry_run_forces_mock():
    ctx = {"dry_run": True, **_cfg("openai")}
    out = h.decide({"question": "q", "context": {"e": "502"}}, ctx)
    assert out["model"] == "mock-decide" and out["decision"] == "retry"


def test_real_driver_without_credentials_falls_back(monkeypatch):
    for key in ("OPENROUTER_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    ctx = {"allow_real": True, **_cfg("openai")}
    out = h.decide({"question": "q"}, ctx)
    assert out["model"] == "mock-decide"


def test_unknown_driver_falls_back_to_mock():
    ctx = {"allow_real": True, **_cfg("weird", model="m", api_key="k")}
    out = h.decide({"question": "q", "context": {"e": "error"}}, ctx)
    assert out["model"] == "mock-decide"
