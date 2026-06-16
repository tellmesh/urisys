from __future__ import annotations

from uri_control import CapabilityRegistry
import urisystemd


def test_manifest_loads():
    registry = CapabilityRegistry.from_manifest_files([urisystemd.manifest_path()])
    assert registry.manifests[0].scheme == "systemd"
    assert registry.routes
