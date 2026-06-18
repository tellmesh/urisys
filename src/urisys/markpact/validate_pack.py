"""Validate Markpact pack blocks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..managers.markpact_models import MarkpactBlock, MarkpactError, source_hash
from .blocks import handler_blocks, read_blocks, yaml_blocks
from .handlers import handler_id_from_ref
from .pack import capabilities, load_pack_block, package_id, scheme_for_pack


def validate_pack(source_path: Path, blocks: list[MarkpactBlock], pack: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(pack, dict):
        raise MarkpactError(f"{source_path}: markpact:pack block must contain a YAML mapping.")
    pkg_id = package_id(pack, source_path)
    caps = capabilities(pack)
    handlers = handler_blocks(blocks)
    declared_handler_ids = set(handlers)
    needed_handler_ids = {
        handler_id_from_ref(str(item.get("handler") or ""))
        for item in caps
        if str(item.get("handler") or "").startswith("markpact://")
    }
    missing_handlers = sorted(h for h in needed_handler_ids if h and h not in declared_handler_ids)
    warnings: list[str] = []
    if missing_handlers:
        warnings.append(f"Missing handler blocks: {', '.join(missing_handlers)}")
    if not caps:
        raise MarkpactError(f"{source_path}: no capabilities/uri_patterns defined.")
    scheme = scheme_for_pack(pack, caps)
    return {
        "ok": not missing_handlers,
        "kind": "pack",
        "path": str(source_path),
        "package_id": pkg_id,
        "scheme": scheme,
        "capabilities": len(caps),
        "handler_blocks": sorted(declared_handler_ids),
        "source_hash": source_hash(source_path),
        "warnings": warnings,
    }


def validate_markpact_file(path: str | Path) -> dict[str, Any]:
    from ..managers.markpact_validation import validate_bundle, validate_contract, validate_implementation

    source_path = Path(path)
    blocks = read_blocks(source_path)
    pack_blocks = yaml_blocks(blocks, "pack")
    contract_blocks = yaml_blocks(blocks, "contract")
    bundle_blocks = yaml_blocks(blocks, "bundle")
    impl_blocks = yaml_blocks(blocks, "implementation")

    kinds = [
        name
        for name, items in (
            ("pack", pack_blocks),
            ("contract", contract_blocks),
            ("bundle", bundle_blocks),
            ("implementation", impl_blocks),
        )
        if len(items) == 1
    ]
    if len(kinds) > 1:
        raise MarkpactError(f"{path}: expected one markpact kind per file, found: {', '.join(kinds)}.")

    if len(pack_blocks) == 1:
        import yaml

        return validate_pack(source_path, blocks, yaml.safe_load(pack_blocks[0].content) or {})
    sh = source_hash(source_path)
    if len(contract_blocks) == 1:
        import yaml

        return validate_contract(source_path, yaml.safe_load(contract_blocks[0].content) or {}, sh)
    if len(bundle_blocks) == 1:
        import yaml

        return validate_bundle(source_path, yaml.safe_load(bundle_blocks[0].content) or {}, sh)
    if len(impl_blocks) == 1:
        import yaml

        return validate_implementation(source_path, yaml.safe_load(impl_blocks[0].content) or {}, sh)

    raise MarkpactError(
        f"{path}: expected exactly one ```yaml markpact:{{pack|contract|bundle|implementation}}``` block."
    )


__all__ = ["validate_markpact_file", "validate_pack"]
