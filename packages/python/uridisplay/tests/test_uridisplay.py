from __future__ import annotations

from uri_control import CapabilityRegistry
import uridisplay


def test_manifest_loads():
    registry = CapabilityRegistry.from_manifest_files([uridisplay.manifest_path()])
    assert registry.manifests[0].scheme == "display"
    assert registry.routes
