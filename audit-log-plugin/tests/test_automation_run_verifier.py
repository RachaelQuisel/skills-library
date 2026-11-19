import json
import uuid

from conftest import PLUGIN, REPO, load_module

automation_run_verifier = load_module(
    "automation_run_verifier", PLUGIN / "scripts" / "automation_run_verifier.py"
)
plan_status = load_module("audit_plan_status", PLUGIN / "scripts" / "plan_status.py")
log_event = load_module("log_event", REPO / "execute" / "scripts" / "log_event.py")
reopen_task = load_module("reopen_task", PLUGIN / "scripts" / "reopen_task.py")

RUN = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
ATTEMPT = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
WS = "6f0d1c3a-7b2e-4a51-9c8d-0e1f2a3b4c5d"
LOGGER = "execute/scripts/log_event.py"
AUTOMATION_RUN_VERIFIER = "audit-log-plugin/scripts/automation_run_verifier.py"


def _plan(*, logger="🟩", automation_run_verifier_mark="🟩", progress=100):
    return f"""# Feature Implementation Plan

**Overall Progress:** `{progress}%`

## Tasks:

- [x] {logger} **Write the logger**
  - Touch `{LOGGER}`
- [x] {automation_run_verifier_mark} **Write the automation run verifier**
"""


def _event(event_type, second, **data):
    return {
        "event_id": str(uuid.uuid4()),
        "workspace_id": WS,
        "source": "execute",
        "source_event_id": f"{event_type}-{second}-{data.get('task_id', '')}",
        "run_id": RUN,
        "attempt_id": ATTEMPT,
        "event_type": event_type,
        "occurred_at": f"2026-10-05T00:00:{second:02d}.000000Z",
        "observed_at": f"2026-10-05T00:00:{second:02d}.000000Z",
        "data_redacted": data,
    }


def _task_chain(title, file_path, second, result="pass", include_verification=True):
    events = [
        _event("task.started", second, task_id=title),
        _event("task.files_changed", second + 1, task_id=title, files=[file_path]),
    ]
    if include_verification:
        events.append(
            _event(
                "verification.ran",
                second + 2,
                task_id=title,
                command="python3 -m pytest",
                result=result,
            )
        )
    events.append(_event("task.completed", second + 3, task_id=title))
    return events


def _run_events(logger_kwargs=None, automation_run_verifier_kwargs=None, approve_automation_run_verifier=True):
    events = [
        _event(
            "run.started",
            1,
            plan_path="plan.md",
            plan_hash="abc123",
        )
    ]
    events.extend(_task_chain("Write the logger", LOGGER, 10, **(logger_kwargs or {})))
    if approve_automation_run_verifier:
        events.append(
            _event(
                "run.escalated",
                20,
                reason="automation run verifier path was not in the original plan text",
                approved_files=[AUTOMATION_RUN_VERIFIER],
            )
        )
    events.extend(
        _task_chain(
            "Write the automation run verifier",
            AUTOMATION_RUN_VERIFIER,
            30,
            **(automation_run_verifier_kwargs or {}),
        )
    )
    events.append(_event("run.completed", 40))
    return events


def test_progress_rounds_half_up():
    tasks = [
        {"status": "done"},
        {"status": "done"},
        {"status": "todo"},
    ]
    assert plan_status.done_share_percent(tasks) == 67


def test_complete_proven_run_is_verified():
    report = automation_run_verifier.verify_automation_run(_plan(), _run_events())
    assert report["business_outcome"] == "verified"
    assert report["execution_status"] == "completed"
    assert report["telemetry_health"] == "current"
    assert report["run_id"] == RUN


def test_open_task_is_not_achieved():
    report = automation_run_verifier.verify_automation_run(
        _plan(automation_run_verifier_mark="🟥", progress=50),
        _run_events(),
    )
    assert report["business_outcome"] == "not_achieved"


def test_failed_verification_is_not_achieved():
    report = automation_run_verifier.verify_automation_run(
        _plan(),
        _run_events(automation_run_verifier_kwargs={"result": "fail"}),
    )
    assert report["business_outcome"] == "not_achieved"


def test_unapproved_file_is_not_achieved():
    report = automation_run_verifier.verify_automation_run(
        _plan(),
        _run_events(approve_automation_run_verifier=False),
    )
    assert report["business_outcome"] == "not_achieved"


