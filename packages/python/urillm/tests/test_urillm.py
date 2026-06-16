from __future__ import annotations

from uri_control import CapabilityRegistry
import urillm


def test_manifest_loads():
    registry = CapabilityRegistry.from_manifest_files([urillm.manifest_path()])
    assert registry.manifests[0].scheme == "llm"
    assert registry.routes
