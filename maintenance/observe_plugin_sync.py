"""Read-only live capture. Connector credentials enter through hidden stdin only."""
import argparse
import concurrent.futures
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import posixpath
import re
import subprocess
import sys
import tarfile
import urllib.request
from urllib.parse import urlparse, unquote
import zipfile

from plugin_sync import check, validate_contract

ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return hashlib.sha256(value).hexdigest()


def json_bytes(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()


def compatibility(value, portable=None):
    value = json.loads(json.dumps(value))
    if portable is not None:
        value['interface'] = portable.get('extensions', {}).get('com.openai', {}).get('interface', {})
        if 'author' in portable:
            value.setdefault('author', portable['author'])
    value.setdefault('keywords', (portable or {}).get('keywords', []))
    value.setdefault('skills', './skills')
    if isinstance(value.get('skills'), str):
        value['skills'] = value['skills'].rstrip('/')
    if value.get('interface', {}).get('defaultPrompt', 'absent') is None:
        value['interface'].pop('defaultPrompt')
    return value


def markdown_pair(source, built, rule, export, files):
    """Only normalize documented external relative links into pinned GitHub links."""
    allowed = {}
    def original(match):
        link = match[1]
        if ':' in link or link.startswith('#'):
            return match[0]
        clean, _, anchor = link.partition('#')
        if posixpath.normpath(posixpath.join(posixpath.dirname(export), clean)) in files:
            return match[0]
        path = posixpath.normpath(posixpath.join(posixpath.dirname(rule['source_path']), clean))
        if path.startswith('../'):
            return match[0]
        token = 'github://' + rule['repository'] + '/' + path + ('#' + anchor if anchor else '')
        allowed[(rule['repository'], path, anchor)] = token
        return '](' + token + ')'
    normalized = re.sub(r'\]\(([^\s)]+)\)', original, source)
    def exported(match):
        parsed = urlparse(match[1])
        parts = unquote(parsed.path).strip('/').split('/')
        if parsed.scheme != 'https' or parsed.netloc != 'github.com' or len(parts) < 5 or parts[2] != 'blob' or not re.fullmatch(r'[0-9a-f]{40}', parts[3]):
            return match[0]
        token = allowed.get(('/'.join(parts[:2]), '/'.join(parts[4:]), parsed.fragment))
        return '](' + token + ')' if token else match[0]
    return normalized.encode(), re.sub(r'\]\(([^\s)]+)\)', exported, built).encode()


def read_bundle(data):
    if data[:2] == b'PK':
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise ValueError('Duplicate ZIP paths')
            return {n: archive.read(n) for n in names if not n.endswith('/')}
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        members = [m for m in archive.getmembers() if m.isfile()]
        if len(members) != len({m.name for m in members}) or any(m.issym() or m.islnk() for m in archive):
            raise ValueError('Duplicate or linked archive entries')
        return {m.name.removeprefix('./'): archive.extractfile(m).read() for m in members}


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.DEVNULL)


