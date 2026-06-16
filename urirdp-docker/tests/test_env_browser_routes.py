"""Route registration tests for env:// and browser:// packs."""

from __future__ import annotations

import json

from urirdpedge.cli import build_runtime


class _Args:
    packs = "env,browser"
    config = None
    events = "data/events.jsonl"


def test_env_and_browser_routes_registered():
    rt = build_runtime(_Args())
    patterns = {r.pattern for r in rt.routes}
    assert "env://runtime/query/health" in patterns
    assert "browser://{session}/page/open" in patterns
    assert "browser://{session}/page/command/open" in patterns


def test_env_health_call():
    rt = build_runtime(_Args())
    res = rt.call("env://runtime/query/health", {}, {"approved": True})
    assert res["ok"] is True
    assert res["result"]["scheme"] == "env"


def test_browser_lab_alias_open_and_dom():
    rt = build_runtime(_Args())
    rt.config = {"browser": {"driver": "mock", "headless": True}}
    open_res = rt.call(
        "browser://chrome/page/open",
        {"url": "http://example.com"},
        {"approved": True, "allow_real": True, "dry_run": False},
    )
    assert open_res["ok"] is True
    dom_res = rt.call("browser://chrome/page/active/dom", {}, {"approved": True})
    assert dom_res["ok"] is True
    assert "html" in dom_res["result"]
    shot_res = rt.call(
        "browser://chrome/page/active/screenshot",
        {},
        {"approved": True, "allow_real": True, "dry_run": False},
    )
    assert shot_res["ok"] is True
    assert shot_res["result"].get("base64")
