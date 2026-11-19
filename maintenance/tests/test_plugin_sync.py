import copy
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))
import plugin_sync as m
from observe_plugin_sync import capture, compatibility, markdown_pair, profile_for

NOW = datetime(2026, 11, 4, 22, tzinfo=timezone.utc)
CONTRACT = {'schema_version':1, 'max_observation_age_hours':3, 'plugins':[{
    'name':'example', 'plugin_id':'plugins_example', 'catalog_id':'catalog:example',
    'repository':'RachaelQuisel/example', 'package_root':'plugins/example',
    'files':{p:{'repository':'RachaelQuisel/example','source_path':'plugins/example/'+p,'mode':'exact'}
             for p in ['plugin.json','skills/example/SKILL.md']}, 'generated_files':[]}]}


def observed():
    files = {'plugin.json':'a'*64, 'skills/example/SKILL.md':'b'*64}
    return {'schema_version':1, 'checked_at':NOW.isoformat(), 'unavailable':[], 'plugins':[{
        'name':'example', 'source':{'version':'1.0.0', 'commit':'a'*40, 'branch':'main', 'files':files,
            'skills':['skills/example/SKILL.md']},
        'built':{'version':'1.0.0', 'plugin_id':'plugins_example', 'release_id':'release_1',
            'scope':'USER', 'discoverability':'PRIVATE', 'files':copy.deepcopy(files), 'skills':['skills/example/SKILL.md']},
        'artifact':{'id':'catalog:example', 'name':'example', 'version':'1.0.0',
            'githubUrl':'https://github.com/RachaelQuisel/example/tree/main/plugins/example',
            'platformVersions':[{'platform':'ChatGPT','version':'1.0.0','url':'https://chatgpt.com/plugins/plugins_example'},
                {'platform':'Portable','version':'1.0.0','url':'https://github.com/RachaelQuisel/example/tree/'+'a'*40+'/plugins/example'}]}}]}


def test_complete_match_is_healthy():
    assert m.check(CONTRACT, observed(), NOW)['status'] == 'passed'


@pytest.mark.parametrize('change', ['version','contents','missing','extra','skills','identity','audience','catalog','manifest-link','wrong-github'])
def test_real_drift_is_one_stable_problem_per_plugin(change):
    observation = observed()
    row = observation['plugins'][0]
    if change=='version':row['built']['version']='1.0.1'
    elif change=='contents':row['built']['files']['skills/example/SKILL.md']='c'*64
    elif change=='missing':row['built']['files'].pop('skills/example/SKILL.md')
    elif change=='extra':row['built']['files']['old-copy/SKILL.md']='c'*64
    elif change=='skills':row['built']['skills']=[]
    elif change=='identity':row['built']['plugin_id']='different'
    elif change=='audience':row['built']['discoverability']='LISTED'
    elif change=='catalog':row['artifact']['version']='1.0.1'
    elif change=='manifest-link':row['artifact']['platformVersions'][1]['url']='https://github.com/RachaelQuisel/example/blob/'+'a'*40+'/plugin.json'
    elif change=='wrong-github':row['artifact']['githubUrl']='https://github.com/RachaelQuisel/other'
    result=m.check(CONTRACT, observation, NOW)
    assert result['status']=='failed'
    assert [p['problem_key'] for p in result['problems']]==['sync:example']
    assert 'sync:example' not in result['healthy_keys']


@pytest.mark.parametrize('bad', ['stale','future','missing','duplicate','access','empty-files'])
def test_missing_evidence_never_proves_recovery(bad):
    observation=observed()
    if bad=='stale':observation['checked_at']=(NOW-timedelta(hours=4)).isoformat()
    elif bad=='future':observation['checked_at']=(NOW+timedelta(hours=1)).isoformat()
    elif bad=='missing':observation['plugins']=[]
    elif bad=='duplicate':observation['plugins']*=2
    elif bad=='access':observation['unavailable']=['Plugin Creator access unavailable']
    elif bad=='empty-files':observation['plugins'][0]['built']['files']={}
    result=m.check(CONTRACT, observation, NOW)
    assert result['status']!='passed'
    assert 'sync:example' not in result['healthy_keys']


def test_unrelated_repository_commit_does_not_create_drift():
    observation=observed()
    observation['plugins'][0]['source']['commit']='b'*40
    assert m.check(CONTRACT, observation, NOW)['status']=='passed'


def test_duplicate_identity_is_rejected():
    contract=copy.deepcopy(CONTRACT)
    contract['plugins']*=2
    assert m.validate_contract(contract)


def test_known_compatibility_defaults_preserve_metadata():
    portable={'author':{'name':'Owner'},'keywords':['one'],'extensions':{'com.openai':{'interface':{'displayName':'Example'}}}}
    source={'name':'example','skills':'./skills/'}
    built={**source,'skills':'./skills','author':{'name':'Owner'},'keywords':['one'],
           'interface':{'displayName':'Example','defaultPrompt':None}}
    assert compatibility(source, portable)==compatibility(built)
    built['interface']['displayName']='Wrong title'
    assert compatibility(source, portable)!=compatibility(built)


def test_only_documented_external_link_adaptation_is_normalized():
    rule={'repository':'RachaelQuisel/example','source_path':'plugins/example/README.md'}
    source='Read [release steps](../../RELEASING.md) and [skill](skills/example/SKILL.md).'
    built='Read [release steps](https://github.com/RachaelQuisel/example/blob/'+'a'*40+'/RELEASING.md) and [skill](skills/example/SKILL.md).'
    expected,actual=markdown_pair(source,built,rule,'README.md',CONTRACT['plugins'][0]['files'])
    assert expected==actual
    assert markdown_pair(source,built.replace('/RELEASING.md','/OTHER.md'),rule,'README.md',CONTRACT['plugins'][0]['files'])[0]!=markdown_pair(source,built.replace('/RELEASING.md','/OTHER.md'),rule,'README.md',CONTRACT['plugins'][0]['files'])[1]


@pytest.mark.parametrize('changed', [None,'source','release','rules'])
def test_hosted_capture_requires_both_fresh_immutable_identities(tmp_path, changed):
    previous=observed()
    previous['source_revisions']={'RachaelQuisel/example':'a'*40}
    record=previous['plugins'][0]
    record['built']['profile']=profile_for(CONTRACT['plugins'][0])
    inputs={'source_revisions':copy.deepcopy(previous['source_revisions']), 'plugins':[{'name':'example','plugin':{
        'plugin_id':'plugins_example','current_release_id':'release_1','scope':'USER','discoverability':'PRIVATE','version':'1.0.0'}}]}
    if changed=='source':inputs['source_revisions']['RachaelQuisel/example']='b'*40
    if changed=='release':inputs['plugins'][0]['plugin']['current_release_id']='release_2'
    if changed=='rules':record['built']['profile']='other-rules'
    captured=capture(CONTRACT, inputs, tmp_path, previous, {'schema_version':1,'plugins':[record['artifact']]})
    assert (m.check(CONTRACT,captured)['status']=='passed') is (changed is None)
