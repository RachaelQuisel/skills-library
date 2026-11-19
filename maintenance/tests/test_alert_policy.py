import datetime as dt
import importlib.util
import json
import pytest
from pathlib import Path

root = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location('alert_policy', root / 'alert_policy.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
# These original cases isolate workflow behavior. Live sync is covered below.
POLICY = dict(json.loads((root / 'notification-policy.json').read_text()), require_plugin_sync=False)
NOW = dt.datetime(2026, 10, 11, 16, tzinfo=dt.timezone.utc)

def run(**overrides):
    r = dict(id=1, run_attempt=1, path=POLICY['workflow_path'], head_branch='main',
             created_at='2026-10-11T15:30:00Z', updated_at='2026-10-11T15:35:00Z', status='completed', conclusion='success', html_url='https://example.invalid/run/1')
    r.update(overrides)
    return r

def test_recent_success_stays_quiet():
    assert m.classify([run()], POLICY, NOW) == []

def test_new_failure_is_reported_even_with_previous_success():
    alerts = m.classify([run(), run(id=2, conclusion='failure')], POLICY, NOW)
    assert alerts[0]['kind'] == 'failed'
    assert alerts[0]['key'] == '2:1'

def test_no_runs_is_not_healthy():
    assert m.classify([], POLICY, NOW)[0]['kind'] == 'missing-success'

def test_eight_day_old_success_expires():
    r = run(created_at='2026-10-03T15:00:00Z', updated_at='2026-10-03T16:00:00Z')
    assert m.classify([r], POLICY, NOW)[0]['kind'] == 'missing-success'

def test_stuck_run_is_reported():
    r = run(status='in_progress', conclusion=None, created_at='2026-10-11T14:00:00Z')
    assert 'stuck' in [a['kind'] for a in m.classify([r, run(id=2)], POLICY, NOW)]

def test_other_workflow_or_branch_does_not_hide_missing_run():
    assert m.classify([run(path='other.yml'), run(head_branch='feature')], POLICY, NOW)[0]['kind'] == 'missing-success'

def test_access_failure_is_explicit():
    assert m.classify([], POLICY, NOW, access_ok=False)[0]['kind'] == 'unavailable'

def test_skipped_run_is_not_success():
    assert m.classify([run(conclusion='skipped')], POLICY, NOW)[0]['kind'] == 'missing-success'

def test_invalid_timestamp_is_not_success():
    assert m.classify([run(updated_at='not-a-date')], POLICY, NOW)[0]['kind'] == 'unknown'


def delivered_opening():
    state = m.plan([run(conclusion='failure')], POLICY, m.new_state(), NOW)
    event_id = next(iter(state['events']))
    state = m.claim_event(state, event_id, 'test-owner')
    return m.acknowledge(state, event_id, 'https://example.invalid/verified-message')


def test_later_success_supersedes_old_failed_runs():
    assert m.classify([run(conclusion='failure'), run(id=2)], POLICY, NOW) == []


def test_same_problem_on_new_runs_and_restarts_does_not_alert_again():
    state = json.loads(json.dumps(delivered_opening()))
    state = m.plan([run(id=2, conclusion='failure')], POLICY, state, NOW)
    state = m.plan([run(id=3, run_attempt=2, conclusion='failure')], POLICY, state, NOW)
    assert len(state['events']) == 1
    assert next(iter(state['events'].values()))['status'] == 'delivered'


def test_recovery_is_sent_once_and_recurrence_is_a_new_episode():
    state = m.plan([run(id=2)], POLICY, delivered_opening(), NOW)
    recovered = [e for e in state['events'].values() if e['phase'] == 'fixed']
    assert len(recovered) == 1
    key = recovered[0]['event_id']
    state = m.acknowledge(m.claim_event(state, key, 'test-owner'), key, 'verified-recovery')
    state = m.plan([run(id=3)], POLICY, state, NOW)
    assert len(state['events']) == 2
    state = m.plan([run(id=4, conclusion='failure')], POLICY, state, NOW)
    assert len(state['events']) == 3
    assert len([e for e in state['events'].values() if e['status'] == 'pending']) == 1


def test_access_loss_cannot_resolve_an_open_problem():
    state = m.plan([], POLICY, delivered_opening(), NOW, access_ok=False)
    assert all(e['phase'] != 'fixed' for e in state['events'].values())
    assert state['problems']['workflow-result']['open']


def test_uncertain_delivery_is_not_sent_again_or_reported_as_fixed():
    state = m.plan([run(conclusion='failure')], POLICY, m.new_state(), NOW)
    key = next(iter(state['events']))
    state = m.claim_event(state, key, 'first-owner')
    with pytest.raises(ValueError):
        m.claim_event(state, key, 'second-owner')
    state = m.plan([run(id=2)], POLICY, state, NOW)
    assert len(state['events']) == 1
    assert state['events'][key]['status'] == 'claimed'


def test_unreported_problem_resolving_does_not_send_a_recovery():
    state = m.plan([run(conclusion='failure')], POLICY, m.new_state(), NOW)
    state = m.plan([run(id=2)], POLICY, state, NOW)
    assert [e['status'] for e in state['events'].values()] == ['cancelled']


def test_missing_or_stale_state_fails_closed():
    with pytest.raises(ValueError):
        m.plan([run()], POLICY, {}, NOW)
    with pytest.raises(ValueError):
        m.plan([run()], POLICY, dict(m.new_state(), latest_run_id=2), NOW)


def test_delivery_requires_a_verified_receipt():
    state = m.plan([run(conclusion='failure')], POLICY, m.new_state(), NOW)
    key = next(iter(state['events']))
    with pytest.raises(ValueError):
        m.acknowledge(state, key, 'receipt-without-claim')
    with pytest.raises(ValueError):
        m.acknowledge(m.claim_event(state, key, 'owner'), key, '')


def test_concrete_problem_keys_survive_changed_run_ids():
    report = {'source_commit': 'abc', 'run_attempt': 1, 'release': {'status': 'passed'},
              'maintenance': {'inventory_errors': ['Unregistered skill: example'], 'suites': {}}}
    first = m.classify([run(conclusion='failure', head_sha='abc')], POLICY, NOW, reports={'1': report})
    later = m.classify([run(id=2, conclusion='failure', head_sha='abc')], POLICY, NOW, reports={'2': report})
    assert first[0]['problem_key'] == later[0]['problem_key']
    assert first[0]['problem_key'].startswith('inventory:')


def test_wrong_commit_or_attempt_report_is_not_trusted():
    report = {'source_commit': 'wrong', 'run_attempt': 1, 'release': {'status': 'passed'}}
    alerts = m.classify([run(conclusion='failure', head_sha='actual')], POLICY, NOW, reports={'1': report})
    assert alerts[0]['problem_key'] == 'workflow-result'


def test_recovery_link_must_be_a_completed_success():
    state = m.plan([run(id=2), run(id=3, status='in_progress', conclusion=None)], POLICY, delivered_opening(), NOW)
    fixed = [e for e in state['events'].values() if e['phase'] == 'fixed']
    assert fixed[0]['evidence']['run_id'] == 2


def sync_result(problems=(), healthy=()):
    return {'schema_version':1,'checked_at':NOW.isoformat(),'status':'failed' if problems else 'passed',
            'problems':[{'kind':'sync','problem_key':'sync:'+p,'message':'Drift '+p} for p in problems],
            'healthy_keys':['sync:'+p for p in healthy], 'plugins_checked':28}


def test_required_sync_cannot_be_skipped_or_recover_without_evidence():
    policy=dict(POLICY,require_plugin_sync=True)
    alerts=m.classify([run()],policy,NOW)
    assert [a['problem_key'] for a in alerts]==['sync:observation']
    stale=sync_result(healthy=['example'])
    stale['checked_at']='2026-10-11T01:00:00Z'
    assert m.classify([run()],policy,NOW,sync_report=stale)[0]['problem_key']=='sync:observation'


def test_sync_repeats_stay_quiet_and_one_plugin_can_recover_while_another_fails():
    policy=dict(POLICY,require_plugin_sync=True)
    state=m.plan([run()],policy,m.new_state(),NOW,sync_report=sync_result(['one','two']))
    for event in list(state['events']):
        state=m.acknowledge(m.claim_event(state,event,'first'),event,'verified:'+event)
    state=m.plan([run(id=2)],policy,state,NOW,sync_report=sync_result(['one','two']))
    assert len(state['events'])==2
    state=m.plan([run(id=3)],policy,state,NOW,sync_report=sync_result(['two'],['one']))
    fixed=[e for e in state['events'].values() if e['phase']=='fixed']
    assert len(fixed)==1 and fixed[0]['problem_key']=='sync:one'
    state=m.plan([run(id=4)],policy,state,NOW,sync_report=sync_result(['two'],['one']))
    assert len(state['events'])==3


def test_access_loss_cannot_resolve_a_reported_sync_problem():
    policy=dict(POLICY,require_plugin_sync=True)
    state=m.plan([run()],policy,m.new_state(),NOW,sync_report=sync_result(['one']))
    event=next(iter(state['events']))
    state=m.acknowledge(m.claim_event(state,event,'first'),event,'verified')
    state=m.plan([run(id=2)],policy,state,NOW,sync_report=None)
    assert state['problems']['sync:one']['open']
    assert not any(e['phase']=='fixed' for e in state['events'].values())


def test_same_sync_problem_in_ci_and_live_observation_is_one_alert():
    policy=dict(POLICY,require_plugin_sync=True)
    report={'source_commit':'abc','run_attempt':1,'release':{'status':'passed'},
            'maintenance':{'inventory_errors':[],'suites':{}},'plugin_sync':sync_result(['one'])}
    alerts=m.classify([run(head_sha='abc',conclusion='failure')],policy,NOW,
                      reports={'1':report},sync_report=sync_result(['one']))
    assert [a['problem_key'] for a in alerts]==['sync:one']
