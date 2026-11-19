"""Plan durable, once-per-problem alerts. No network or notification side effects."""
import argparse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

def timestamp(value):
    stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if stamp.tzinfo is None:
        raise ValueError('Timestamp requires a timezone')
    return stamp

def problem_key(kind, detail=''):
    return kind + ':' + hashlib.sha256(detail.encode()).hexdigest()[:16]


def failure_details(run, reports):
    report = (reports or {}).get(str(run['id']))
    details = {'key': str(run['id']) + ':' + str(run.get('run_attempt', 1)),
               'run_id': run['id'], 'url': run.get('html_url'), 'kind': 'failed'}
    if (not report or report.get('source_commit') != run.get('head_sha') or
            report.get('run_attempt') != run.get('run_attempt', 1)):
        return [dict(details, problem_key='workflow-result', conclusion=run['conclusion'])]
    alerts = []
    release = report.get('release', {})
    if release.get('status') != 'passed':
        for message in release.get('errors') or ['Release check could not complete.']:
            alerts.append(dict(details, problem_key=problem_key('release', message), message=message))
    maintenance = report.get('maintenance')
    if not maintenance:
        alerts.append(dict(details, problem_key='maintenance-evidence', message='Maintenance evidence is unavailable.'))
    else:
        for message in maintenance.get('inventory_errors', []):
            alerts.append(dict(details, problem_key=problem_key('inventory', message), message=message))
        for name, suite in maintenance.get('suites', {}).items():
            if suite.get('status') == 'passed':
                continue
            cases = suite.get('failures', []) + suite.get('missing_regressions', []) + suite.get('skipped', [])
            for case in cases or [name + ': check could not complete']:
                alerts.append(dict(details, problem_key=problem_key('test', name + ':' + case), message=case))
    sync = report.get('plugin_sync')
    if sync and sync.get('status') != 'passed':
        alerts.extend(dict(details, **p) for p in sync.get('problems', []))
    return alerts or [dict(details, problem_key='workflow-result', conclusion=run['conclusion'])]


def sync_alerts(sync_report, required, now):
    if sync_report is None and not required:
        return [], []
    try:
        checked = timestamp(sync_report['checked_at'])
        if checked > now + timedelta(minutes=5) or now - checked > timedelta(hours=3):
            raise ValueError('Stale sync result')
        if sync_report['status'] not in ('passed', 'failed', 'unknown'):
            raise ValueError('Unknown sync result')
        problems = sync_report['problems']
        healthy = sync_report['healthy_keys']
        if not isinstance(problems, list) or not isinstance(healthy, list):
            raise ValueError('Invalid sync evidence')
        if sync_report['status'] != 'passed' and not problems:
            raise ValueError('Missing sync problem evidence')
        if sync_report['status'] == 'passed' and problems:
            raise ValueError('Conflicting sync result')
        if any(not p['problem_key'].startswith('sync:') for p in problems):
            raise ValueError('Invalid sync problem key')
        return problems, healthy if sync_report['status'] != 'unknown' else []
    except (TypeError, KeyError, ValueError, AttributeError):
        return [{'kind':'sync', 'problem_key':'sync:observation',
                 'message':'Fresh source/build/catalog verification is unavailable.'}], []


def classify(runs, policy, now=None, access_ok=True, reports=None, sync_report=None):
    now = now or datetime.now(timezone.utc)
    if not access_ok:
        return [{'kind': 'unavailable', 'key': 'github-access', 'problem_key': 'github-access', 'message': 'GitHub could not be checked.'}]
    alerts = []
    valid = []
    for run in runs:
        if run.get('path') != policy['workflow_path'] or run.get('head_branch') != policy['branch']:
            continue
        try:
            created = timestamp(run['created_at'])
            updated = timestamp(run.get('updated_at', run['created_at']))
            if created > now or updated > now:
                raise ValueError('Future timestamp')
        except (KeyError, TypeError, ValueError):
            alerts.append({'kind': 'unknown', 'key': str(run.get('id')), 'problem_key': 'run-metadata', 'message': 'Run timestamps are missing or invalid.'})
            continue
        valid.append((created, int(run['id']), int(run.get('run_attempt', 1)), updated, run))
    valid.sort(key=lambda item: item[:3], reverse=True)
    completed = [item for item in valid if item[4].get('status') == 'completed'
                 and item[4].get('conclusion') not in ('skipped', 'neutral')]
    latest = completed[0] if completed else None
    if latest:
        run = latest[4]
        if run.get('conclusion') in policy['failure_conclusions']:
            alerts += failure_details(run, reports)
        elif run.get('conclusion') != 'success':
            alerts.append({'kind': 'unknown', 'key': str(run['id']), 'problem_key': 'workflow-result',
                           'message': 'Completed run has no recognized result.'})
    for created, run_id, attempt, updated, run in valid:
        if run.get('status') != 'completed' and now - created > timedelta(minutes=policy['unfinished_run_max_age_minutes']):
            alerts.append({'kind': 'stuck', 'key': f'{run_id}:{attempt}', 'problem_key': 'workflow-stuck',
                           'run_id': run_id, 'url': run.get('html_url')})
    successful = [item[3] for item in valid if item[4].get('status') == 'completed' and item[4].get('conclusion') == 'success']
    if not successful or now - max(successful) >= timedelta(days=policy['successful_run_max_age_days']):
        # A known failed run already explains why this workflow is not healthy.
        if not any(a['kind'] == 'failed' for a in alerts) and not (latest and latest[4].get('conclusion') in policy['failure_conclusions']):
            alerts.append({'kind': 'missing-success', 'key': 'workflow-freshness', 'problem_key': 'workflow-freshness',
                           'message': 'No successful run was found within the required window.'})
    sync, _ = sync_alerts(sync_report, policy.get('require_plugin_sync', False), now)
    if sync_report and sync_report.get('status') in ('passed', 'failed') and not any(p['problem_key']=='sync:observation' for p in sync):
        alerts = [a for a in alerts if not a['problem_key'].startswith('sync:')]
    # An Actions report and the hourly observer describe the same sync problem.
    return list({a['problem_key']:a for a in [*alerts, *sync]}.values())


