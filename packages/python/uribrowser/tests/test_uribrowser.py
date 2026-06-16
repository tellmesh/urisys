from __future__ import annotations

from uri_control import CapabilityRegistry
import uribrowser


def test_manifest_loads():
    registry = CapabilityRegistry.from_manifest_files([uribrowser.manifest_path()])
    assert registry.manifests[0].scheme == "browser"
    assert registry.routes