def test_missing_verification_is_unknown():
    events = _run_events(automation_run_verifier_kwargs={"include_verification": False})
    report = automation_run_verifier.verify_automation_run(_plan(), events)
    assert report["business_outcome"] == "unknown"
    assert report["telemetry_health"] == "incomplete"
    assert any("Write the automation run verifier" in reason for reason in report["reasons"])


def test_run_without_completion_is_unknown():
    events = _run_events()
    events = [event for event in events if event["event_type"] != "run.completed"]
    report = automation_run_verifier.verify_automation_run(_plan(), events)
    assert report["business_outcome"] == "unknown"


def _one_task_plan():
    return f"""# Feature Implementation Plan

**Overall Progress:** `100%`

## Tasks:

- [x] 🟩 **Write the logger**
  - Touch `{LOGGER}`
"""


def _bare_run(*task_events):
    return [
        _event("run.started", 1, plan_path="plan.md", plan_hash="abc123"),
        *task_events,
        _event("run.completed", 50),
    ]


def test_verification_after_completion_is_unknown():
    events = _bare_run(
        _event("task.files_changed", 2, task_id="Write the logger", files=[LOGGER]),
        _event("task.completed", 3, task_id="Write the logger"),
        _event(
            "verification.ran",
            4,
            task_id="Write the logger",
            command="python3 -m pytest",
            result="pass",
        ),
    )
    report = automation_run_verifier.verify_automation_run(_one_task_plan(), events)
    assert report["business_outcome"] == "unknown"


def test_verification_before_last_file_change_is_unknown():
    events = _bare_run(
        _event(
            "verification.ran",
            2,
            task_id="Write the logger",
            command="python3 -m pytest",
            result="pass",
        ),
        _event("task.files_changed", 3, task_id="Write the logger", files=[LOGGER]),
        _event("task.completed", 4, task_id="Write the logger"),
    )
    report = automation_run_verifier.verify_automation_run(_one_task_plan(), events)
    assert report["business_outcome"] == "unknown"


def test_progress_rounding_through_verify_automation_run():
    def three_task_plan(progress):
        return f"""# Feature Implementation Plan

**Overall Progress:** `{progress}%`

## Tasks:

- [x] 🟩 **One**
- [x] 🟩 **Two**
- [ ] 🟥 **Three**
"""

    def proven(title, second):
        return [
            _event("task.started", second, task_id=title),
            _event(
                "verification.ran",
                second + 1,
                task_id=title,
                command="review: " + title,
                result="pass",
            ),
            _event("task.completed", second + 2, task_id=title),
        ]

    events = _bare_run(*proven("One", 10), *proven("Two", 20))
    matched = automation_run_verifier.verify_automation_run(three_task_plan(67), events)
    missed = automation_run_verifier.verify_automation_run(three_task_plan(66), events)
    assert matched["business_outcome"] == "not_achieved"
    assert missed["business_outcome"] == "not_achieved"
    assert not any(reason.startswith("progress is") for reason in matched["reasons"])
    assert any("progress is 66%" in reason and "67%" in reason for reason in missed["reasons"])


def test_indented_subtasks_are_not_tasks():
    plan = f"""# Feature Implementation Plan

**Overall Progress:** `100%`

## Tasks:

- [x] 🟩 **Write the logger**
  - Touch `{LOGGER}`
  - [ ] 🟥 Subtask still open
"""
    events = _bare_run(
        *_task_chain("Write the logger", LOGGER, 10),
    )
    titles = [task["title"] for task in plan_status.parse_tasks(plan)]
    report = automation_run_verifier.verify_automation_run(plan, events)
    assert titles == ["Write the logger"]
    assert report["business_outcome"] == "verified"


def _append(path, event_type, second, **data):
    return log_event.append_event(
        path,
        {
            "workspace_id": WS,
            "source": "execute",
            "run_id": RUN,
            "attempt_id": ATTEMPT,
            "event_type": event_type,
            "occurred_at": f"2026-10-05T00:00:{second:02d}.000000Z",
            "data_redacted": data,
        },
    )


