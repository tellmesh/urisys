from __future__ import annotations

import hashlib
import json
import re
import shlex
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml


_FENCE_RE = re.compile(
    r"^```(?P<lang>[A-Za-z0-9_+.-]+)\s+markpact:(?P<kind>[A-Za-z0-9_-]+)(?P<meta>[^\n]*)\n(?P<content>.*?)^```\s*$",
    re.MULTILINE | re.DOTALL,
)


@dataclass(frozen=True)
class MarkpactBlock:
    lang: str
    kind: str
    meta: dict[str, str] = field(default_factory=dict)
    content: str = ""


@dataclass(frozen=True)
class CompiledMarkpact:
    source_path: Path
    source_hash: str
    cache_dir: Path
    package_id: str
    module_name: str
    manifest_path: Path
    tests_path: Path | None = None
    docs_path: Path | None = None
    metadata_path: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": str(self.source_path),
            "source_hash": self.source_hash,
            "cache_dir": str(self.cache_dir),
            "package_id": self.package_id,
            "module_name": self.module_name,
            "manifest_path": str(self.manifest_path),
            "tests_path": str(self.tests_path) if self.tests_path else None,
            "docs_path": str(self.docs_path) if self.docs_path else None,
            "metadata_path": str(self.metadata_path) if self.metadata_path else None,
        }


class MarkpactError(ValueError):
    """Raised when a Markpact cannot be parsed, validated or compiled."""


def _safe_identifier(value: str, *, fallback: str = "pack") -> str:
    value = re.sub(r"[^0-9A-Za-z_]+", "_", value.strip())
    value = re.sub(r"_+", "_", value).strip("_")
    if not value:
        value = fallback
    if value[0].isdigit():
        value = "_" + value
    return value.lower()


