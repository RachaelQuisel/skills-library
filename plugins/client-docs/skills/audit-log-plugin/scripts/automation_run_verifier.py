#!/usr/bin/env python3
"""The automation run verifier.

Reads the audit diary and the plan. Gives one of three answers: verified,
not_achieved, or unknown. Missing proof is unknown. A recorded failure of
the success predicate is not_achieved.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import plan_status  # noqa: E402

OUTCOMES = ("verified", "not_achieved", "unknown")
PATH_RE = re.compile(r"(?<![\w./-])((?:[\w.-]+/)+[\w.-]+\.[\w]+)")


def parse_utc(value: str) -> datetime:
    raw = value.strip()
    iso = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    parsed = datetime.fromisoformat(iso)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must be UTC")
    if parsed.utcoffset().total_seconds() != 0:
        raise ValueError("timestamp must be UTC")
    return parsed.astimezone(timezone.utc)


def load_events(path: Path) -> tuple[list[dict] | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, str(exc)
    events = []
    for index, line in enumerate(text.splitlines()):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            return None, f"line {index + 1} is not JSON"
        if not isinstance(event, dict):
            return None, f"line {index + 1} is not an object"
        event["_line"] = index
        events.append(event)
    return events, None


def normalize_path(value: str) -> str:
    text = value.strip().strip("`").replace("\\", "/")
    if text.startswith("./"):
        text = text[2:]
    return text


def looks_like_path(value: str) -> bool:
    if any(char.isspace() for char in value):
        return False
    return "/" in value or bool(re.search(r"\.[A-Za-z0-9]+$", value))


def paths_named_in_plan(plan_text: str) -> set[str]:
    named = set()
    for span in re.findall(r"`([^`]+)`", plan_text):
        if looks_like_path(span):
            named.add(normalize_path(span))
    for match in PATH_RE.findall(plan_text):
        named.add(normalize_path(match))
    return named


def data_of(event: dict) -> dict:
    data = event.get("data_redacted")
    if data is None:
        data = event.get("data") or {}
    return data if isinstance(data, dict) else {}


def event_key(event: dict) -> tuple:
    raw = event.get("occurred_at") or event.get("observed_at")
    if not raw:
        raise ValueError("event is missing occurred_at and observed_at")
    return (parse_utc(raw), event.get("_line", 0))


def index_events(events: list[dict]) -> list[dict]:
    indexed = []
    for index, event in enumerate(events):
        copied = dict(event)
        copied.setdefault("_line", index)
        indexed.append(copied)
    return indexed


def _task_events(task_id: str, events: list[dict], event_type: str) -> list[dict]:
    matched = []
    for event in events:
        if event.get("event_type") != event_type:
            continue
        if data_of(event).get("task_id") != task_id:
            continue
        matched.append(event)
    return matched


def proof_gap(task_id: str, events: list[dict]) -> str:
    """Return ok, missing, or failed for one task's verification window.

    The window is after the task's last file change and before its latest
    task.completed.

    ok: a passing verification.ran sits inside that window.
    failed: a failing verification.ran sits inside that window, and no pass does.
    missing: nothing inside the window decides the task. A pass or fail that
    falls outside the window is not proof and is not a recorded failure.
    """
    completed = _task_events(task_id, events, "task.completed")
    verifications = _task_events(task_id, events, "verification.ran")
    changes = _task_events(task_id, events, "task.files_changed")
    if not completed or not verifications:
        return "missing"
    try:
        completion = max(completed, key=event_key)
        last_change = max(changes, key=event_key) if changes else None
    except (TypeError, ValueError):
        return "missing"
    saw_in_window_fail = False
    for verification in verifications:
        result = data_of(verification).get("result")
        if result not in {"pass", "fail"}:
            continue
        try:
            after_change = last_change is None or event_key(last_change) < event_key(verification)
            before_done = event_key(verification) < event_key(completion)
        except (TypeError, ValueError):
            continue
        if not (after_change and before_done):
            continue
        if result == "pass":
            return "ok"
        saw_in_window_fail = True
    return "failed" if saw_in_window_fail else "missing"


def task_has_passing_proof(task_id: str, events: list[dict]) -> bool:
    return proof_gap(task_id, index_events(events)) == "ok"


def _select_run(events: list[dict], run_id: str | None) -> tuple[str | None, str | None]:
    ids: list[str] = []
    for event in events:
        rid = event.get("run_id")
        if rid and rid not in ids:
            ids.append(rid)
    if run_id:
        if run_id not in ids:
            return None, "run_id is not in the log"
        return run_id, None
    if len(ids) == 1:
        return ids[0], None
    if not ids:
        return None, "log has no run_id"
    return None, "log contains more than one run_id"


def _report(
    outcome: str,
    *,
    reasons: list[str],
    run_id: str | None,
    execution_status: str,
    telemetry_health: str,
) -> dict:
    if outcome not in OUTCOMES:
        raise ValueError(outcome)
    return {
        "business_outcome": outcome,
        "execution_status": execution_status,
        "telemetry_health": telemetry_health,
        "reasons": reasons,
        "run_id": run_id,
    }


def verify_automation_run(plan_text: str, events: list[dict], run_id: str | None = None) -> dict:
    indexed = index_events(events)
    selected, select_reason = _select_run(indexed, run_id)
    if selected is None:
        return _report(
            "unknown",
            reasons=[select_reason or "run could not be selected"],
            run_id=run_id,
            execution_status="unknown",
            telemetry_health="unavailable" if not indexed else "incomplete",
        )

    scoped = [event for event in indexed if event.get("run_id") == selected]
    started = [event for event in scoped if event.get("event_type") == "run.started"]
    finished = [event for event in scoped if event.get("event_type") == "run.completed"]
    tasks = plan_status.parse_tasks(plan_text)
    progress = plan_status.parse_progress(plan_text)

    if not started or not finished:
        reasons = []
        if not started:
            reasons.append("missing run.started")
        if not finished:
            reasons.append("missing run.completed")
        execution = "running" if started else "unknown"
        return _report(
            "unknown",
            reasons=reasons,
            run_id=selected,
            execution_status=execution,
            telemetry_health="incomplete",
        )

    if not tasks or progress is None:
        reasons = []
        if not tasks:
            reasons.append("plan has no emoji tasks")
        if progress is None:
            reasons.append("plan has no overall progress percentage")
        return _report(
            "unknown",
            reasons=reasons,
            run_id=selected,
            execution_status="completed",
            telemetry_health="incomplete",
        )

    start_data = data_of(started[0])
    gaps: list[str] = []
    failures: list[str] = []
    if not start_data.get("plan_path") or not start_data.get("plan_hash"):
        gaps.append("run.started is missing plan_path or plan_hash")

    expected = plan_status.done_share_percent(tasks)
    if progress != expected:
        failures.append(
            f"progress is {progress}% and the done-task share rounds to {expected}%"
        )
    if any(task["status"] != "done" for task in tasks):
        open_titles = [task["title"] for task in tasks if task["status"] != "done"]
        failures.append("not every task is done: " + ", ".join(open_titles))

    allowed = paths_named_in_plan(plan_text)
    plan_path = start_data.get("plan_path")
    if isinstance(plan_path, str) and plan_path:
        allowed.add(normalize_path(plan_path))
    for event in scoped:
        if event.get("event_type") != "run.escalated":
            continue
        for approved in data_of(event).get("approved_files") or []:
            if isinstance(approved, str):
                allowed.add(normalize_path(approved))

    for event in scoped:
        if event.get("event_type") != "task.files_changed":
            continue
        files = data_of(event).get("files")
        if not isinstance(files, list) or not files:
            gaps.append("task.files_changed is missing its file list")
            continue
        for file_path in files:
            if not isinstance(file_path, str):
                gaps.append("task.files_changed lists a non-text path")
                continue
            if normalize_path(file_path) not in allowed:
                failures.append(f"changed file was not named or approved: {file_path}")

    for task in tasks:
        if task["status"] != "done":
            continue
        gap = proof_gap(task["title"], scoped)
        if gap == "missing":
            gaps.append(f"task {task['title']!r} is marked done without passing proof")
        elif gap == "failed":
            failures.append(
                f"task {task['title']!r} has a failing verification.ran inside the required window"
            )

    execution_status = "completed"
    recorded = data_of(finished[-1]).get("execution_status")
    if isinstance(recorded, str) and recorded:
        execution_status = recorded

    if failures:
        return _report(
            "not_achieved",
            reasons=failures + gaps,
            run_id=selected,
            execution_status=execution_status,
            telemetry_health="incomplete" if gaps else "current",
        )
    if gaps:
        return _report(
            "unknown",
            reasons=gaps,
            run_id=selected,
            execution_status=execution_status,
            telemetry_health="incomplete",
        )
    return _report(
        "verified",
        reasons=["every task is done, proven, and the progress percentage matches"],
        run_id=selected,
        execution_status=execution_status,
        telemetry_health="current",
    )


def verify_automation_run_files(plan_path: Path, log_path: Path, run_id: str | None = None) -> dict:
    try:
        plan_text = plan_path.read_text(encoding="utf-8")
    except OSError as exc:
        return _report(
            "unknown",
            reasons=[f"plan could not be read: {exc}"],
            run_id=run_id,
            execution_status="unknown",
            telemetry_health="unavailable",
        )
    events, error = load_events(log_path)
    if error is not None or events is None:
        return _report(
            "unknown",
            reasons=[f"log could not be read: {error}"],
            run_id=run_id,
            execution_status="unknown",
            telemetry_health="unavailable",
        )
    return verify_automation_run(plan_text, events, run_id=run_id)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="The automation run verifier reads the audit diary and the plan and reports verified, not_achieved, or unknown."
    )
    parser.add_argument("--plan", required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("--run-id")
    args = parser.parse_args(argv)
    report = verify_automation_run_files(Path(args.plan), Path(args.log), run_id=args.run_id)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
