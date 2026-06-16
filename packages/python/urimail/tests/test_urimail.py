from __future__ import annotations

from uri_control import CapabilityRegistry
import urimail


def test_manifest_loads():
    registry = CapabilityRegistry.from_manifest_files([urimail.manifest_path()])
    assert registry.manifests[0].scheme == "mail"
    assert registry.routes
