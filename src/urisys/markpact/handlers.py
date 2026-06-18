"""Generated handler modules and handler reference resolution."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..managers.markpact_models import MarkpactBlock, MarkpactError, safe_identifier


def handler_id_from_ref(ref: str) -> str:
    if not ref:
        return ""
    return ref.rstrip("/").split("/")[-1]


def resolve_handler_ref(
    handler_ref: Any,
    operation: str,
    module_name: str,
    handlers_python: dict[str, str],
    handlers_urisys: dict[str, str],
) -> Any:
    if isinstance(handler_ref, str) and handler_ref.startswith("markpact://"):
        handler_id = handler_id_from_ref(handler_ref)
        resolved = f"python://{module_name}.{safe_identifier(handler_id)}:handle"
        handlers_python[operation] = resolved
        return resolved
    if isinstance(handler_ref, str) and handler_ref.startswith("python://"):
        handlers_python[operation] = handler_ref
        return handler_ref
    if isinstance(handler_ref, str) and handler_ref.startswith("urisys://"):
        handlers_urisys[operation] = handler_ref
        return handler_ref
    return handler_ref


def write_handler_modules(package_dir: Path, blocks: dict[str, MarkpactBlock]) -> None:
    for handler_id, block in blocks.items():
        if block.lang not in {"python", "py"}:
            continue
        content = block.content
        if "def handle" not in content and "async def handle" not in content:
            raise MarkpactError(
                f"Handler block id={handler_id!r} must define a callable named handle(payload, context)."
            )
        module_file = package_dir / f"{safe_identifier(handler_id, fallback='handler')}.py"
        module_file.write_text(content, encoding="utf-8")


__all__ = ["handler_id_from_ref", "resolve_handler_ref", "write_handler_modules"]
