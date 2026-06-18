"""Stateless data types and parsing helpers for Markpact authoring files."""

from __future__ import annotations

import hashlib
import re
import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

FENCE_RE = re.compile(
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
    flows_dir: Path | None = None
    flow_ids: tuple[str, ...] = ()
    proto_dir: Path | None = None
    proto_files: tuple[str, ...] = ()
    module_files: tuple[str, ...] = ()

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
            "flows_dir": str(self.flows_dir) if self.flows_dir else None,
            "flow_ids": list(self.flow_ids),
            "proto_dir": str(self.proto_dir) if self.proto_dir else None,
            "proto_files": list(self.proto_files),
            "module_files": list(self.module_files),
        }


class MarkpactError(ValueError):
    """Raised when a Markpact cannot be parsed, validated or compiled."""


def safe_identifier(value: str, *, fallback: str = "pack") -> str:
    value = re.sub(r"[^0-9A-Za-z_]+", "_", value.strip())
    value = re.sub(r"_+", "_", value).strip("_")
    if not value:
        value = fallback
    if value[0].isdigit():
        value = "_" + value
    return value.lower()


def parse_meta(raw: str) -> dict[str, str]:
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


def scheme_from_uri(uri: str) -> str:
    parsed = urlsplit(uri)
    if not parsed.scheme:
        raise MarkpactError(f"Capability URI has no scheme: {uri!r}")
    return parsed.scheme


def source_hash(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
