from __future__ import annotations

from typing import Any

from ..profile import (
    LintIssue,
    _build_flow_profiles,
    _cross_check_schemes,
    _validate_scheme_requirements,
)
from .context import MarkpactLintContext
from .rules import MARKPACT_RULES


def _issue_message(issue: LintIssue) -> str:
    return f"{issue.code}: {issue.message}"


def run_lint(
    *,
    pack: dict[str, Any],
    scheme: str,
    capabilities: list[dict[str, Any]],
    flows: list[dict[str, Any]],
    undeclared_schemes: list[str],
) -> dict[str, Any]:
    errors, warnings, schemes_required, packs_default = _validate_scheme_requirements(pack, scheme)
    ctx = MarkpactLintContext(
        pack=pack,
        scheme=scheme,
        capabilities=capabilities,
        flows=flows,
        undeclared_schemes=undeclared_schemes,
        schemes_required=schemes_required,
        packs_default=packs_default,
    )

    issues: list[LintIssue] = []
    for rule in MARKPACT_RULES:
        issues.extend(rule.check(ctx))

    for issue in issues:
        msg = _issue_message(issue)
        if issue.severity == "error":
            errors.append(msg)
        else:
            warnings.append(msg)

    flow_profiles = _build_flow_profiles(flows, scheme, warnings, issues)
    warnings = _cross_check_schemes(flows, schemes_required, scheme, warnings)

    requires_caps = (pack.get("requires") or {}).get("capabilities") if isinstance(pack.get("requires"), dict) else None

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "issues": [
            {"code": i.code, "severity": i.severity, "message": i.message, "location": i.location}
            for i in issues
        ],
        "requires": {"schemes": sorted(schemes_required), "capabilities": requires_caps or []},
        "uses_packs": packs_default,
        "flow_profiles": flow_profiles,
        "profile": "markpact-v1alpha",
    }
