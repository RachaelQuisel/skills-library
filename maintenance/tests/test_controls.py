import datetime as dt
import importlib.util
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location('maintenance_check', Path(__file__).parents[1] / 'check.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_edit_date_does_not_count_as_verification():
    assert m.freshness(None) == 'unverified'

def test_verification_expires_at_seven_days():
    now = dt.datetime(2026, 10, 11, tzinfo=dt.timezone.utc)
    assert m.freshness('2026-10-04T00:00:00Z', now) == 'stale'
    assert m.freshness('2026-10-05T00:00:00Z', now) == 'current'
    assert m.freshness('2026-10-12T00:00:00Z', now) == 'invalid-evidence-date'

def test_inventory_detects_missing_new_and_changed_skills():
    r = {'skills': [{'id':'old','path':'old','baseline_tree_sha':'a','maintainer':'owner'}]}
    errors, changed = m.evaluate_inventory(r, [{'path':'new/SKILL.md','sha':'b'}, {'path':'old','sha':'c'}])
    assert 'Unregistered skill: new' in errors
    assert 'Registered skill missing: old' in errors
    assert changed == ['old']

def test_missing_owner_is_not_silently_accepted():
    r = {'skills':[{'id':'a','path':'a','baseline_tree_sha':'x','maintainer':''}]}
    errors, _ = m.evaluate_inventory(r, [{'path':'a','sha':'x'}, {'path':'a/SKILL.md','sha':'y'}, {'path':'a/README.md','sha':'z'}])
    assert errors == ['Missing maintainer: a']

def test_junit_distinguishes_failure_skipped_and_passed(tmp_path):
    f = tmp_path / 'results.xml'
    f.write_text('<testsuites><testsuite><testcase name="pass"/><testcase name="bad"><failure/></testcase><testcase name="skip"><skipped/></testcase></testsuite></testsuites>')
    r = m.junit_summary(f)
    assert r == {'tests':3,'failures':['::bad'],'skipped':['::skip']}

def test_deleted_regression_fails_even_when_remaining_test_passes(tmp_path):
    test = tmp_path / 'test_remaining.py'
    test.write_text('def test_ok():\n    assert True\n')
    r = m.run_suite('deleted-case', [str(test)], tmp_path, ['deleted.py::test_previous_fix'])
    assert r['status'] == 'failed'
    assert r['tests'] == 1
    assert r['missing_regressions'] == ['deleted.py::test_previous_fix']

def test_skipping_a_case_does_not_count_as_passing(tmp_path):
    test = tmp_path / 'test_skipped.py'
    test.write_text('import pytest\n@pytest.mark.skip(reason="synthetic")\ndef test_fix():\n    assert True\n')
    r = m.run_suite('skipped-case', [str(test)], tmp_path, [])
    assert r['status'] == 'failed'
    assert len(r['skipped']) == 1


def test_missing_readme_fails_inventory():
    r = {'skills':[{'id':'a','path':'a','baseline_tree_sha':'x','maintainer':'owner'}]}
    errors, _ = m.evaluate_inventory(r, [{'path':'a','sha':'x'}, {'path':'a/SKILL.md','sha':'y'}])
    assert errors == ['Missing README: a']


def test_unregistered_plugin_skill_is_not_silently_skipped():
    errors, _ = m.evaluate_inventory({'skills': []}, [
        {'path': 'plugins/example/skills/example/SKILL.md', 'sha': 'a'}])
    assert errors == ['Unregistered skill: plugins/example/skills/example']


def test_registered_plugin_skill_uses_package_readme_and_skill_hash():
    path = 'plugins/example/skills/example'
    registry = {'skills': [{'id': 'example', 'path': path,
        'readme_path': 'plugins/example/README.md',
        'baseline_tree_sha': 'old', 'maintainer': 'owner'}]}
    tree = [{'path': path, 'sha': 'new'},
            {'path': path + '/SKILL.md', 'sha': 'entry'},
            {'path': 'plugins/example/README.md', 'sha': 'docs'}]
    errors, changed = m.evaluate_inventory(registry, tree)
    assert errors == []
    assert changed == ['example']


def test_missing_nested_skill_and_package_readme_are_reported():
    registry = {'skills': [{'id': 'example',
        'path': 'plugins/example/skills/example',
        'readme_path': 'plugins/example/README.md',
        'baseline_tree_sha': 'old', 'maintainer': 'owner'}]}
    errors, _ = m.evaluate_inventory(registry, [])
    assert 'Registered skill missing: example' in errors
    assert 'Missing README: example' in errors


def test_root_and_namespaced_plugin_skill_coexist():
    path = 'plugins/example/skills/example'
    registry = {'skills': [
        {'id': 'example', 'path': 'example',
         'baseline_tree_sha': 'root', 'maintainer': 'owner'},
        {'id': 'example:example', 'path': path,
         'readme_path': 'plugins/example/README.md',
         'baseline_tree_sha': 'plugin', 'maintainer': 'owner'}]}
    tree = [
        {'path': 'example', 'sha': 'root'},
        {'path': 'example/SKILL.md', 'sha': 'root-entry'},
        {'path': 'example/README.md', 'sha': 'root-docs'},
        {'path': path, 'sha': 'plugin'},
        {'path': path + '/SKILL.md', 'sha': 'plugin-entry'},
        {'path': 'plugins/example/README.md', 'sha': 'plugin-docs'}]
    errors, changed = m.evaluate_inventory(registry, tree)
    assert errors == []
    assert changed == []
    tree[3]['sha'] = 'updated-plugin'
    errors, changed = m.evaluate_inventory(registry, tree)
    assert errors == []
    assert changed == ['example:example']


def test_namespaced_plugin_id_must_match_package_and_skill():
    path = 'plugins/example/skills/example'
    tree = [{'path': path, 'sha': 'baseline'},
            {'path': path + '/SKILL.md', 'sha': 'entry'},
            {'path': path + '/README.md', 'sha': 'docs'}]
    for skill_id in ['other:example', 'example:other', 'example:example:extra',
                     'example:', ':example']:
        registry = {'skills': [{'id': skill_id, 'path': path,
                    'baseline_tree_sha': 'baseline', 'maintainer': 'owner'}]}
        errors, _ = m.evaluate_inventory(registry, tree)
        assert errors == ['Invalid skill path: ' + skill_id]


def test_namespaced_inventory_still_rejects_duplicate_ids_and_paths():
    path = 'plugins/example/skills/example'
    skill = {'id': 'example:example', 'path': path,
             'baseline_tree_sha': 'baseline', 'maintainer': 'owner'}
    tree = [{'path': path, 'sha': 'baseline'},
            {'path': path + '/SKILL.md', 'sha': 'entry'},
            {'path': path + '/README.md', 'sha': 'docs'}]
    errors, _ = m.evaluate_inventory({'skills': [skill, dict(skill)]}, tree)
    assert 'Duplicate skill IDs in collection.json' in errors
    assert 'Duplicate skill paths in collection.json' in errors


def test_namespaced_id_does_not_allow_invalid_skill_paths():
    for path in ['example', 'plugins/../skills/example',
                 'plugins/example/skills/../example',
                 'plugins/example/other/example']:
        skill_id = 'example:example'
        registry = {'skills': [{'id': skill_id, 'path': path,
                    'baseline_tree_sha': 'baseline', 'maintainer': 'owner'}]}
        tree = [{'path': path, 'sha': 'baseline'},
                {'path': path + '/SKILL.md', 'sha': 'entry'},
                {'path': path + '/README.md', 'sha': 'docs'}]
        errors, _ = m.evaluate_inventory(registry, tree)
        assert errors == ['Invalid skill path: ' + skill_id]



def test_trash_and_synced_copies_are_not_unregistered_skills():
    errors, _ = m.evaluate_inventory({'skills': []}, [
        {'path': '.trash/123-abc/example/SKILL.md', 'sha': 'a'},
        {'path': 'synced/account/example/SKILL.md', 'sha': 'b'},
        {'path': 'example/SKILL.md', 'sha': 'c'}])
    assert errors == ['Unregistered skill: example']


def test_registered_skill_inside_synced_is_still_checked():
    registry = {'skills': [{'id': 'example', 'path': 'synced/example',
        'baseline_tree_sha': 'x', 'maintainer': 'owner'}]}
    errors, _ = m.evaluate_inventory(registry, [])
    assert 'Registered skill missing: example' in errors
