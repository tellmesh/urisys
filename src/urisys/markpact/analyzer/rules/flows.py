from __future__ import annotations

from ....managers.markpact_flows import flow_uris
from ....managers.markpact_profile import LintIssue
from ..context import MarkpactLintContext


class MP007ProcessExpect:
    code = "MP007"

    def check(self, ctx: MarkpactLintContext) -> list[LintIssue]:
        if ctx.scheme != "process":
            return []
        issues: list[LintIssue] = []
        for flow in ctx.flows:
            flow_id = flow["id"]
            if not flow["data"].get("expect"):
                issues.append(
                    LintIssue(
                        code=self.code,
                        severity="warning",
                        message=f"flow {flow_id!r} has no expect: block (v1alpha production processes)",
                        location=flow_id,
                    )
                )
        return issues


class MP008ImplicitLatest:
    code = "MP008"

    def check(self, ctx: MarkpactLintContext) -> list[LintIssue]:
        issues: list[LintIssue] = []
        for flow in ctx.flows:
            flow_id = flow["id"]
            for uri in flow_uris(flow["data"]):
                if "/image/latest/" in uri:
                    issues.append(
                        LintIssue(
                            code=self.code,
                            severity="warning",
                            message=f"flow {flow_id!r} uses implicit latest state in {uri!r}",
                            location=flow_id,
                        )
                    )
        return issues