def refresh(repository, cache):
    target = cache / repository.split('/')[-1]
    if not (target / '.git').exists():
        subprocess.run(['git', 'clone', '--quiet', '--depth=1', 'git@github.com:' + repository + '.git', str(target)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    subprocess.run(['git', '-C', str(target), 'fetch', '--quiet', 'git@github.com:' + repository + '.git', 'main'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    return repository, (target, git(target, 'rev-parse', 'FETCH_HEAD').decode().strip())


def profile_for(row):
    return digest(json_bytes({'files':row['files'], 'generated':row['generated_files'], 'normalizer':1}))


def read_catalog(contract, inputs, artifact_data):
    if artifact_data is None:
        headers = {'Cache-Control':'no-cache', 'Accept':'application/json', 'User-Agent':'SkillChecks/1.0'}
        if inputs.get('artifact_token'):
            headers['OAI-Sites-Authorization'] = 'Bearer ' + inputs['artifact_token'].removeprefix('Bearer ')
        request = urllib.request.Request(contract['artifact']['url'] + contract['artifact']['probe'], headers=headers)
        with urllib.request.urlopen(request, timeout=60) as response:
            artifact_data = json.load(response)
    if artifact_data.get('schema_version') != 1:
        raise ValueError('Unknown deployed catalog probe format')
    rows = artifact_data['plugins']
    artifact = {p['name']: p for p in rows}
    if len(rows) != len(artifact) or set(artifact) != {r['name'] for r in contract['plugins']}:
        raise ValueError('Deployed catalog plugin inventory differs')
    return artifact


def reuse_verified_revisions(contract, observation, inputs, previous, artifact, repos):
    """Reuse content hashes only after fresh reads of both immutable identities."""
    revisions = inputs['source_revisions']
    previous = previous or {}
    if set(revisions) != repos or revisions != previous.get('source_revisions'):
        observation['unavailable'].append('A GitHub revision changed or is unverified; a full source capture is required.')
        return observation
    if any(not re.fullmatch(r'[0-9a-f]{40}', revision) for revision in revisions.values()):
        observation['unavailable'].append('GitHub revision evidence is invalid.')
        return observation
    old = {p['name']:p for p in previous.get('plugins', [])}
    supplied = {p['name']:p['plugin'] for p in inputs.get('plugins', [])}
    observation['source_revisions'] = revisions
    for row in contract['plugins']:
        try:
            saved = json.loads(json.dumps(old[row['name']]))
            current = supplied[row['name']]
            if saved['built']['release_id'] != current['current_release_id'] or saved['built']['profile'] != profile_for(row):
                raise ValueError('Changed release or comparison rules')
            if saved['source']['commit'] != revisions[row['repository']]:
                raise ValueError('Source evidence is for a different revision')
            for key in ('plugin_id', 'version', 'scope', 'discoverability'):
                saved['built'][key] = current[key]
            saved['artifact'] = artifact[row['name']]
            observation['plugins'].append(saved)
        except (KeyError, TypeError, ValueError):
            observation['unavailable'].append('A full current source and archive capture is required for ' + row['name'])
    return observation


def capture(contract, inputs, cache, previous=None, artifact_data=None):
    observation = {'schema_version': 1, 'checked_at': datetime.now(timezone.utc).isoformat(), 'unavailable': [], 'plugins': []}
    repos = {r['repository'] for r in contract['plugins']}
    repos.update(rule['repository'] for r in contract['plugins'] for rule in r['files'].values())
    try:
        artifact = read_catalog(contract, inputs, artifact_data)
    except (OSError, ValueError, KeyError, TypeError):
        observation['unavailable'].append('Cannot verify the deployed catalog probe')
        return observation
    if 'source_revisions' in inputs:
        return reuse_verified_revisions(contract, observation, inputs, previous, artifact, repos)
    contexts = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(refresh, repo, cache): repo for repo in repos}
        for future, repo in futures.items():
            try:
                name, context = future.result()
                contexts[name] = context
            except (OSError, ValueError, subprocess.SubprocessError):
                observation['unavailable'].append('Cannot verify current GitHub source: ' + repo)
    observation['source_revisions'] = {name:context[1] for name, context in contexts.items()}
    metadata = {p['name']: p for p in inputs.get('plugins', [])}
    old = {p['name']: p for p in (previous or {}).get('plugins', [])}
    for row in contract['plugins']:
        try:
            supplied = metadata[row['name']]
            plugin = supplied['plugin']
            if plugin['plugin_id'] != row['plugin_id']:
                raise ValueError('Connector identity mismatch')
            repo, commit = contexts[row['repository']]
            root = '' if row['package_root'] == '.' else row['package_root'] + '/'
            portable = json.loads(git(repo, 'show', commit + ':' + root + 'plugin.json'))
            source_files = {}
            source_content = {}
            for path, rule in row['files'].items():
                source_repo, revision = contexts[rule['repository']]
                raw = git(source_repo, 'show', revision + ':' + rule['source_path'])
                source_content[path] = raw
                if rule['mode'] == 'json':
                    raw = json_bytes(json.loads(raw))
                elif rule['mode'] == 'compatibility':
                    raw = json_bytes(compatibility(json.loads(raw), portable))
                elif rule['mode'] == 'markdown-links':
                    raw = markdown_pair(raw.decode(), '', rule, path, row['files'])[0]
                source_files[path] = digest(raw)
            cached = old.get(row['name'], {}).get('built')
            profile = profile_for(row)
            if cached and cached.get('release_id') == plugin['current_release_id'] and cached.get('profile') == profile:
                built = json.loads(json.dumps(cached))
                for key in ('version', 'plugin_id', 'scope', 'discoverability'):
                    built[key] = plugin[key]
                errors = list(built.get('errors', []))
            else:
                if supplied.get('bundle_path'):
                    if supplied.get('bundle_release_id') != plugin['current_release_id']:
                        raise ValueError('Local archive receipt is for another release')
                    data = Path(supplied['bundle_path']).read_bytes()
                else:
                    url = urlparse(supplied['download_url'])
                    if url.scheme != 'https' or not url.hostname.endswith('.oaiusercontent.com'):
                        raise ValueError('Archive URL is not a connector-provided download')
                    with urllib.request.urlopen(supplied['download_url'], timeout=120) as response:
                        data = response.read()
                bundle = read_bundle(data)
                errors = []
                files = {}
                for path, raw in bundle.items():
                    if path in row['generated_files']:
                        if path == 'SOURCE-OF-TRUTH.json' and json.loads(raw).get('version') != portable['version']:
                            errors.append('Current provenance version differs')
                        continue
                    rule = row['files'].get(path)
                    if rule and rule['mode'] == 'json':
                        raw = json_bytes(json.loads(raw))
                    elif rule and rule['mode'] == 'compatibility':
                        raw = json_bytes(compatibility(json.loads(raw)))
                    elif rule and rule['mode'] == 'markdown-links':
                        raw = markdown_pair(source_content[path].decode(), raw.decode(), rule, path, row['files'])[1]
                    files[path] = digest(raw)
                manifest = json.loads(bundle['plugin.json'])
                if manifest['version'] != plugin['version']:
                    errors.append('Saved archive and connector versions differ')
                built = {k:plugin[k] for k in ('plugin_id', 'version', 'scope', 'discoverability')}
                built.update(release_id=plugin['current_release_id'], files=files,
                             skills=sorted(p for p in bundle if re.fullmatch(r'skills/[^/]+/SKILL.md', p)),
                             profile=profile, errors=errors)
            source_skills = [p[len(root):] for p in git(repo, 'ls-tree', '-r', '--name-only', commit, '--', root + 'skills').decode().splitlines() if re.fullmatch(r'skills/[^/]+/SKILL.md', p[len(root):])]
            observation['plugins'].append({'name':row['name'], 'source':{'version':portable['version'], 'commit':commit, 'branch':'main', 'files':source_files, 'skills':source_skills}, 'built':built, 'artifact':artifact[row['name']], 'errors':errors})
        except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.SubprocessError, tarfile.TarError, zipfile.BadZipFile):
            observation['unavailable'].append('Cannot verify plugin source/build/catalog evidence: ' + row['name'])
    return observation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', type=Path, default=ROOT / 'maintenance/plugin-sync.json')
    parser.add_argument('--inputs', type=Path)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--previous', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text())
    if validate_contract(contract):
        raise SystemExit('Invalid sync contract')
    if args.inputs:
        inputs = json.loads(args.inputs.read_text())
    else:
        if sys.stdin.isatty():
            import termios
            settings = termios.tcgetattr(0)
            settings[3] &= ~(termios.ECHO | termios.ICANON)
            termios.tcsetattr(0, termios.TCSANOW, settings)
        print('Ready for sync inputs on hidden stdin.', flush=True)
        inputs = json.loads(sys.stdin.readline())
    args.cache.mkdir(parents=True, exist_ok=True)
    previous = json.loads(args.previous.read_text()) if args.previous else None
    observation = capture(contract, inputs, args.cache, previous)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(observation, separators=(',', ':')) + '\n')
    result = check(contract, observation)
    args.output.with_suffix('.report.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Live sync: ' + result['status'] + '; plugins checked: ' + str(result['plugins_checked']))
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
