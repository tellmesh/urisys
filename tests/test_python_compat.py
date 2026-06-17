"""Python version compatibility checks (doctor + imports)."""

from __future__ import annotations

import sys

import pytest

from urisys.doctor import _check_python, run_doctor


class _FakeVersionInfo:
    """Minimal sys.version_info stand-in for tests."""

    def __init__(self, major: int, minor: int, micro: int = 0) -> None:
        self.major = major
        self.minor = minor
        self.micro = micro

    def __getitem__(self, index: int) -> int:
        return (self.major, self.minor, self.micro)[index]

    def __ge__(self, other: tuple[int, int]) -> bool:
        return (self.major, self.minor) >= other

    def __lt__(self, other: tuple[int, int]) -> bool:
        return (self.major, self.minor) < other


@pytest.mark.parametrize(
    "major,minor,expected",
    [
        (3, 9, "fail"),
        (3, 10, "ok"),
        (3, 11, "ok"),
        (3, 12, "ok"),
        (3, 13, "ok"),
        (3, 14, "warn"),
    ],
)
def test_python_version_gate(monkeypatch, major, minor, expected):
    monkeypatch.setattr(sys, "version_info", _FakeVersionInfo(major, minor))
    monkeypatch.setattr(sys, "executable", f"/usr/bin/python{major}.{minor}")
    check = _check_python()
    assert check.status == expected


def test_current_python_supported():
    report = run_doctor(min_version="0.1.0")
    py_check = next(c for c in report["checks"] if c["id"] == "python_version")
    assert py_check["status"] in ("ok", "warn")
    assert report["summary"]["fail"] == 0 or py_check["status"] == "fail"
