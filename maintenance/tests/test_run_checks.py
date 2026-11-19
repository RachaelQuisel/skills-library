import importlib.util
import json
from pathlib import Path
import subprocess

spec = importlib.util.spec_from_file_location('run_checks', Path(__file__).parents[1] / 'run_checks.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fake_runner(release_code=0, maintenance_code=0, write_report=True, sync_code=0, write_sync=True):
    calls = []
    def execute(command, **kwargs):
        calls.append(command)
        is_maintenance = any(arg.endswith('/maintenance/check.py') for arg in command)
        is_sync = any(arg.endswith('/maintenance/plugin_sync.py') for arg in command)
        if is_maintenance and write_report:
            directory = Path(command[command.index('--output') + 1])
            directory.mkdir(parents=True, exist_ok=True)
            (directory / 'report.json').write_text(json.dumps({
                'inventory_errors': [], 'skills': [],
                'suites': {'synthetic': {'status': 'passed', 'tests': 1}}}))
        if is_sync and write_sync:
            path = Path(command[command.index('--output') + 1])
            path.write_text(json.dumps({'status':'failed' if sync_code else 'passed', 'problems':[]}))
        code = sync_code if is_sync else maintenance_code if is_maintenance else release_code
        return subprocess.CompletedProcess(command, code, 'synthetic result\n', '')
    return execute, calls


def test_release_failure_does_not_skip_maintenance(tmp_path):
    execute, calls = fake_runner(release_code=1)
    result = m.run_checks(tmp_path, 'HEAD^', execute)
    assert len(calls) == 3
    assert result['status'] == 'failed'
    assert result['maintenance_execution']['status'] == 'passed'
    assert (tmp_path / 'release.log').is_file()
    assert (tmp_path / 'report.md').is_file()


def test_maintenance_failure_cannot_be_hidden_by_release_success(tmp_path):
    execute, _ = fake_runner(maintenance_code=1)
    assert m.run_checks(tmp_path, runner=execute)['status'] == 'failed'


def test_stale_report_cannot_make_missing_evidence_pass(tmp_path):
    directory = tmp_path / 'maintenance'
    directory.mkdir()
    (directory / 'report.json').write_text('{"inventory_errors": [], "suites": {"old": {"status": "passed"}}}')
    execute, _ = fake_runner(write_report=False)
    result = m.run_checks(tmp_path, runner=execute)
    assert result['status'] == 'failed'
    assert result['maintenance'] is None


def test_both_checks_must_pass(tmp_path):
    execute, _ = fake_runner()
    assert m.run_checks(tmp_path, runner=execute)['status'] == 'passed'


def test_sync_failure_is_not_hidden_by_passing_offline_checks(tmp_path):
    execute, _ = fake_runner(sync_code=1)
    result = m.run_checks(tmp_path, runner=execute, sync_observation=tmp_path/'capture.json')
    assert result['status'] == 'failed'
    assert result['plugin_sync']['status'] == 'failed'


def test_previous_sync_result_cannot_hide_missing_new_evidence(tmp_path):
    (tmp_path/'plugin-sync.json').write_text('{"status":"passed"}')
    execute, _ = fake_runner(write_sync=False)
    result = m.run_checks(tmp_path, runner=execute)
    assert result['status'] == 'failed'
    assert result['plugin_sync']['status'] == 'unknown'
