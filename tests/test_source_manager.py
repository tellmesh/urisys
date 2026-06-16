from __future__ import annotations

from pathlib import Path

from urisys.managers.source_manager import SourceManager

ROOT = Path(__file__).resolve().parents[1]
BROWSER_MARKPACT = ROOT / "markpacts" / "packs" / "uribrowser.markpact.md"


def test_fetch_local_file(tmp_path):
    manager = SourceManager(cache_root=tmp_path / "sources")
    result = manager.fetch(f"file://{BROWSER_MARKPACT}")
    assert result["ok"] is True
    assert Path(result["local_path"]).exists()
    assert "browser" in Path(result["local_path"]).read_text(encoding="utf-8")


def test_fetch_github_raw(monkeypatch, tmp_path):
    manager = SourceManager(cache_root=tmp_path / "sources")

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b"# mock markpact\n"

    monkeypatch.setattr("urisys.managers.source_manager.urlopen", lambda *args, **kwargs: FakeResponse())
    result = manager.fetch("gh://tellmesh/urisys/markpacts/packs/uribrowser.markpact.md?ref=main")
    assert result["ok"] is True
    assert result["cached"] is True
