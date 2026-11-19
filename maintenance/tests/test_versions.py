import importlib.util
import os
from pathlib import Path
import subprocess
import pytest

spec = importlib.util.spec_from_file_location('prepare_version', Path(__file__).parents[1] / 'prepare_version.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_moving_branch_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        m.prepare(tmp_path, 'main', tmp_path / 'copy')

def test_existing_destination_is_preserved(tmp_path):
    target = tmp_path / 'installed'
    target.mkdir()
    keep = target / 'important.txt'
    keep.write_text('unchanged')
    with pytest.raises(ValueError):
        m.prepare(tmp_path, 'a' * 40, target)
    assert keep.read_text() == 'unchanged'

def test_prepare_old_commit_leaves_current_version_unchanged(tmp_path):
    repo = tmp_path / 'repo'
    repo.mkdir()
    env = dict(os.environ, GIT_AUTHOR_NAME='Synthetic Test', GIT_AUTHOR_EMAIL='test@example.invalid', GIT_COMMITTER_NAME='Synthetic Test', GIT_COMMITTER_EMAIL='test@example.invalid')
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=repo, env=env, text=True).strip()
    git('init')
    f = repo / 'SKILL.md'
    f.write_text('old version')
    git('add', 'SKILL.md'); git('commit', '-m', 'old')
    old = git('rev-parse', 'HEAD')
    f.write_text('new version')
    git('add', 'SKILL.md'); git('commit', '-m', 'new')
    new = git('rev-parse', 'HEAD')
    target = m.prepare(repo, old, tmp_path / 'rollback')
    assert (target / 'SKILL.md').read_text() == 'old version'
    assert f.read_text() == 'new version'
    assert git('rev-parse', 'HEAD') == new
