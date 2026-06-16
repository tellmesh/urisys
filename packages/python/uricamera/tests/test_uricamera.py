from __future__ import annotations

from uri_control import CapabilityRegistry
import uricamera


def test_manifest_loads():
    registry = CapabilityRegistry.from_manifest_files([uricamera.manifest_path()])
    assert registry.manifests[0].scheme == "camera"
    assert registry.routes
