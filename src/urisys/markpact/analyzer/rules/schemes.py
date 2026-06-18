from __future__ import annotations

from ...profile import LintIssue
from ..context import MarkpactLintContext


class MP006UndeclaredScheme:
    code = "MP006"

    def check(self, ctx: MarkpactLintContext) -> list[LintIssue]:
        return [
            LintIssue(
                code=self.code,
                severity="error",
                message=f"flow uses undeclared scheme {s!r} (add to requires.schemes)",
                location=s,
            )
            for s in ctx.undeclared_schemes
        ]
