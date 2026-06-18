"""Backward-compatible re-export — see ``urisys.markpact.models``."""

from ..markpact.models import (
    CompiledMarkpact,
    FENCE_RE,
    MarkpactBlock,
    MarkpactError,
    parse_meta,
    safe_identifier,
    scheme_from_uri,
    source_hash,
)

__all__ = [
    "CompiledMarkpact",
    "FENCE_RE",
    "MarkpactBlock",
    "MarkpactError",
    "parse_meta",
    "safe_identifier",
    "scheme_from_uri",
    "source_hash",
]
