from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import generate_pack_markpacts as gen


def render(root):
    return gen._render(file_stem='sample', manifest={'id': 'sample', 'scheme': 'sample',
        'uri_patterns': [{'operation': 'sample.status', 'pattern': 'sample://local/query/status'}]},
        repo_dir=root / 'sample', manifest_file=root / 'sample' / 'manifest.yaml')


def test_render_independent_of_checkout_root(tmp_path, monkeypatch):
    monkeypatch.setattr(gen, 'TELLMESH', tmp_path / 'first')
    first = render(gen.TELLMESH)
    monkeypatch.setattr(gen, 'TELLMESH', tmp_path / 'second')
    assert render(gen.TELLMESH) == first
    assert str(tmp_path) not in first


def test_legacy_example_normalization_preserves_capability_drift(tmp_path, monkeypatch):
    monkeypatch.setattr(gen, 'TELLMESH', tmp_path)
    expected = render(tmp_path)
    legacy = expected.replace('export TELLMESH_ROOT="$(cd .. && pwd)"',
                              'export TELLMESH_ROOT=/home/old/workspace')
    assert gen.portable_workspace_docs(legacy) == expected
    changed = legacy.replace('sample://local/query/status', 'sample://local/query/other')
    assert gen.portable_workspace_docs(changed) != expected
    assert gen.portable_workspace_docs('export TELLMESH_ROOT=/outside/example') == 'export TELLMESH_ROOT=/outside/example'
