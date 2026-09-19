from unittest.mock import patch

import pytest

from urisys.managers.pack_manager import PackManager
from pack_registry import all_promoted_packs, sibling_repo_names


def test_default_discovery_preserves_successors_without_chat():
    packs = PackManager.parse_packs("all")
    assert "chat" not in packs
    assert {"llm", "message"} <= set(packs)
    assert "urichat" not in all_promoted_packs()
    assert "urichat" not in sibling_repo_names()
    assert {"urillm", "urimessage"} <= all_promoted_packs()


@pytest.mark.parametrize("spec", ["chat", "urichat"])
def test_explicit_retired_pack_never_uses_import_or_local_backup(spec):
    with PackManager(packs=spec) as manager:
        with patch.object(manager, "_resolve_importable_manifest") as imported, patch(
            "urisys.managers.pack_manager._sibling_manifest_path"
        ) as sibling:
            with pytest.raises(ModuleNotFoundError, match="retired.*llm.*message"):
                manager.manifest_paths()
        imported.assert_not_called()
        sibling.assert_not_called()
