"""Validators for the standalone Markpact kinds (contract / bundle / implementation).

Split out of ``markpact_manager``: these are pure functions of the parsed YAML
mapping plus the source hash — they do not touch manager/compile state. The
``pack`` validator stays in the manager because it shares the compile helpers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .markpact_models import MarkpactError, scheme_from_uri


def validate_contract(source_path: Path, data: dict[str, Any], source_hash: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise MarkpactError(f"{source_path}: markpact:contract block must contain a YAML mapping.")
    metadata = data.get("metadata") or {}
    contract_id = str(metadata.get("id") or "").strip()
    if not contract_id:
        raise MarkpactError(f"{source_path}: contract metadata.id is required.")
    kind = str(data.get("kind") or "UriContract")
    if kind != "UriContract":
        raise MarkpactError(f"{source_path}: expected kind UriContract, got {kind!r}.")
    scheme = str(data.get("scheme") or "").strip()
    if not scheme:
        raise MarkpactError(f"{source_path}: contract scheme is required.")

    routes: list[dict[str, Any]] = []
    warnings: list[str] = []
    for section in ("queries", "commands"):
        items = data.get(section) or []
        if not isinstance(items, list):
            raise MarkpactError(f"{source_path}: contract {section} must be a list.")
        for item in items:
            if not isinstance(item, dict):
                raise MarkpactError(f"{source_path}: invalid entry in contract {section}.")
            item_id = str(item.get("id") or "").strip()
            pattern = str(item.get("pattern") or "").strip()
            if not item_id or not pattern:
                raise MarkpactError(f"{source_path}: contract {section} entries require id and pattern.")
            item_scheme = scheme_from_uri(pattern)
            if item_scheme != scheme:
                raise MarkpactError(
                    f"{source_path}: pattern {pattern!r} scheme {item_scheme!r} != contract scheme {scheme!r}."
                )
            routes.append(item)

    resources = data.get("resources") or []
    if not routes and not resources:
        raise MarkpactError(f"{source_path}: contract must define queries, commands, or resources.")

    return {
        "ok": True,
        "kind": "contract",
        "path": str(source_path),
        "contract_id": contract_id,
        "scheme": scheme,
        "capabilities": len(routes),
        "resources": len(resources) if isinstance(resources, list) else 0,
        "source_hash": source_hash,
        "warnings": warnings,
    }


def validate_bundle(source_path: Path, data: dict[str, Any], source_hash: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise MarkpactError(f"{source_path}: markpact:bundle block must contain a YAML mapping.")
    metadata = data.get("metadata") or {}
    bundle_id = str(metadata.get("id") or "").strip()
    if not bundle_id:
        raise MarkpactError(f"{source_path}: bundle metadata.id is required.")
    kind = str(data.get("kind") or "UriBundle")
    if kind != "UriBundle":
        raise MarkpactError(f"{source_path}: expected kind UriBundle, got {kind!r}.")

    imports = data.get("imports") or {}
    warnings: list[str] = []
    missing: list[str] = []
    if isinstance(imports, dict):
        for section in ("contracts", "implementations"):
            for rel in imports.get(section) or []:
                ref = source_path.parent / str(rel)
                if not ref.is_file():
                    missing.append(str(rel))
    if missing:
        warnings.append(f"Missing import files: {', '.join(missing)}")

    return {
        "ok": not missing,
        "kind": "bundle",
        "path": str(source_path),
        "bundle_id": bundle_id,
        "imports": imports,
        "source_hash": source_hash,
        "warnings": warnings,
    }


def validate_implementation(source_path: Path, data: dict[str, Any], source_hash: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise MarkpactError(f"{source_path}: markpact:implementation block must contain a YAML mapping.")
    metadata = data.get("metadata") or {}
    impl_id = str(metadata.get("id") or "").strip()
    if not impl_id:
        raise MarkpactError(f"{source_path}: implementation metadata.id is required.")
    kind = str(data.get("kind") or "UriImplementation")
    if kind != "UriImplementation":
        raise MarkpactError(f"{source_path}: expected kind UriImplementation, got {kind!r}.")

    implements = data.get("implements") or {}
    contract_ref = ""
    if isinstance(implements, dict):
        contract_ref = str(implements.get("contract") or "").strip()
    if not contract_ref:
        raise MarkpactError(f"{source_path}: implementation implements.contract is required.")

    capabilities = data.get("capabilities") or []
    if not isinstance(capabilities, list) or not capabilities:
        raise MarkpactError(f"{source_path}: implementation must declare capabilities.")

    warnings: list[str] = []
    for item in capabilities:
        if not isinstance(item, dict):
            raise MarkpactError(f"{source_path}: invalid implementation capability entry.")
        handler = str(item.get("handler") or "").strip()
        if not handler:
            warnings.append("Capability without handler reference.")

    return {
        "ok": True,
        "kind": "implementation",
        "path": str(source_path),
        "implementation_id": impl_id,
        "implements": contract_ref,
        "capabilities": len(capabilities),
        "source_hash": source_hash,
        "warnings": warnings,
    }
