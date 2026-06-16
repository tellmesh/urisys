from __future__ import annotations

from uri_control import CapabilityRegistry
import uriagent


def test_manifest_loads():
    registry = CapabilityRegistry.from_manifest_files([uriagent.manifest_path()])
    assert registry.manifests[0].scheme == "agent"
    assert registry.routes
