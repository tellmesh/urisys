"""Backward-compatible re-export — see ``urisys.markpact.profile``."""

from ..markpact.profile import (
    LintIssue,
    _build_flow_profiles,
    _cross_check_schemes,
    _issue,
    _issue_message,
    _validate_scheme_requirements,
    declared_packs,
    declared_schemes,
    lint_markpact,
)

__all__ = [
    "LintIssue",
    "_build_flow_profiles",
    "_cross_check_schemes",
    "_issue",
    "_issue_message",
    "_validate_scheme_requirements",
    "declared_packs",
    "declared_schemes",
    "lint_markpact",
]
