"""Prepare an exact version in a separate folder; never overwrite an installation."""
import argparse
from pathlib import Path
import re
import subprocess

def prepare(repo, commit, destination):
    repo = Path(repo).resolve()
    destination = Path(destination).resolve()
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Use a full 40-character commit SHA, not a moving branch name.')
    if destination.exists() or destination == repo or repo in destination.parents:
        raise ValueError('Choose a new folder outside the source repository.')
    subprocess.run(['git', 'cat-file', '-e', commit + '^{commit}'], cwd=repo, check=True, capture_output=True)
    subprocess.run(['git', 'worktree', 'add', '--detach', str(destination), commit], cwd=repo, check=True, capture_output=True)
    return destination

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--commit', required=True)
    p.add_argument('--destination', required=True, type=Path)
    a = p.parse_args()
    try:
        target = prepare(Path(__file__).resolve().parents[1], a.commit, a.destination)
    except (ValueError, subprocess.CalledProcessError) as exc:
        p.exit(1, str(exc) + '\n')
    print(f'Prepared {a.commit} at {target}. Installed skills were not changed. Review and explicitly choose this folder in your host before adopting it.')
