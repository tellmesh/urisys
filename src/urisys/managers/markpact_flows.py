"""Backward-compatible re-export — see ``urisys.markpact.flows``."""

from ..markpact.flows import (
    DOMAIN_SCHEME_PROVIDERS,
    _provider_scheme,
    classify_flow,
    declared_uses,
    extract_flows,
    extract_modules,
    extract_protos,
    flow_uris,
)

__all__ = [
    "DOMAIN_SCHEME_PROVIDERS",
    "_provider_scheme",
    "classify_flow",
    "declared_uses",
    "extract_flows",
    "extract_modules",
    "extract_protos",
    "flow_uris",
]
