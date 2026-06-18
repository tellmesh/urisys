"""Stable CI JSON contract for ``urisys markpact analyze --json``."""

from __future__ import annotations

from typing import Any

ANALYZE_JSON_FORMAT = "urisys.markpact.analyze-v1"


def _normalize_markpact_issue(issue: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": "markpact",
        "code": str(issue["code"]),
        "severity": issue["severity"],
        "message": issue["message"],
        "location": issue.get("location"),
    }


def _normalize_resolver_issue(issue: dict[str, Any]) -> dict[str, Any]:
    platform = issue.get("platform")
    path = issue.get("path")
    location: str | None
    if platform and path:
        location = f"{platform}:{path}"
    elif platform:
        location = str(platform)
    else:
        location = str(path) if path else None
    return {
        "source": "resolver",
        "code": str(issue["code"]),
        "severity": issue["severity"],
        "message": issue["message"],
        "location": location,
        "platform": platform,
    }


def collect_analyze_issues(result: dict[str, Any]) -> list[dict[str, Any]]:
    """Merge MP (profile) and RR (resolver stub) issues into one list."""
    issues: list[dict[str, Any]] = []
    profile = result.get("profile") or {}
    for raw in profile.get("issues") or []:
        if isinstance(raw, dict):
            issues.append(_normalize_markpact_issue(raw))

    resolver = result.get("resolver")
    if isinstance(resolver, dict) and not resolver.get("skipped"):
        for raw in resolver.get("issues") or []:
            if isinstance(raw, dict):
                issues.append(_normalize_resolver_issue(raw))
    return issues


def analyze_json_report(result: dict[str, Any]) -> dict[str, Any]:
    """Reduce a full ``analyze_markpact`` result to the stable CI contract."""
    issues = collect_analyze_issues(result)
    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]

    report: dict[str, Any] = {
        "format": ANALYZE_JSON_FORMAT,
        "ok": bool(result.get("ok")),
        "package_id": result["package_id"],
        "scheme": result["scheme"],
        "capabilities": result["capabilities"],
        "flow_count": len(result.get("flows") or []),
        "issue_codes": sorted({i["code"] for i in issues}),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "issues": issues,
    }

    if result.get("scheme") == "process":
        report["use_cases"] = list(result.get("use_cases") or [])
        report["integrations"] = list(result.get("integrations") or [])
        report["undeclared_uses"] = list(result.get("undeclared_uses") or [])
        resolver = result.get("resolver")
        report["resolver_ok"] = True if resolver is None else bool(resolver.get("ok", True))

    if result.get("strict"):
        report["strict"] = True
    if result.get("strict_operations"):
        report["strict_operations"] = True

    return report


__all__ = ["ANALYZE_JSON_FORMAT", "analyze_json_report", "collect_analyze_issues"]