def test_post_reopen_completion_is_accepted_and_run_reverifies(tmp_path):
    plan = tmp_path / "plan.md"
    log = tmp_path / "events.jsonl"
    plan.write_text(_one_task_plan(), encoding="utf-8")
    _append(log, "run.started", 1, plan_path="plan.md", plan_hash="abc123")
    _append(log, "task.started", 2, task_id="Write the logger")
    _append(
        log,
        "task.files_changed",
        3,
        task_id="Write the logger",
        files=[LOGGER],
    )
    first = _append(log, "task.completed", 4, task_id="Write the logger")
    retry = _append(log, "task.completed", 5, task_id="Write the logger")
    assert first["status"] == "accepted"
    assert first["source_event_id"].endswith(":0")
    assert retry["status"] == "duplicate"
    assert retry["source_event_id"] == first["source_event_id"]

    reopen_task.reopen_task(plan, log, "Write the logger")
    started_again = _append(log, "task.started", 6, task_id="Write the logger")
    _append(
        log,
        "verification.ran",
        7,
        task_id="Write the logger",
        command="review: Write the logger",
        result="pass",
    )
    second = _append(log, "task.completed", 8, task_id="Write the logger")
    second_retry = _append(log, "task.completed", 9, task_id="Write the logger")
    _append(log, "run.completed", 10)

    assert started_again["status"] == "accepted"
    assert started_again["source_event_id"].endswith(":1")
    assert second["status"] == "accepted"
    assert second["source_event_id"].endswith(":1")
    assert second["source_event_id"] != first["source_event_id"]
    assert second_retry["status"] == "duplicate"

    restored = plan_status.set_progress(
        plan_status.set_task_status(plan.read_text(encoding="utf-8"), "Write the logger", "done"),
        100,
    )
    events, error = automation_run_verifier.load_events(log)
    assert error is None
    report = automation_run_verifier.verify_automation_run(restored, events)
    assert report["business_outcome"] == "verified"


def _mark_done(plan_path):
    text = plan_status.set_task_status(
        plan_path.read_text(encoding="utf-8"),
        "Write the logger",
        "done",
    )
    plan_path.write_text(plan_status.set_progress(text, 100), encoding="utf-8")


def test_two_reopen_cycles_end_verified(tmp_path):
    plan = tmp_path / "plan.md"
    log = tmp_path / "events.jsonl"
    plan.write_text(_one_task_plan(), encoding="utf-8")
    _append(log, "run.started", 1, plan_path="plan.md", plan_hash="abc123")
    _append(log, "task.started", 2, task_id="Write the logger")
    _append(
        log,
        "task.files_changed",
        3,
        task_id="Write the logger",
        files=[LOGGER],
    )
    _append(log, "task.completed", 4, task_id="Write the logger")

    first_reopen = reopen_task.reopen_task(plan, log, "Write the logger")
    assert first_reopen["event"]["status"] == "accepted"

    _mark_done(plan)
    redelivery = reopen_task.reopen_task(plan, log, "Write the logger")
    assert redelivery["event"]["status"] == "duplicate"
    assert redelivery["event"]["source_event_id"] == first_reopen["event"]["source_event_id"]

    second_done = _append(log, "task.completed", 6, task_id="Write the logger")
    assert second_done["status"] == "accepted"
    assert second_done["source_event_id"].endswith(":1")
    _mark_done(plan)
    second_reopen = reopen_task.reopen_task(plan, log, "Write the logger")
    assert second_reopen["event"]["status"] == "accepted"
    assert second_reopen["event"]["source_event_id"] != first_reopen["event"]["source_event_id"]
    assert second_reopen["target_event_id"] == second_done["event_id"]

    _append(
        log,
        "verification.ran",
        8,
        task_id="Write the logger",
        command="review: Write the logger",
        result="pass",
    )
    third_done = _append(log, "task.completed", 9, task_id="Write the logger")
    _append(log, "run.completed", 10)
    assert third_done["status"] == "accepted"
    assert third_done["source_event_id"].endswith(":2")

    _mark_done(plan)
    events, error = automation_run_verifier.load_events(log)
    assert error is None
    corrections = [event for event in events if event["event_type"] == "correction.reopened"]
    assert len(corrections) == 2
    report = automation_run_verifier.verify_automation_run(plan.read_text(encoding="utf-8"), events)
    assert report["business_outcome"] == "verified"


def test_automation_run_verifier_cli_reports_unknown_for_a_missing_log(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text(_plan(), encoding="utf-8")
    report = automation_run_verifier.verify_automation_run_files(plan, tmp_path / "missing.jsonl")
    assert report["business_outcome"] == "unknown"
    parsed = json.loads(json.dumps(report))
    assert parsed["business_outcome"] in {"verified", "not_achieved", "unknown"}
