from __future__ import annotations

from typing import Protocol

from ...profile import LintIssue
from ..context import MarkpactLintContext


class MarkpactRule(Protocol):
    code: str

    def check(self, ctx: MarkpactLintContext) -> list[LintIssue]:
        ...


def cap_uri(cap: dict) -> str:
    return str(cap.get("uri") or cap.get("pattern") or "")
