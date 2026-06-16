from __future__ import annotations

from uri_control import CapabilityRegistry
import uriandroid


def test_manifest_loads():
    registry = CapabilityRegistry.from_manifest_files([uriandroid.manifest_path()])
    assert registry.manifests[0].scheme == "android"
    assert registry.routes
