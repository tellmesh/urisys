from __future__ import annotations

from uri_control import CapabilityRegistry
import uriprinter


def test_manifest_loads():
    registry = CapabilityRegistry.from_manifest_files([uriprinter.manifest_path()])
    assert registry.manifests[0].scheme == "printer"
    assert registry.routes
