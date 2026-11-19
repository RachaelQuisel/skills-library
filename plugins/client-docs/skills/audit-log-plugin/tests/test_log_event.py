import json
import subprocess
import sys

from conftest import REPO, load_module

log_event = load_module("log_event", REPO / "execute" / "scripts" / "log_event.py")

WORKSPACE = "6f0d1c3a-7b2e-4a51-9c8d-0e1f2a3b4c5d"
OTHER_WORKSPACE = "6f0d1c3a-7b2e-4a51-9c8d-0e1f2a3b4c5e"
RUN_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
ATTEMPT_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"


def test_duplicate_event_is_rejected_and_original_body_remains(tmp_path):
    path = tmp_path / "events.jsonl"
    first = log_event.append_event(
        path,
        {
            "workspace_id": WORKSPACE,
            "source": "execute",
            "source_event_id": "evt-1",
            "run_id": RUN_ID,
            "attempt_id": ATTEMPT_ID,
            "event_type": "run.started",
            "data_redacted": {
                "plan_path": "plan.md",
                "plan_hash": "first-hash",
                "api_key": "super-secret",
                "note": "Authorization: Bearer abcdefghijklmnop",
            },
        },
    )
    second = log_event.append_event(
        path,
        {
            "workspace_id": WORKSPACE,
            "source": "execute",
            "source_event_id": "evt-1",
            "run_id": RUN_ID,
            "attempt_id": ATTEMPT_ID,
            "event_type": "run.started",
            "data_redacted": {"plan_path": "plan.md", "plan_hash": "second-hash"},
        },
    )

    lines = path.read_text(encoding="utf-8").splitlines()
    stored = json.loads(lines[0])
    assert first["status"] == "accepted"
    assert second["status"] == "duplicate"
    assert second["event_id"] == first["event_id"]
    assert len(lines) == 1
    assert stored["data_redacted"]["plan_hash"] == "first-hash"
    assert stored["data_redacted"]["api_key"] == "[REDACTED]"
    assert "abcdefghijklmnop" not in lines[0]
    assert stored["observed_at"].endswith("Z")
    assert stored["run_id"] == RUN_ID
    assert stored["attempt_id"] == ATTEMPT_ID


def test_same_event_id_in_another_workspace_is_stored(tmp_path):
    path = tmp_path / "events.jsonl"
    log_event.append_event(
        path,
        {
            "workspace_id": WORKSPACE,
            "source": "execute",
            "source_event_id": "evt-1",
            "run_id": RUN_ID,
            "attempt_id": ATTEMPT_ID,
            "event_type": "run.started",
            "data_redacted": {"plan_path": "plan.md", "plan_hash": "one"},
        },
    )
    other = log_event.append_event(
        path,
        {
            "workspace_id": OTHER_WORKSPACE,
            "source": "execute",
            "source_event_id": "evt-1",
            "run_id": RUN_ID,
            "attempt_id": ATTEMPT_ID,
            "event_type": "run.started",
            "data_redacted": {"plan_path": "plan.md", "plan_hash": "two"},
        },
    )

    assert other["status"] == "accepted"
    assert len(path.read_text(encoding="utf-8").splitlines()) == 2


def test_cli_redelivery_does_not_append_a_second_line(tmp_path):
    log_path = tmp_path / "events.jsonl"
    plan_path = tmp_path / "plan.md"
    plan_path.write_text("# Plan\n", encoding="utf-8")
    command = [
        sys.executable,
        str(REPO / "execute" / "scripts" / "log_event.py"),
        "--log",
        str(log_path),
        "--type",
        "run.started",
        "--workspace-id",
        WORKSPACE,
        "--run-id",
        RUN_ID,
        "--attempt-id",
        ATTEMPT_ID,
        "--source-event-id",
        "cli-evt-1",
        "--plan-path",
        str(plan_path),
    ]
    first = subprocess.run(command, check=True, capture_output=True, text=True)
    second = subprocess.run(command, check=True, capture_output=True, text=True)

    assert json.loads(first.stdout)["status"] == "accepted"
    assert json.loads(second.stdout)["status"] == "duplicate"
    assert len(log_path.read_text(encoding="utf-8").splitlines()) == 1
