from __future__ import annotations

from pathlib import Path

from urisys.managers.markpact_materialize import materialize_markpact

TELLMESH = Path(__file__).resolve().parents[2]
URISHELL = TELLMESH / "urishell" / "markpacts" / "urishell.markpact.md"


def test_materialize_unpacks_markpact_tree(tmp_path):
    if not URISHELL.is_file():
        import pytest

        pytest.skip("urishell.markpact.md not generated yet")
    result = materialize_markpact(URISHELL, root=tmp_path / ".markpact")
    dest = Path(result["materialized"]["materialized_dir"])
    assert (dest / "manifest.yaml").is_file()
    assert (dest / "materialize.json").is_file()
    assert (dest / "flows").is_dir()
    assert result["ok"] is True
