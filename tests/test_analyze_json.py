"""Stable ``analyze --json`` CI contract (MP + RR issue codes)."""

from __future__ import annotations

from pathlib import Path

import pytest

from urisys.markpact.analyzer import ANALYZE_JSON_FORMAT, analyze_json_report, analyze_markpact, collect_analyze_issues

TELLMESH = Path(__file__).resolve().parents[2]
PACKS = TELLMESH / "markpact-contracts" / "packs"


def test_analyze_json_format_constant():
    assert ANALYZE_JSON_FORMAT == "urisys.markpact.analyze-v1"


def test_collect_analyze_issues_merges_mp_and_rr():
    result = {
        "profile": {
            "issues": [
                {"code": "MP007", "severity": "warning", "message": "no expect", "location": "flow:a"},
            ]
        },
        "resolver": {
            "ok": False,
            "issues": [
                {
                    "code": "RR010",
                    "severity": "error",
                    "message": "mqtt broker missing",
                    "path": "targets.x.options",
                    "platform": "linux",
                }
            ],
        },
    }
    issues = collect_analyze_issues(result)
    assert len(issues) == 2
    assert {i["source"] for i in issues} == {"markpact", "resolver"}
    assert issues[1]["location"] == "linux:targets.x.options"


@pytest.mark.parametrize(
    "markpact_name",
    ("machine-cycle-process.markpact.md", "uristepper.markpact.md"),
)
def test_analyze_json_report_shape(markpact_name: str):
    path = PACKS / markpact_name
    if not path.is_file():
        pytest.skip(f"missing contract: {path}")
    report = analyze_json_report(analyze_markpact(path))
    assert report["format"] == ANALYZE_JSON_FORMAT
    assert isinstance(report["issues"], list)
    assert report["issue_codes"] == sorted({i["code"] for i in report["issues"]})
    assert report["error_count"] == sum(1 for i in report["issues"] if i["severity"] == "error")
    assert report["warning_count"] == sum(1 for i in report["issues"] if i["severity"] == "warning")
    if report["scheme"] == "process":
        assert "resolver_ok" in report
    else:
        assert "resolver_ok" not in report