def new_state():
    return {'schema_version': 1, 'observed_at': None, 'latest_run_id': 0, 'problems': {}, 'events': {}}


def plan(runs, policy, state, now=None, access_ok=True, reports=None, sync_report=None):
    now = now or datetime.now(timezone.utc)
    if state.get('schema_version') != 1 or not isinstance(state.get('events'), dict) or not isinstance(state.get('problems'), dict):
        raise ValueError('Missing or invalid durable alert state; do not reset it.')
    if state.get('observed_at') and timestamp(state['observed_at']) > now:
        raise ValueError('Refusing an older observation.')
    relevant = [r for r in runs if r.get('path') == policy['workflow_path'] and r.get('head_branch') == policy['branch']]
    latest_id = max((int(r['id']) for r in relevant), default=0)
    if access_ok and latest_id < state.get('latest_run_id', 0):
        raise ValueError('Run history is incomplete or older than saved state.')
    result = deepcopy(state)
    result['observed_at'] = now.isoformat()
    result['latest_run_id'] = max(latest_id, state.get('latest_run_id', 0))
    alerts = classify(runs, policy, now, access_ok, reports, sync_report)
    _, healthy_sync = sync_alerts(sync_report, policy.get('require_plugin_sync', False), now)
    for alert in alerts:
        key = alert['problem_key']
        previous = result['problems'].get(key, {})
        if previous.get('open'):
            previous['latest_evidence'] = alert
            continue
        sequence = previous.get('sequence', 0) + 1
        event_id = problem_key('open', f'{key}:{sequence}')
        result['problems'][key] = {'open': True, 'sequence': sequence, 'opened_at': now.isoformat(),
                                    'latest_evidence': alert, 'opened_event': event_id}
        result['events'][event_id] = {'event_id': event_id, 'problem_key': key, 'phase': 'opened',
                                      'status': 'pending', 'evidence': alert, 'created_at': now.isoformat()}
    # Each sync problem requires fresh evidence for that same plugin. Workflow
    # problems retain the existing fully-healthy recovery requirement.
    active_keys = {a['problem_key'] for a in alerts}
    for key, problem in result['problems'].items():
        can_recover = access_ok and key not in active_keys and (key in healthy_sync if key.startswith('sync:') else not alerts)
        if can_recover:
            if not problem['open']:
                continue
            opening = result['events'][problem['opened_event']]
            if opening['status'] == 'claimed':
                continue  # Reconcile uncertain delivery before announcing recovery.
            problem['open'] = False
            problem['resolved_at'] = now.isoformat()
            if opening['status'] == 'pending':
                opening['status'] = 'cancelled'  # No alert was delivered, so no recovery notice is needed.
                continue
            if opening['status'] != 'delivered':
                continue
            event_id = problem_key('fixed', f"{key}:{problem['sequence']}")
            evidence_run = max((r for r in relevant if r.get('status') == 'completed'
                                and r.get('conclusion') == 'success'), key=lambda r: int(r['id']), default=None)
            result['events'][event_id] = {'event_id': event_id, 'problem_key': key, 'phase': 'fixed',
                'status': 'pending', 'created_at': now.isoformat(),
                'evidence': {'run_id': evidence_run['id'] if evidence_run else None,
                             'url': problem['latest_evidence'].get('url') if key.startswith('sync:') else evidence_run.get('html_url') if evidence_run else None,
                             'sync_checked_at':sync_report.get('checked_at') if sync_report else None}}
    return result


def claim_event(state, event_id, claim_id):
    result = deepcopy(state)
    event = result['events'][event_id]
    if event['status'] != 'pending' or not claim_id:
        raise ValueError('Event is already claimed, delivered, or cancelled.')
    event.update(status='claimed', claim_id=claim_id)
    return result


def acknowledge(state, event_id, receipt):
    result = deepcopy(state)
    event = result['events'][event_id]
    if event['status'] != 'claimed' or not receipt:
        raise ValueError('A claimed event and verified delivery receipt are required.')
    event.update(status='delivered', receipt=receipt)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', type=Path, required=True)
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--reports', type=Path)
    parser.add_argument('--sync-report', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--access-unavailable', action='store_true')
    args = parser.parse_args()
    read = lambda path: json.loads(path.read_text())
    result = plan(read(args.runs), read(args.policy), read(args.state),
                  access_ok=not args.access_unavailable, reports=read(args.reports) if args.reports else None,
                  sync_report=read(args.sync_report) if args.sync_report else None)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps([e for e in result['events'].values() if e['status'] == 'pending'], indent=2))


if __name__ == '__main__':
    main()
