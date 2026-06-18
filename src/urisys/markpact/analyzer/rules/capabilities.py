from __future__ import annotations

from ....managers.markpact_profile import LintIssue
from ..context import MarkpactLintContext
from .base import cap_uri


class MP001NamespacedOperation:
    code = "MP001"

    def check(self, ctx: MarkpactLintContext) -> list[LintIssue]:
        issues: list[LintIssue] = []
        for cap in ctx.capabilities:
            op = str(cap.get("operation") or "").strip()
            if op and "." not in op:
                issues.append(
                    LintIssue(
                        code=self.code,
                        severity="warning",
                        message=f"operation {op!r} should be namespaced (e.g. stepper.status)",
                        location=cap_uri(cap) or op,
                    )
                )
        return issues


class MP002QueryKind:
    code = "MP002"

    def check(self, ctx: MarkpactLintContext) -> list[LintIssue]:
        issues: list[LintIssue] = []
        for cap in ctx.capabilities:
            uri = cap_uri(cap)
            kind = str(cap.get("kind") or "").strip()
            if uri and kind and "/query/" in uri and kind != "query":
                issues.append(
                    LintIssue(
                        code=self.code,
                        severity="error",
                        message=f"URI {uri!r} contains /query/ but kind is {kind!r}",
                        location=uri,
                    )
                )
        return issues


class MP003CommandKind:
    code = "MP003"

    def check(self, ctx: MarkpactLintContext) -> list[LintIssue]:
        issues: list[LintIssue] = []
        for cap in ctx.capabilities:
            uri = cap_uri(cap)
            kind = str(cap.get("kind") or "").strip()
            if uri and kind and "/command/" in uri and kind != "command":
                issues.append(
                    LintIssue(
                        code=self.code,
                        severity="error",
                        message=f"URI {uri!r} contains /command/ but kind is {kind!r}",
                        location=uri,
                    )
                )
        return issues


class MP004CommandApproval:
    code = "MP004"

    def check(self, ctx: MarkpactLintContext) -> list[LintIssue]:
        issues: list[LintIssue] = []
        for cap in ctx.capabilities:
            uri = cap_uri(cap)
            kind = str(cap.get("kind") or "").strip()
            op = str(cap.get("operation") or "").strip()
            if kind == "command" and cap.get("side_effects") and str(cap.get("approval") or "") == "not_required":
                issues.append(
                    LintIssue(
                        code=self.code,
                        severity="error",
                        message=f"command {op or uri!r} has side_effects:true but approval:not_required",
                        location=op or uri,
                    )
                )
        return issues


class MP005ProcessHandler:
    code = "MP005"

    def check(self, ctx: MarkpactLintContext) -> list[LintIssue]:
        if ctx.scheme != "process":
            return []
        issues: list[LintIssue] = []
        for cap in ctx.capabilities:
            op = str(cap.get("operation") or "").strip()
            handler = str(cap.get("handler") or "")
            if handler and not handler.startswith("urisys://flow/"):
                issues.append(
                    LintIssue(
                        code=self.code,
                        severity="error",
                        message=f"process capability {op!r} handler must be urisys://flow/<id>, got {handler!r}",
                        location=op,
                    )
                )
        return issues