def _parse_meta(raw: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    if not raw.strip():
        return meta
    for token in shlex.split(raw.strip()):
        if "=" in token:
            key, value = token.split("=", 1)
            meta[key.strip()] = value.strip().strip('"\'')
        else:
            meta[token.strip()] = "true"
    return meta


def _scheme_from_uri(uri: str) -> str:
    parsed = urlsplit(uri)
    if not parsed.scheme:
        raise MarkpactError(f"Capability URI has no scheme: {uri!r}")
    return parsed.scheme


class MarkpactManager:
    """Parses and compiles one-file UriPack Markpacts.

    Markpact is an authoring/distribution format. Runtime uses a cached,
    generated manifest and extracted handler modules for speed and safety.
    """

    def __init__(self, cache_root: str | Path = ".urisys/cache/markpacts") -> None:
        self.cache_root = Path(cache_root)

    def read_blocks(self, path: str | Path) -> list[MarkpactBlock]:
        source_path = Path(path)
        text = source_path.read_text(encoding="utf-8")
        blocks: list[MarkpactBlock] = []
        for match in _FENCE_RE.finditer(text):
            blocks.append(
                MarkpactBlock(
                    lang=match.group("lang"),
                    kind=match.group("kind"),
                    meta=_parse_meta(match.group("meta") or ""),
                    content=match.group("content").strip() + "\n",
                )
            )
        return blocks

    def source_hash(self, path: str | Path) -> str:
        data = Path(path).read_bytes()
        return hashlib.sha256(data).hexdigest()

    def load_pack_block(self, path: str | Path) -> dict[str, Any]:
        blocks = self.read_blocks(path)
        pack_blocks = [b for b in blocks if b.kind == "pack" and b.lang in {"yaml", "yml"}]
        if len(pack_blocks) != 1:
            raise MarkpactError(f"{path}: expected exactly one ```yaml markpact:pack``` block, found {len(pack_blocks)}.")
        data = yaml.safe_load(pack_blocks[0].content) or {}
        if not isinstance(data, dict):
            raise MarkpactError(f"{path}: markpact:pack block must contain a YAML mapping.")
        return data

    def load_pack_block(self, path: str | Path) -> dict[str, Any]:
        blocks = self.read_blocks(path)
        pack_blocks = self._yaml_blocks(blocks, "pack")
        if len(pack_blocks) != 1:
            raise MarkpactError(f"{path}: expected exactly one ```yaml markpact:pack``` block, found {len(pack_blocks)}.")
        data = yaml.safe_load(pack_blocks[0].content) or {}
        if not isinstance(data, dict):
            raise MarkpactError(f"{path}: markpact:pack block must contain a YAML mapping.")
        return data

    def validate(self, path: str | Path) -> dict[str, Any]:
        source_path = Path(path)
        blocks = self.read_blocks(source_path)
        pack_blocks = self._yaml_blocks(blocks, "pack")
        contract_blocks = self._yaml_blocks(blocks, "contract")
        bundle_blocks = self._yaml_blocks(blocks, "bundle")
        impl_blocks = self._yaml_blocks(blocks, "implementation")

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
            return self._validate_pack(source_path, blocks, yaml.safe_load(pack_blocks[0].content) or {})
        if len(contract_blocks) == 1:
            return self._validate_contract(source_path, yaml.safe_load(contract_blocks[0].content) or {})
        if len(bundle_blocks) == 1:
            return self._validate_bundle(source_path, yaml.safe_load(bundle_blocks[0].content) or {})
        if len(impl_blocks) == 1:
            return self._validate_implementation(source_path, yaml.safe_load(impl_blocks[0].content) or {})

        raise MarkpactError(
            f"{path}: expected exactly one ```yaml markpact:{{pack|contract|bundle|implementation}}``` block."
        )

    def _validate_pack(self, source_path: Path, blocks: list[MarkpactBlock], pack: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(pack, dict):
            raise MarkpactError(f"{source_path}: markpact:pack block must contain a YAML mapping.")
        package_id = self._package_id(pack, source_path)
        capabilities = self._capabilities(pack)
        handler_blocks = self._handler_blocks(blocks)
        declared_handler_ids = set(handler_blocks)
        needed_handler_ids = {
            self._handler_id_from_ref(str(item.get("handler") or ""))
            for item in capabilities
            if str(item.get("handler") or "").startswith("markpact://")
        }
        missing_handlers = sorted(h for h in needed_handler_ids if h and h not in declared_handler_ids)
        warnings = []
        if missing_handlers:
            warnings.append(f"Missing handler blocks: {', '.join(missing_handlers)}")
        if not capabilities:
            raise MarkpactError(f"{source_path}: no capabilities/uri_patterns defined.")
        scheme = self._scheme(pack, capabilities)
        return {
            "ok": not missing_handlers,
            "kind": "pack",
            "path": str(source_path),
            "package_id": package_id,
            "scheme": scheme,
            "capabilities": len(capabilities),
            "handler_blocks": sorted(declared_handler_ids),
            "source_hash": self.source_hash(source_path),
            "warnings": warnings,
        }

    def _validate_contract(self, source_path: Path, data: dict[str, Any]) -> dict[str, Any]:
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
                item_scheme = _scheme_from_uri(pattern)
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
            "source_hash": self.source_hash(source_path),
            "warnings": warnings,
        }

    def _validate_bundle(self, source_path: Path, data: dict[str, Any]) -> dict[str, Any]:
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
            "source_hash": self.source_hash(source_path),
            "warnings": warnings,
        }

    def _validate_implementation(self, source_path: Path, data: dict[str, Any]) -> dict[str, Any]:
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
            "source_hash": self.source_hash(source_path),
            "warnings": warnings,
        }

    def _yaml_blocks(self, blocks: list[MarkpactBlock], kind: str) -> list[MarkpactBlock]:
        return [b for b in blocks if b.kind == kind and b.lang in {"yaml", "yml"}]

    def compile(self, path: str | Path, *, out_dir: str | Path | None = None, force: bool = False) -> CompiledMarkpact:
        source_path = Path(path)
        blocks = self.read_blocks(source_path)
        pack = self.load_pack_block(source_path)
        digest = self.source_hash(source_path)
        package_id = self._package_id(pack, source_path)
        safe_package_id = _safe_identifier(package_id)
        module_name = f"urisys_markpact_{safe_package_id}_{digest[:10]}"
        root = Path(out_dir) if out_dir else self.cache_root
        cache_dir = root / safe_package_id / digest[:16]
        package_dir = cache_dir / module_name
        manifest_path = cache_dir / "manifest.yaml"
        tests_path = cache_dir / "tests.yaml"
        docs_path = cache_dir / "README.generated.md"
        metadata_path = cache_dir / "markpact.json"

        if manifest_path.exists() and not force:
            self._ensure_importable(cache_dir)
            return CompiledMarkpact(
                source_path=source_path,
                source_hash=digest,
                cache_dir=cache_dir,
                package_id=package_id,
                module_name=module_name,
                manifest_path=manifest_path,
                tests_path=tests_path if tests_path.exists() else None,
                docs_path=docs_path if docs_path.exists() else None,
                metadata_path=metadata_path if metadata_path.exists() else None,
            )

        validation = self.validate(source_path)
        if not validation["ok"]:
            raise MarkpactError("; ".join(validation.get("warnings") or ["Markpact validation failed."]))

        cache_dir.mkdir(parents=True, exist_ok=True)
        package_dir.mkdir(parents=True, exist_ok=True)
        (package_dir / "__init__.py").write_text("# generated by urisys Markpact compiler\n", encoding="utf-8")

        handler_blocks = self._handler_blocks(blocks)
        for handler_id, block in handler_blocks.items():
            if block.lang not in {"python", "py"}:
                continue
            module_file = package_dir / f"{_safe_identifier(handler_id, fallback='handler')}.py"
            content = block.content
            if "def handle" not in content and "async def handle" not in content:
                raise MarkpactError(
                    f"Handler block id={handler_id!r} must define a callable named handle(payload, context)."
                )
            module_file.write_text(content, encoding="utf-8")

        manifest = self._compile_manifest(pack, package_id=package_id, module_name=module_name, source_hash=digest)
        manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")

        tests = self._load_yaml_blocks(blocks, "tests")
        if tests:
            tests_path.write_text(yaml.safe_dump(tests[0], sort_keys=False, allow_unicode=True), encoding="utf-8")
        else:
            tests_path = None  # type: ignore[assignment]

        docs = [b.content.strip() for b in blocks if b.kind == "docs"]
        if docs:
            docs_path.write_text("\n\n".join(docs) + "\n", encoding="utf-8")
        else:
            docs_path = None  # type: ignore[assignment]

        metadata = {
            "kind": "CompiledUriPackMarkpact",
            "source_path": str(source_path),
            "source_hash": digest,
            "package_id": package_id,
            "module_name": module_name,
            "manifest_path": str(manifest_path),
        }
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        (cache_dir / "source.markpact.md").write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")
        self._ensure_importable(cache_dir)

        return CompiledMarkpact(
            source_path=source_path,
            source_hash=digest,
            cache_dir=cache_dir,
            package_id=package_id,
            module_name=module_name,
            manifest_path=manifest_path,
            tests_path=tests_path if isinstance(tests_path, Path) and tests_path.exists() else None,
            docs_path=docs_path if isinstance(docs_path, Path) and docs_path.exists() else None,
            metadata_path=metadata_path,
        )

    def manifest_path_for(self, path: str | Path) -> Path:
        return self.compile(path).manifest_path

    def run_tests(self, path: str | Path, *, events_path: str | Path | None = None) -> dict[str, Any]:
        compiled = self.compile(path)
        if not compiled.tests_path or not compiled.tests_path.exists():
            return {"ok": True, "compiled": compiled.to_dict(), "tests": [], "message": "No markpact:tests block."}

        from ..controllers.uri_controller import UriController
        from ..defaults import DEFAULT_ENVIRONMENT

        test_data = yaml.safe_load(compiled.tests_path.read_text(encoding="utf-8")) or {}
        tests = test_data.get("tests") or [] if isinstance(test_data, dict) else []
        results = []
        ctrl = UriController(packs=str(compiled.manifest_path), events_path=str(events_path or compiled.cache_dir / "test-events.jsonl"))
        try:
            for item in tests:
                uri = item["uri"]
                payload = item.get("payload") or {}
                context = item.get("context") or {}
                expect = item.get("expect") or {}
                result = ctrl.call(
                    uri,
                    payload,
                    approved=bool(context.get("approved")),
                    dry_run=bool(context.get("dry_run")),
                    allow_real=bool(context.get("allow_real")),
                    environment=str(context.get("environment", DEFAULT_ENVIRONMENT)),
                    context=context,
                )
                ok = True
                failures = []
                if "ok" in expect and bool(result.get("ok")) != bool(expect["ok"]):
                    ok = False
                    failures.append(f"expected ok={expect['ok']!r}, got {result.get('ok')!r}")
                if "operation" in expect and result.get("operation") != expect["operation"]:
                    ok = False
                    failures.append(f"expected operation={expect['operation']!r}, got {result.get('operation')!r}")
                if "result_contains" in expect:
                    for key, expected_value in (expect.get("result_contains") or {}).items():
                        if result.get("result", {}).get(key) != expected_value:
                            ok = False
                            failures.append(f"expected result.{key}={expected_value!r}, got {result.get('result', {}).get(key)!r}")
                results.append({"id": item.get("id", uri), "ok": ok, "failures": failures, "result": result})
        finally:
            ctrl.close()
        return {"ok": all(r["ok"] for r in results), "compiled": compiled.to_dict(), "tests": results}

    def _compile_manifest(self, pack: dict[str, Any], *, package_id: str, module_name: str, source_hash: str) -> dict[str, Any]:
        capabilities = self._capabilities(pack)
        scheme = self._scheme(pack, capabilities)
        version = pack.get("version") or (pack.get("metadata") or {}).get("version") or 1
        handlers: dict[str, str] = {}
        uri_patterns = []

        for item in capabilities:
            pattern = str(item.get("pattern") or item.get("uri") or "")
            if not pattern:
                raise MarkpactError(f"Capability in {package_id!r} has no uri/pattern: {item!r}")
            item_scheme = _scheme_from_uri(pattern)
            if item_scheme != scheme:
                raise MarkpactError(
                    f"UriPack Markpact currently supports one scheme per file. Expected {scheme!r}, got {item_scheme!r}."
                )
            operation = str(item.get("operation") or item.get("id") or "").split(".")[-1].replace("-", "_")
            if not operation:
                raise MarkpactError(f"Capability has no operation/id: {item!r}")
            kind = str(item.get("kind") or ("command" if "/command/" in pattern else "query"))
            handler_ref = item.get("handler")
            if isinstance(handler_ref, str) and handler_ref.startswith("markpact://"):
                handler_id = self._handler_id_from_ref(handler_ref)
                handlers[operation] = f"python://{module_name}.{_safe_identifier(handler_id)}:handle"
                handler_ref = handlers[operation]
            elif isinstance(handler_ref, str) and handler_ref.startswith("python://"):
                handlers[operation] = handler_ref
            route = {
                "pattern": pattern,
                "kind": kind,
                "operation": operation,
                "side_effects": bool(item.get("side_effects", kind == "command")),
                "approval": item.get("approval", "required" if kind == "command" else "not_required"),
            }
            for key in ["command_type", "query_type", "result_type", "success_event_type", "description"]:
                if key in item:
                    route[key] = item[key]
            if handler_ref:
                route["handler"] = handler_ref
            uri_patterns.append(route)

        metadata = pack.get("metadata") or {}
        manifest = {
            "id": package_id,
            "version": version,
            "scheme": scheme,
            "description": pack.get("description") or metadata.get("description") or f"UriPack generated from Markpact {package_id}.",
            "generated_from": str(pack.get("generated_from") or "markpact"),
            "source_hash": source_hash,
            "uri_patterns": uri_patterns,
            "handlers": {"python": handlers},
        }
        for optional_key in ["policy", "runtime", "environment", "dependencies"]:
            if optional_key in pack:
                manifest[optional_key] = pack[optional_key]
        return manifest

    def _package_id(self, pack: dict[str, Any], path: Path) -> str:
        metadata = pack.get("metadata") or {}
        value = pack.get("id") or metadata.get("id") or path.stem.replace(".markpact", "")
        value = str(value).strip()
        if not value:
            raise MarkpactError(f"{path}: package id is required.")
        return value

    def _capabilities(self, pack: dict[str, Any]) -> list[dict[str, Any]]:
        raw = pack.get("uri_patterns") or pack.get("capabilities") or []
        if not isinstance(raw, list):
            raise MarkpactError("capabilities/uri_patterns must be a list.")
        return [item for item in raw if isinstance(item, dict)]

    def _scheme(self, pack: dict[str, Any], capabilities: list[dict[str, Any]]) -> str:
        if pack.get("scheme"):
            return str(pack["scheme"])
        schemes = pack.get("schemes") or []
        if isinstance(schemes, list) and schemes:
            return str(schemes[0])
        if capabilities:
            return _scheme_from_uri(str(capabilities[0].get("pattern") or capabilities[0].get("uri") or ""))
        raise MarkpactError("Cannot infer scheme from Markpact.")

    def _handler_blocks(self, blocks: list[MarkpactBlock]) -> dict[str, MarkpactBlock]:
        result: dict[str, MarkpactBlock] = {}
        for block in blocks:
            if block.kind != "handler":
                continue
            handler_id = block.meta.get("id") or block.meta.get("name")
            if not handler_id:
                raise MarkpactError("markpact:handler block must define id=<handler_id>.")
            result[handler_id] = block
        return result

    def _load_yaml_blocks(self, blocks: list[MarkpactBlock], kind: str) -> list[dict[str, Any]]:
        parsed = []
        for block in blocks:
            if block.kind != kind or block.lang not in {"yaml", "yml"}:
                continue
            data = yaml.safe_load(block.content) or {}
            if not isinstance(data, dict):
                raise MarkpactError(f"markpact:{kind} block must contain a YAML mapping.")
            parsed.append(data)
        return parsed

    def _handler_id_from_ref(self, ref: str) -> str:
        if not ref:
            return ""
        return ref.rstrip("/").split("/")[-1]

    def _ensure_importable(self, cache_dir: Path) -> None:
        value = str(cache_dir.resolve())
        if value not in sys.path:
            sys.path.insert(0, value)
