from __future__ import annotations

from uri_control import CapabilityRegistry
import uridocker


def test_manifest_loads():
    registry = CapabilityRegistry.from_manifest_files([uridocker.manifest_path()])
    assert registry.manifests[0].scheme == "docker"
    assert registry.routes
