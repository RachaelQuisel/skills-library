"""Compare fresh GitHub, saved-plugin, and deployed-catalog evidence. Never publish."""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def validate_contract(contract):
    errors = []
    if contract.get('schema_version') != 1 or not contract.get('plugins'):
        return ['Missing plugin sync contract.']
    rows = contract['plugins']
    for key in ('name', 'plugin_id', 'catalog_id'):
        values = [row.get(key) for row in rows]
        if None in values or len(values) != len(set(values)):
            errors.append('Missing or duplicate ' + key)
    for row in rows:
        if not re.fullmatch(r'RachaelQuisel/[A-Za-z0-9_.-]+', row.get('repository', '')):
            errors.append('Invalid repository: ' + row['name'])
        for path in [row.get('package_root', ''), *row.get('files', {})]:
            if not path or path.startswith('/') or '..' in Path(path).parts:
                errors.append('Unsafe package path: ' + row['name'])
        if 'plugin.json' not in row.get('files', {}):
            errors.append('Missing portable manifest rule: ' + row['name'])
    return errors


def problem(key, messages):
    return {'kind': 'sync', 'problem_key': key, 'message': '; '.join(messages), 'details': messages}


def check(contract, observation, now=None):
    now = now or datetime.now(timezone.utc)
    result = {'schema_version': 1, 'checked_at': now.isoformat(), 'status': 'unknown',
              'problems': [], 'healthy_keys': [], 'plugins_checked': 0}
    errors = validate_contract(contract)
    if errors:
        result['problems'] = [problem('sync:contract', errors)]
        return result
    try:
        stamp = datetime.fromisoformat(observation['checked_at'].replace('Z', '+00:00'))
        if stamp.tzinfo is None or stamp > now + timedelta(minutes=5):
            raise ValueError('Invalid observation time')
        if now - stamp > timedelta(hours=contract['max_observation_age_hours']):
            raise ValueError('Observation is stale')
        if observation.get('schema_version') != 1:
            raise ValueError('Unknown observation format')
        if observation.get('unavailable'):
            result['problems'] = [problem('sync:access', observation['unavailable'])]
            return result
        captures = observation['plugins']
        names = [row['name'] for row in captures]
        if len(names) != len(set(names)) or set(names) != {r['name'] for r in contract['plugins']}:
            raise ValueError('Observation does not cover every registered plugin exactly once')
    except (KeyError, TypeError, ValueError) as exc:
        result['problems'] = [problem('sync:observation', [str(exc)])]
        return result
    by_name = {r['name']: r for r in captures}
    for row in contract['plugins']:
        key = 'sync:' + row['name']
        errors = []
        try:
            capture = by_name[row['name']]
            source, built, artifact = (capture[k] for k in ('source', 'built', 'artifact'))
            errors.extend(capture.get('errors', []))
            version = source['version']
            if not re.fullmatch(r'[1-9]\d*\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?', version):
                errors.append('Canonical version must start at 1.0.0 or higher')
            if built['plugin_id'] != row['plugin_id'] or built['scope'] != 'USER' or built['discoverability'] != 'PRIVATE':
                errors.append('Saved plugin identity or audience differs')
            if not built['release_id'] or not re.fullmatch(r'[0-9a-f]{40}', source['commit']):
                errors.append('Missing immutable release or source evidence')
            if built['version'] != version or artifact['version'] != version:
                errors.append('GitHub, saved build, and catalog versions differ')
            expected, actual = source['files'], built['files']
            if not expected or not actual:
                raise ValueError('File evidence is empty')
            if set(expected) != set(row['files']):
                errors.append('Canonical file evidence does not cover the full package contract')
            for path in sorted(expected.keys() - actual.keys()):
                errors.append('Missing built file: ' + path)
            for path in sorted(actual.keys() - expected.keys()):
                errors.append('Unmapped built file: ' + path)
            for path in sorted(expected.keys() & actual.keys()):
                if not re.fullmatch(r'[0-9a-f]{64}', expected[path]) or expected[path] != actual[path]:
                    errors.append('Built file differs from canonical source: ' + path)
            if sorted(source['skills']) != sorted(built['skills']):
                errors.append('Bundled skill inventory differs')
            if artifact['id'] != row['catalog_id'] or artifact['name'] != row['name']:
                errors.append('Catalog identity differs')
            suffix = '' if row['package_root'] == '.' else '/tree/' + source['branch'] + '/' + row['package_root']
            github = 'https://github.com/' + row['repository'] + suffix
            if artifact['githubUrl'] != github:
                errors.append('Primary catalog link does not open the full plugin source')
            chatgpt = []
            for platform in artifact['platformVersions']:
                if platform['version'] != version:
                    errors.append('Catalog platform version differs: ' + platform['platform'])
                url = platform['url']
                if url.startswith('https://github.com/'):
                    root = '' if row['package_root'] == '.' else '/' + row['package_root']
                    pattern = re.escape('https://github.com/' + row['repository'] + '/tree/') + r'[0-9a-f]{40}' + re.escape(root) + r'/?'
                    if not re.fullmatch(pattern, url):
                        errors.append('Catalog revision link does not open the full plugin source')
                if platform['platform'] == 'ChatGPT' and url.startswith('https://chatgpt.com/plugins/'):
                    chatgpt.append(url)
            if chatgpt != ['https://chatgpt.com/plugins/' + row['plugin_id']]:
                errors.append('Catalog does not link to the existing saved plugin')
            result['plugins_checked'] += 1
        except (KeyError, TypeError, ValueError) as exc:
            errors.append('Incomplete verification: ' + str(exc))
        if errors:
            alert = problem(key, list(dict.fromkeys(errors)))
            alert['url'] = 'https://github.com/' + row['repository'] + ('' if row['package_root'] == '.' else '/tree/main/' + row['package_root'])
            result['problems'].append(alert)
        else:
            result['healthy_keys'].append(key)
    result['status'] = 'failed' if result['problems'] else 'passed'
    if result['status'] == 'passed':
        result['healthy_keys'] += ['sync:access', 'sync:observation', 'sync:contract']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', type=Path, default=ROOT / 'maintenance/plugin-sync.json')
    parser.add_argument('--observation', type=Path)
    parser.add_argument('--contract-only', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text())
    if args.contract_only:
        errors = validate_contract(contract)
        result = {'status': 'failed' if errors else 'passed', 'errors': errors,
                  'coverage': 'Contract structure only; no live verification'}
    else:
        try:
            observation = json.loads(args.observation.read_text()) if args.observation else {}
        except (OSError, ValueError):
            observation = {}
        result = check(contract, observation)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('Plugin source/build/catalog sync: ' + result['status'])
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
