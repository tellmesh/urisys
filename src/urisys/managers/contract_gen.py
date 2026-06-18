"""Backward-compatible re-export — see ``urisys_dev.contract_gen``."""

from urisys_dev.contract_gen import (
    API_VERSION,
    contract_id,
    diff_manifest_contract,
    load_contract_block,
    load_manifest,
    manifest_to_contract,
    normalize_version,
    render_contract_markpact,
)

__all__ = [
    "API_VERSION",
    "contract_id",
    "diff_manifest_contract",
    "load_contract_block",
    "load_manifest",
    "manifest_to_contract",
    "normalize_version",
    "render_contract_markpact",
]
