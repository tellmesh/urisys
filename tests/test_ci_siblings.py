"""Exercise CI dependency setup without network access or package installation."""
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def setup(tmp_path, tool):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    log = tmp_path / "calls.jsonl"
    stub = bindir / tool
    stub.write_text("#!/usr/bin/env python3\nimport json,os,sys\n"
                    "with open(os.environ['CALL_LOG'], 'a') as f: print(json.dumps(sys.argv[1:]), file=f)\n"
                    "sys.exit(1 if os.environ.get('FAIL_CLONE') else 0)\n")
    stub.chmod(0o755)
    env = dict(os.environ, PATH=str(bindir)+os.pathsep+os.environ['PATH'],
               CALL_LOG=str(log), TELLMESH_ROOT=str(tmp_path), URISYS_ROOT=str(ROOT))
    return env, log


def run(script, env):
    return subprocess.run(['bash', str(ROOT / 'scripts' / script)], env=env,
                          capture_output=True, text=True)


def test_checkout_pins_renamed_core_and_omits_retired_repo(tmp_path):
    env, log = setup(tmp_path, 'git')
    result = run('ci-checkout-siblings.sh', env)
    assert result.returncode == 0, result.stderr
    calls = [json.loads(line) for line in log.read_text().splitlines()]
    core = next(c for c in calls if c[-1].endswith('/uricontrol'))
    assert core[core.index('--branch')+1] == 'v0.1.14'
    assert not any(c[-1].endswith('/urichat') for c in calls)
    assert any(c[-1].endswith('/urisys-dev') for c in calls)


def test_checkout_reports_clone_failure(tmp_path):
    env, _ = setup(tmp_path, 'git')
    env['FAIL_CLONE'] = '1'
    result = run('ci-checkout-siblings.sh', env)
    assert result.returncode != 0
    assert 'required sibling repositories unavailable' in result.stderr


def test_checkout_preserves_linked_worktree(tmp_path):
    env, log = setup(tmp_path, 'git')
    core = tmp_path / 'uricontrol'
    core.mkdir()
    (core / '.git').write_text('gitdir: elsewhere')
    assert run('ci-checkout-siblings.sh', env).returncode == 0
    assert not any(json.loads(line)[-1] == str(core) for line in log.read_text().splitlines())


def test_install_fails_before_pip_when_dependency_missing(tmp_path):
    env, log = setup(tmp_path, 'python')
    result = run('ci-install-siblings.sh', env)
    assert result.returncode != 0
    assert not log.exists()


def test_install_resolves_candidate_and_siblings_together(tmp_path):
    env, log = setup(tmp_path, 'python')
    names = 'uriguard uriresolver uritransport uricontrol urioperators urisys-node urisys-dev urikvm urihim uriocr urillm urikvmedge urirdp urishell uriscreen urimessage uristepper'.split()
    for name in names:
        path = tmp_path / name
        path.mkdir()
        (path / 'pyproject.toml').touch()
    result = run('ci-install-siblings.sh', env)
    assert result.returncode == 0, result.stderr
    calls = [json.loads(line) for line in log.read_text().splitlines()]
    assert len(calls) == 1
    assert str(ROOT) in calls[0]
    for name in names:
        assert str(tmp_path / name) in calls[0]
