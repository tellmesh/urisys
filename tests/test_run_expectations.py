"""Unit tests for lab-10 expect: contract evaluation."""

from __future__ import annotations

from urisys_lab.sessions import evaluate_expectations


def test_screen_changed_uses_baseline_not_previous_flow():
    failures = evaluate_expectations(
        {"screen_changed": True},
        screenshot_md5="bbbb",
        baseline_md5="aaaa",
        duplicate_of="02-other-flow",
        step_results=[],
    )
    assert failures == []


def test_screen_changed_fails_when_equal_baseline():
    failures = evaluate_expectations(
        {"screen_changed": True},
        screenshot_md5="aaaa",
        baseline_md5="aaaa",
        duplicate_of="00-baseline",
        step_results=[],
    )
    assert len(failures) == 1
    assert "screen_changed" in failures[0]


def test_ocr_contains_from_pipeline():
    steps = [
        {
            "response": {
                "result": {
                    "pipeline": {
                        "ocr": {
                            "result": {"text": "TellMesh Demo Fill the form Name"},
                        }
                    }
                }
            }
        }
    ]
    failures = evaluate_expectations(
        {"ocr_contains": ["Name", "TellMesh"]},
        step_results=steps,
    )
    assert failures == []
