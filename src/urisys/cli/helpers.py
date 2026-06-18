from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..managers.source_manager import SourceManager


def json_arg(value: str | None) -> dict:
    if not value:
        return {}
    if value.startswith("@"):
        return json.loads(Path(value[1:]).read_text(encoding="utf-8"))
    return json.loads(value)


def print_json(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def resolve_markpact_source(source: str, *, source_manager: SourceManager | None = None) -> str:
    if source_manager is None:
        from ..managers.source_manager import SourceManager

        source_manager = SourceManager()
    return str(source_manager.resolve(source))
