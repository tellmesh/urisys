from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from .context import RunContext


class MarkpactRunMode(Protocol):
    name: str

    def run(self, ctx: RunContext) -> dict[str, Any]:
        ...
