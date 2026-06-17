"""Characterization tests for PackManager spec parsing.

Pins the all/none/empty/iterable edge cases so the dedup of the
string-or-iterable split into _split_specs stays behaviour-preserving.
"""

from __future__ import annotations

from urisys.defaults import DEFAULT_PACKAGES
from urisys.managers.pack_manager import PackManager as P

_DEFAULT = list(DEFAULT_PACKAGES)


def test_parse_packs_default_set():
    assert P.parse_packs(None) == _DEFAULT
    assert P.parse_packs("") == _DEFAULT
    assert P.parse_packs("all") == _DEFAULT
    assert P.parse_packs("a,all,b") == _DEFAULT  # any 'all' wins
    assert P.parse_packs(["all"]) == _DEFAULT


def test_parse_packs_explicit_and_none_filter():
    assert P.parse_packs("a,b") == ["a", "b"]
    assert P.parse_packs(["a", "b"]) == ["a", "b"]
    assert P.parse_packs("a,none,b") == ["a", "b"]  # 'none' filtered out
    assert P.parse_packs("none") == []
    assert P.parse_packs(["a", " ", "none"]) == ["a"]  # blanks dropped
    assert P.parse_packs([]) == []


def test_is_all():
    for truthy in (None, "", "all", "a,all", ["all"]):
        assert P._is_all(truthy) is True
    for falsy in ("a,b", "a,b,c", [], ["x"]):
        assert P._is_all(falsy) is False


def test_parse_markpacts():
    assert P.parse_markpacts(None) == []
    assert P.parse_markpacts("") == []
    assert P.parse_markpacts("a,b") == ["a", "b"]
    assert P.parse_markpacts(["a", " b "]) == ["a", "b"]
    assert P.parse_markpacts("a, ,b") == ["a", "b"]
