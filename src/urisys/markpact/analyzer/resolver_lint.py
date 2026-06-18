"""Lint generated UriRuntime resolver stubs for process Markpacts."""

from __future__ import annotations

from typing import Any

from ..platform_export import build_resolver_yaml, collect_process_uris

_DEFAULT_PLATFORMS = ("linux", "server", "esp32")


def lint_process_resolver_stubs(
    path: str,
    *,
    platforms: tuple[str, ...] = _DEFAULT_PLATFORMS,
) -> dict[str, Any]:
    """Validate platform-export resolver YAML stubs with uri_router RR rules."""
    try:
        from uri_router.resolver.schema import validate_resolver_issues
    except ImportError:  # pragma: no cover
        return {"ok": True, "skipped": True, "issues": [], "platforms": {}}

    collected = collect_process_uris(path)
    if not collected.get("flow_ids"):
        return {"ok": True, "skipped": True, "issues": [], "platforms": {}}

    all_issues: list[dict[str, Any]] = []
    platform_results: dict[str, Any] = {}
    for platform in platforms:
        doc = build_resolver_yaml(
            platform=platform,
            authorities=collected["authorities"],
            schemes=collected["schemes"],
            package_id=collected["package_id"],
        )
        issues = validate_resolver_issues(doc)
        serialized = [
            {
                "code": i.code,
                "severity": i.severity,
                "message": i.message,
                "path": i.path,
                "platform": platform,
            }
            for i in issues
        ]
        errors = [i for i in serialized if i["severity"] == "error"]
        platform_results[platform] = {"ok": not errors, "issues": serialized}
        all_issues.extend(serialized)

    has_errors = any(i["severity"] == "error" for i in all_issues)
    return {
        "ok": not has_errors,
        "platforms": platform_results,
        "issues": all_issues,
        "issue_codes": sorted({i["code"] for i in all_issues}),
    }


__all__ = ["lint_process_resolver_stubs"]
