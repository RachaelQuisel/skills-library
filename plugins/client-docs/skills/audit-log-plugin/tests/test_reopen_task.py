import json
import uuid

import pytest
from conftest import PLUGIN, load_module

reopen_task = load_module("reopen_task", PLUGIN / "scripts" / "reopen_task.py")

RUN = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
ATTEMPT = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
WS = "6f0d1c3a-7b2e-4a51-9c8d-0e1f2a3b4c5d"


def _plan():
    return """# Feature Implementation Plan

**Overall Progress:** `100%`

## Tasks:

- [x] 🟩 **Write the logger**
- [x] 🟩 **Write the automation run verifier**
"""


def _event(event_type, second, event_id=None, **data):
    return {
        "event_id": event_id or str(uuid.uuid4()),
        "workspace_id": WS,
        "source": "execute",
        "source_event_id": f"{event_type}-{data.get('task_id', 'run')}",
        "run_id": RUN,
        "attempt_id": ATTEMPT,
        "event_type": event_type,
        "occurred_at": f"2026-10-05T00:00:{second:02d}.000000Z",
        "observed_at": f"2026-10-05T00:00:{second:02d}.000000Z",
        "data_redacted": data,
    }


def _write_log(path, events):
    path.write_text(
        "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
        encoding="utf-8",
    )


def test_reopen_sets_the_plan_back_and_links_the_original_completion(tmp_path):
    plan = tmp_path / "plan.md"
    log = tmp_path / "events.jsonl"
    decoy = tmp_path / "notes.txt"
    plan.write_text(_plan(), encoding="utf-8")
    decoy.write_text("do not touch\n", encoding="utf-8")
    completed_id = str(uuid.uuid4())
    _write_log(
        log,
        [
            _event("run.started", 1, plan_path="plan.md", plan_hash="abc"),
            _event(
                "task.completed",
                2,
                event_id=completed_id,
                task_id="Write the automation run verifier",
            ),
        ],
    )

    result = reopen_task.reopen_task(plan, log, "Write the automation run verifier", requested_by="operator")

    text = plan.read_text(encoding="utf-8")
    assert "🟥 **Write the automation run verifier**" in text
    assert "[ ] 🟥 **Write the automation run verifier**" in text
    assert "🟩 **Write the logger**" in text
    assert "**Overall Progress:** `50%`" in text
    assert decoy.read_text(encoding="utf-8") == "do not touch\n"
    assert result["status"] == "applied"
    assert result["target_event_id"] == completed_id

    stored = [
        json.loads(line)
        for line in log.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    corrections = [event for event in stored if event["event_type"] == "correction.reopened"]
    assert len(corrections) == 1
    assert corrections[0]["data_redacted"]["target_event_id"] == completed_id
    assert corrections[0]["data_redacted"]["target_source_event_id"] == "task.completed-Write the automation run verifier"
    assert corrections[0]["data_redacted"]["status"] == "applied"
    assert corrections[0]["run_id"] == RUN
    assert corrections[0]["attempt_id"] == ATTEMPT
    completed = next(event for event in stored if event["event_id"] == completed_id)
    assert completed["event_type"] == "task.completed"


def test_reopen_refuses_a_task_that_has_passing_proof(tmp_path):
    plan = tmp_path / "plan.md"
    log = tmp_path / "events.jsonl"
    original = _plan()
    plan.write_text(original, encoding="utf-8")
    _write_log(
        log,
        [
            _event("task.files_changed", 1, task_id="Write the logger", files=["execute/SKILL.md"]),
            _event(
                "verification.ran",
                2,
                task_id="Write the logger",
                command="python3 -m pytest",
                result="pass",
            ),
            _event("task.completed", 3, task_id="Write the logger"),
        ],
    )
    before = log.read_text(encoding="utf-8")

    with pytest.raises(reopen_task.ReopenRejected):
        reopen_task.reopen_task(plan, log, "Write the logger")

    assert plan.read_text(encoding="utf-8") == original
    assert log.read_text(encoding="utf-8") == before
