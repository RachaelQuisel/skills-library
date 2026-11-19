"""A registry row whose skill folder was deleted must not stop the release check."""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / 'scripts' / 'release_sync.py'


def make_repo(tmp_path):
    (tmp_path / 'scripts').mkdir()
    shutil.copy(SCRIPT, tmp_path / 'scripts' / 'release_sync.py')
    present = tmp_path / 'present' / 'SKILL.md'
    present.parent.mkdir()
    present.write_text('---\nname: present\nversion: 1.0.0\n---\n# Present\n')
    digest = hashlib.sha256(present.read_bytes()).hexdigest()
    registry = {
        'skills': [
            {'path': 'present/SKILL.md', 'source': 'present/SKILL.md', 'version': '1.0.0', 'sha256': digest},
            {'path': 'gone/SKILL.md', 'source': 'gone/SKILL.md', 'version': '1.0.0', 'sha256': 'x'},
        ],
        'copies': [
            {'source': 'present/SKILL.md', 'target': 'export/present/SKILL.md'},
            {'source': 'gone/SKILL.md', 'target': 'export/gone/SKILL.md'},
        ],
    }
    (tmp_path / 'release-registry.json').write_text(json.dumps(registry))
    return tmp_path


def run(repo, *args):
    return subprocess.run([sys.executable, str(repo / 'scripts' / 'release_sync.py'), *args],
                          cwd=repo, capture_output=True, text=True)


def test_missing_skill_folder_is_skipped_with_warning(tmp_path):
    repo = make_repo(tmp_path)
    result = run(repo, '--write')
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'Traceback' not in result.stderr
    assert 'gone/SKILL.md' in result.stdout
    assert 'skipped' in result.stdout.lower()
    assert (repo / 'export/present/SKILL.md').exists()
    assert not (repo / 'export/gone/SKILL.md').exists()


def test_present_skills_are_still_checked(tmp_path):
    repo = make_repo(tmp_path)
    run(repo, '--write')
    (repo / 'present/SKILL.md').write_text('---\nname: present\nversion: 1.0.0\n---\n# Changed\n')
    result = run(repo)
    assert result.returncode == 1
    assert 'present/SKILL.md' in result.stdout
