from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MarkpactLintContext:
    pack: dict[str, Any]
    scheme: str
    capabilities: list[dict[str, Any]]
    flows: list[dict[str, Any]]
    undeclared_schemes: list[str]
    schemes_required: set[str] = field(default_factory=set)
    packs_default: list[str] = field(default_factory=list)
