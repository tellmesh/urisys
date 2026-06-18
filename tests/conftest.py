"""Pytest hooks for markpact test isolation."""

from __future__ import annotations

import pytest

from pack_import_isolation import reset_embedded_pack_imports


@pytest.fixture(autouse=True)
def _cleanup_markpact_embedded_imports():
    yield
    reset_embedded_pack_imports()
