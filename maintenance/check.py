"""Collection inventory and offline regression runner. Never certifies live APIs."""
import argparse
import datetime as dt
import json
import hashlib
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SUITES = {
    'audit-offline': ['audit-log-plugin/tests'],
    'maintenance-controls': ['maintenance/tests'],
}

def utcnow():
    return dt.datetime.now(dt.timezone.utc)

def freshness(verified_at, now=None, days=7):
    if not verified_at:
        return 'unverified'
    stamp = dt.datetime.fromisoformat(verified_at.replace('Z', '+00:00'))
    now = now or utcnow()
    if stamp.tzinfo is None or stamp > now:
        return 'invalid-evidence-date'
    return 'stale' if now - stamp >= dt.timedelta(days=days) else 'current'

# Folders that hold copies, not maintained skills: .trash keeps removed copies
# until they are emptied, and synced mirrors the claude.ai account skills.
# Skills in them are not reported as unregistered. A registered path inside
# them is still checked like any other.
UNMAINTAINED_ROOTS = ('.trash', 'synced')

def evaluate_inventory(registry, tree):
    entries = {x['path']: x for x in tree}
    actual = {p.rsplit('/', 1)[0] for p in entries if p.endswith('/SKILL.md')}
    listed = {x['id'] for x in registry['skills']}
    listed_paths = {x['path'] for x in registry['skills']}
    errors = []
    if len(listed) != len(registry['skills']):
        errors.append('Duplicate skill IDs in collection.json')
    if len(listed_paths) != len(registry['skills']):
        errors.append('Duplicate skill paths in collection.json')
    for key in sorted(actual - listed_paths):
        if key.split('/', 1)[0] in UNMAINTAINED_ROOTS:
            continue
        errors.append('Unregistered skill: ' + key)
    for s in registry['skills']:
        if s['path'] not in actual:
            errors.append('Registered skill missing: ' + s['id'])
    changed = []
    for s in registry['skills']:
        readme = s.get('readme_path', s['path'] + '/README.md')
        if readme not in entries:
            errors.append('Missing README: ' + s['id'])
        if not s.get('maintainer'):
            errors.append('Missing maintainer: ' + s['id'])
        nested = re.fullmatch(r'plugins/([^/.][^/]*)/skills/([^/]+)', s['path'])
        slug = r'[a-z0-9]+(?:-[a-z0-9]+)*'
        standalone_id = (re.fullmatch(slug, s['id']) and
                         s['path'].rsplit('/', 1)[-1] == s['id'])
        plugin_id = (nested and re.fullmatch(slug, nested[1]) and
                     re.fullmatch(slug, nested[2]) and
                     s['id'] == nested[1] + ':' + nested[2])
        if ((not standalone_id and not plugin_id) or
                (s['path'] != s['id'] and not nested) or
                any(part in ('.', '..') for part in s['path'].split('/'))):
            errors.append('Invalid skill path: ' + s['id'])
        if entries.get(s['path'], {}).get('sha') != s['baseline_tree_sha']:
            changed.append(s['id'])
    return errors, changed

def read_git_tree():
    raw = subprocess.check_output(['git', 'ls-tree', '-rz', '-t', 'HEAD'], cwd=ROOT)
    out = []
    for row in raw.split(b'\0'):
        if not row:
            continue
        info, path = row.decode().split('\t', 1)
        mode, kind, sha = info.split()
        out.append({'path': path, 'type': kind, 'sha': sha})
    return out

def junit_summary(path):
    root = ET.parse(path).getroot()
    cases = list(root.iter('testcase'))
    failures = []
    skipped = []
    for c in cases:
        key = c.get('classname', '') + '::' + c.get('name', '')
        if c.find('failure') is not None or c.find('error') is not None:
            failures.append(key)
        if c.find('skipped') is not None:
            skipped.append(key)
    return {'tests': len(cases), 'failures': failures, 'skipped': skipped}

