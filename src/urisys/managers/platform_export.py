"""Backward-compatible re-export — see ``urisys.markpact.platform_export``."""

from ..markpact.platform_export import (
    build_resolver_yaml,
    collect_process_uris,
    export_platform_artifacts,
)

__all__ = [
    "collect_process_uris",
    "build_resolver_yaml",
    "export_platform_artifacts",
]
