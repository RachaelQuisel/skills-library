"""Run release and maintenance checks together, retaining both sets of evidence."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run_check(command, log, runner=subprocess.run):
    try:
        result = runner(command, cwd=ROOT, capture_output=True, text=True, timeout=480)
        output = result.stdout + result.stderr
        status = 'passed' if result.returncode == 0 else 'failed'
        code = result.returncode
    except (OSError, subprocess.TimeoutExpired) as exc:
        output, status, code = type(exc).__name__, 'unknown', None
    log.write_text(output)
    return {'status': status, 'exit_code': code, 'log': log.name,
            'errors': output.strip().splitlines() if status != 'passed' else []}


def run_checks(output, check_base=None, runner=subprocess.run, sync_observation=None):
    output.mkdir(parents=True, exist_ok=True)
    # Remove only this runner's previous report, so a failed command cannot reuse it.
    maintenance_report = output / 'maintenance' / 'report.json'
    maintenance_report.unlink(missing_ok=True)
    sync_path = output / 'plugin-sync.json'
    sync_path.unlink(missing_ok=True)
    release_command = [sys.executable, str(ROOT / 'scripts/release_sync.py')]
    if check_base:
        release_command += ['--check-base', check_base]
    release = run_check(release_command, output / 'release.log', runner)
    maintenance = run_check([sys.executable, str(ROOT / 'maintenance/check.py'),
                             '--output', str(output / 'maintenance')],
                            output / 'maintenance.log', runner)
    try:
        evidence = json.loads(maintenance_report.read_text())
        if not isinstance(evidence.get('inventory_errors'), list) or not evidence.get('suites'):
            raise ValueError('Incomplete maintenance evidence')
        if evidence['inventory_errors'] or any(s.get('status') != 'passed' for s in evidence['suites'].values()):
            maintenance['status'] = 'failed'
    except (OSError, ValueError, TypeError, AttributeError):
        evidence = None
        maintenance['status'] = 'unknown'
    command = [sys.executable, str(ROOT / 'maintenance/plugin_sync.py'), '--output', str(sync_path)]
    if sync_observation:
        command += ['--observation', str(sync_observation)]
    else:
        command += ['--contract-only']
    sync_execution = run_check(command, output / 'plugin-sync.log', runner)
    try:
        sync = json.loads(sync_path.read_text())
        if sync.get('status') not in ('passed', 'failed', 'unknown'):
            raise ValueError('Missing sync status')
        if sync_execution['status'] != 'passed' or sync['status'] != 'passed':
            sync_execution['status'] = 'failed'
    except (OSError, ValueError, TypeError, AttributeError):
        sync = {'status':'unknown', 'problems':[{'kind':'sync','problem_key':'sync:observation',
                'message':'Plugin sync check did not produce fresh evidence.'}]}
        sync_execution['status'] = 'unknown'
    ok = release['status'] == maintenance['status'] == sync_execution['status'] == 'passed'
    report = {'schema_version': 1, 'checked_at': datetime.now(timezone.utc).isoformat(),
              'run_attempt': int(os.environ.get('GITHUB_RUN_ATTEMPT', '1')),
              'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'status': 'passed' if ok else 'failed', 'release': release,
              'maintenance_execution': maintenance, 'maintenance': evidence,
              'plugin_sync': sync, 'plugin_sync_execution':sync_execution,
              'plugin_sync_scope':'Live observation' if sync_observation else 'Contract only; live sync not verified',
              'live_compatibility': 'unverified'}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    lines = ['# Skill checks', '', 'Commit: ' + report['source_commit'], '',
             '| Check | Result |', '| --- | --- |',
             '| Release versions and exports | ' + release['status'] + ' |',
             '| Skill inventory and regression tests | ' + maintenance['status'] + ' |',
             '| Plugin source/build/catalog sync | ' + sync_execution['status'] + ' |',
             '', report['plugin_sync_scope'], '']
    if evidence:
        lines += ['Registered skill paths: ' + str(len(evidence['skills'])),
                  'Inventory errors: ' + (', '.join(evidence['inventory_errors']) or 'none'), '']
        for name, suite in evidence['suites'].items():
            lines.append(f"{name}: {suite['status']}; {suite.get('tests', 0)} tests.")
    lines += ['', 'Detailed results are in the attached logs and report.json.',
              'These checks do not verify live integrations or public directory publication.']
    (output / 'report.md').write_text('\n'.join(lines) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--check-base')
    parser.add_argument('--sync-observation', type=Path)
    args = parser.parse_args()
    report = run_checks(args.output.resolve(), args.check_base, sync_observation=args.sync_observation)
    print((args.output / 'report.md').read_text())
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