def run_suite(name, targets, output, required):
    env = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
    collected = subprocess.run([sys.executable, '-m', 'pytest', '--collect-only', '-q', *targets],
                               cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
    nodes = {line.strip() for line in collected.stdout.splitlines() if '::' in line and not line.startswith(' ')}
    missing = sorted(set(required) - nodes)
    xml = output / (name + '.xml')
    run = subprocess.run([sys.executable, '-m', 'pytest', '-q', *targets, '--junitxml=' + str(xml)],
                         cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
    (output / (name + '.log')).write_text(run.stdout + run.stderr)
    summary = junit_summary(xml) if xml.exists() else {'tests': 0, 'failures': [], 'skipped': []}
    ok = collected.returncode == 0 and run.returncode == 0 and summary['tests'] > 0 and not missing and not summary['skipped']
    return dict(summary, status='passed' if ok else 'failed', missing_regressions=missing,
                command=[sys.executable, '-m', 'pytest', '-q', *targets], scope='offline synthetic tests only')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-tree', type=Path, help='Local validation only: a GitHub tree snapshot')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    registry = json.loads((ROOT / 'maintenance/collection.json').read_text())
    required = json.loads((ROOT / 'maintenance/regressions.json').read_text())
    tree = json.loads(args.source_tree.read_text())['tree'] if args.source_tree else read_git_tree()
    errors, changed = evaluate_inventory(registry, tree)
    suites = {}
    for name, targets in SUITES.items():
        try:
            suites[name] = run_suite(name, targets, output, required.get(name, []))
        except (OSError, ValueError, subprocess.TimeoutExpired, ET.ParseError) as exc:
            suites[name] = {'status': 'unknown', 'reason': type(exc).__name__}
    commit = json.loads(args.source_tree.read_text()).get('source_commit', 'unknown') if args.source_tree else subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    now = utcnow().isoformat()
    report = {'checked_at': now, 'source_commit': commit, 'python': platform.python_version(),
              'inventory_source': 'GitHub snapshot; test files downloaded separately' if args.source_tree else 'checked-out Git commit',
              'maintenance_file_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT / 'maintenance').rglob('*')) if p.is_file() and p.suffix in ('.py', '.json') and p.name not in ('baseline-report.json', 'releases.json')},
              'inventory_errors': errors, 'skills_changed_since_baseline': changed, 'suites': suites,
              'live_api_compatibility': 'unverified', 'agent_behavior': 'unverified',
              'upstream_review': 'manual review required; scheduled tests do not detect all API changes',
              'skills': [{'id': s['id'], 'maintainer': s['maintainer'], 'suites': s['suites'],
                          'compatibility': s['compatibility_status'],
                          'freshness': freshness(s['last_behavior_verified_at'], days=registry['freshness_days'])}
                         for s in registry['skills']]}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    lines = ['# Maintained skills check', '', 'Checked: ' + now, 'Commit: ' + commit, '',
             f"Registered skills: {len(registry['skills'])}", '',
             '**This checks inventory and offline helpers. It does not prove that every skill works with current APIs or agent models.**', '',
             '| Suite | Result | Cases |', '| --- | --- | --- |']
    for name, result in suites.items():
        lines.append(f"| {name} | {result['status']} | {result.get('tests', 0)} |")
        for failed in result.get('failures', []) + result.get('missing_regressions', []):
            lines.append('\nRecorded failure or missing case: `' + failed + '`. See the matching XML and log. Cause remains unconfirmed until inspected.\n')
    lines += ['', 'Inventory errors: ' + (', '.join(errors) or 'none'),
              'Skills changed since recorded baseline: ' + (', '.join(changed) or 'none'), '',
              'Live compatibility: unverified. Upstream documentation review: still required.',
              'Owner: RachaelQuisel. Report a problem through the skill-maintenance issue form.']
    (output / 'report.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    return 1 if errors or any(v['status'] != 'passed' for v in suites.values()) else 0

if __name__ == '__main__':
    raise SystemExit(main())
