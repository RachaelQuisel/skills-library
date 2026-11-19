#!/usr/bin/env python3
"""Reopen one plan task marked done without passing proof.

This correction edits the plan file only: the task emoji goes back to to-do,
the progress percentage is recomputed, and a correction.reopened event is
appended. It does not edit code or invoke git.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "execute" / "scripts"))

import automation_run_verifier  # noqa: E402
import log_event  # noqa: E402
import plan_status  # noqa: E402


class ReopenRejected(ValueError):
    """The correction does not apply. The plan was not changed."""


def _completed_events(events: list[dict], task_id: str, run_id: str | None) -> list[dict]:
    matched = []
    for event in events:
        if event.get("event_type") != "task.completed":
            continue
        data = automation_run_verifier.data_of(event)
        if data.get("task_id") != task_id:
            continue
        if run_id is not None and event.get("run_id") != run_id:
            continue
        matched.append(event)
    return matched


def reopen_task(
    plan_path,
    log_path,
    task_id: str,
    *,
    requested_by: str = "operator",
    run_id: str | None = None,
    workspace_id: str | None = None,
) -> dict:
    plan_file = Path(plan_path)
    log_file = Path(log_path)
    original = plan_file.read_text(encoding="utf-8")
    tasks = [task for task in plan_status.parse_tasks(original) if task["title"] == task_id]
    if len(tasks) != 1:
        raise ReopenRejected(f"expected one task titled {task_id!r}, found {len(tasks)}")
    if tasks[0]["status"] != "done":
        raise ReopenRejected("correction only reopens a task marked done")

    events, error = automation_run_verifier.load_events(log_file) if log_file.exists() else ([], None)
    if error is not None or events is None:
        raise ReopenRejected(f"log could not be read: {error}")

    if run_id is None:
        run_ids = []
        for event in _completed_events(events, task_id, None):
            if event["run_id"] not in run_ids:
                run_ids.append(event["run_id"])
        if len(run_ids) > 1:
            raise ReopenRejected("task.completed appears in multiple runs; pass run_id")
        run_id = run_ids[0] if run_ids else None

    scoped = [event for event in events if run_id is None or event.get("run_id") == run_id]
    if automation_run_verifier.task_has_passing_proof(task_id, scoped):
        raise ReopenRejected("task has passing proof; refusing to reopen")

    completed = _completed_events(scoped, task_id, run_id)
    if not completed:
        raise ReopenRejected("no task.completed event to link the correction to")
    target = max(completed, key=automation_run_verifier.event_key)

    new_text = plan_status.set_task_status(original, task_id, "todo")
    percent = plan_status.done_share_percent(plan_status.parse_tasks(new_text))
    if percent is None:
        raise ReopenRejected("plan has no tasks after the edit")
    new_text = plan_status.set_progress(new_text, percent)

    temporary = plan_file.with_name(plan_file.name + ".tmp")
    temporary.write_text(new_text, encoding="utf-8")
    temporary.replace(plan_file)
    try:
        readback = plan_file.read_text(encoding="utf-8")
        read_tasks = [
            task for task in plan_status.parse_tasks(readback) if task["title"] == task_id
        ]
        read_progress = plan_status.parse_progress(readback)
        applied = (
            len(read_tasks) == 1
            and read_tasks[0]["status"] == "todo"
            and read_progress == percent
        )
        status = "applied" if applied else "failed"
        if not applied:
            plan_file.write_text(original, encoding="utf-8")
        data = {
            "task_id": task_id,
            "target_event_id": target.get("event_id"),
            "target_source_event_id": target.get("source_event_id"),
            "scope": "this_run",
            "status": status,
            "requested_by": requested_by,
            "proposed_change": {"task_id": task_id, "status": "todo", "progress": percent},
        }
        ack = log_event.append_event(
            log_file,
            {
                "workspace_id": workspace_id
                or target.get("workspace_id")
                or log_event.PILOT_WORKSPACE_ID,
                "source": target.get("source") or "execute",
                "run_id": target["run_id"],
                "attempt_id": target["attempt_id"],
                "event_type": "correction.reopened",
                "data_redacted": data,
            },
        )
    except Exception:
        plan_file.write_text(original, encoding="utf-8")
        raise

    if status != "applied":
        raise ReopenRejected("plan readback did not match the correction; original plan restored")
    return {
        "status": status,
        "task_id": task_id,
        "progress": percent,
        "target_event_id": target.get("event_id"),
        "event": ack,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Reopen a done task that lacks passing proof.")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--requested-by", default="operator")
    parser.add_argument("--run-id")
    parser.add_argument("--workspace-id")
    args = parser.parse_args(argv)
    try:
        result = reopen_task(
            args.plan,
            args.log,
            args.task_id,
            requested_by=args.requested_by,
            run_id=args.run_id,
            workspace_id=args.workspace_id,
        )
    except (ReopenRejected, log_event.EventRejected) as exc:
        print(json.dumps({"status": "rejected", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
