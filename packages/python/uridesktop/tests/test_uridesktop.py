from __future__ import annotations

from uri_control import CapabilityRegistry
import uridesktop


def test_manifest_loads():
    registry = CapabilityRegistry.from_manifest_files([uridesktop.manifest_path()])
    assert registry.manifests[0].scheme == "desktop"
    assert registry.routes
