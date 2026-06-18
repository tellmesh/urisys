from __future__ import annotations

import pytest

from urisys.doctor import run_doctor


def test_doctor_ok_in_dev_env():
    report = run_doctor(min_version="0.1.0")
    assert "checks" in report
    assert report["summary"]["fail"] == 0
    ids = {c["id"] for c in report["checks"]}
    assert "import_uri_control" in ids
    assert "dist_uricore" in ids
    assert "import_urisys" in ids
    assert report["ok"] is True


def test_doctor_fails_high_min_version():
    report = run_doctor(min_version="99.0.0")
    assert report["ok"] is False
    assert any(c["id"] == "urisys_min_version" and c["status"] == "fail" for c in report["checks"])


def test_doctor_hints_include_node_serve():
    report = run_doctor(min_version=None)
    joined = " ".join(report["hints"])
    assert "node serve" in joined
    assert "remote health" in joined
