from __future__ import annotations

from ....managers.markpact_profile import LintIssue
from ..context import MarkpactLintContext


class MP009ProcessRequiresSchemes:
    code = "MP009"

    def check(self, ctx: MarkpactLintContext) -> list[LintIssue]:
        if ctx.scheme != "process":
            return []
        if ctx.schemes_required or ctx.pack.get("requires"):
            return []
        return [
            LintIssue(
                code=self.code,
                severity="warning",
                message="process pack should declare requires.schemes explicitly (v1alpha)",
            )
        ]


class MP010RequiresCapabilitiesNamespaced:
    code = "MP010"

    def check(self, ctx: MarkpactLintContext) -> list[LintIssue]:
        requires = ctx.pack.get("requires")
        if not isinstance(requires, dict):
            return []
        requires_caps = requires.get("capabilities")
        if not isinstance(requires_caps, list) or not requires_caps:
            return []
        issues: list[LintIssue] = []
        for cap_name in requires_caps:
            if "." not in str(cap_name):
                issues.append(
                    LintIssue(
                        code=self.code,
                        severity="warning",
                        message=f"requires.capabilities entry {cap_name!r} should be namespaced",
                        location=str(cap_name),
                    )
                )
        return issues
