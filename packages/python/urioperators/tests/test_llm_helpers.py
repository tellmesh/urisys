from __future__ import annotations

import json

import pytest

from urioperators.llm_decide import decision_from_parsed
from urioperators.llm_json import parse_json_response
from urioperators.llm_plan import plan_from_parsed


def test_parse_json_response_plain():
    assert parse_json_response('{"action":"click","x":1}') == {"action": "click", "x": 1}


def test_parse_json_response_embedded():
    text = 'Here is the result:\n{"uri":"him://local/mouse/command/scroll","payload":{"amount":-3}}\nThanks'
    out = parse_json_response(text)
    assert out["uri"] == "him://local/mouse/command/scroll"


def test_parse_json_response_empty():
    assert parse_json_response("") == {}


def test_plan_from_parsed_ok():
    out = plan_from_parsed({"uri": "him://x", "payload": {"a": 1}}, "gpt-4o-mini", "scroll")
    assert out["ok"] is True
    assert out["uri"] == "him://x"
    assert out["payload"] == {"a": 1}


def test_plan_from_parsed_missing_uri():
    with pytest.raises(ValueError, match="missing uri"):
        plan_from_parsed({}, "m", "t")


def test_decision_from_parsed_retry():
    out = decision_from_parsed({"ok": True, "decision": "retry", "reason": "502"}, "m", "q?")
    assert out["ok"] is True
    assert out["decision"] == "retry"


def test_decision_from_parsed_abort_default():
    out = decision_from_parsed({"ok": False}, "m", "q?")
    assert out["decision"] == "abort"
