from __future__ import annotations
from typing import Any
import yaml
from uri_control import CapabilityRegistry, InMemoryEventStore, UriControlRuntime
from .pack_loader import manifest_paths

def load_device_config(path: str | None) -> dict[str, Any]:
    if not path: return {}
    with open(path, "r", encoding="utf-8") as f: return yaml.safe_load(f) or {}

def load_env_config(path: str | None) -> dict[str, Any]:
    if not path: return {}
    with open(path, "r", encoding="utf-8") as f: return yaml.safe_load(f) or {}

def build_runtime(packs: list[str], extra_manifests: list[str] | None = None):
    paths = [str(p) for p in manifest_paths(packs)]; paths.extend(extra_manifests or [])
    registry = CapabilityRegistry.from_manifest_files(paths)
    return UriControlRuntime(registry=registry, event_store=InMemoryEventStore())

def result_to_dict(result) -> dict[str, Any]:
    return {"ok": result.ok, "uri": result.uri, "operation": result.operation, "result": result.result, "error": result.error, "event": result.event.__dict__ if result.event else None, "metadata": result.metadata}
