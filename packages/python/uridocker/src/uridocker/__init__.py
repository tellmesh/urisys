from __future__ import annotations

from importlib.resources import files

__all__ = ["manifest_path", "PACKAGE_NAME", "SCHEME"]

PACKAGE_NAME = "uridocker"
SCHEME = "docker"

def manifest_path():
    return files(__package__).joinpath("manifest.yaml")
