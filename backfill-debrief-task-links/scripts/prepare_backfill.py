#!/usr/bin/env python3
"""Validate a client-scoped manifest and emit one-record Airtable updates."""

from __future__ import annotations

import json
import re
import sys
from typing import Any


BASE_ID = "appExample0000004"
TASKS_TABLE_ID = "tblExample0000010"
SOURCE_FIELD_ID = "fldExample0000013"
TARGET_FIELD_ID = "fldExample0000015"

_RECORD_ID = re.compile(r"^rec[A-Za-z0-9]{14}$")


def _record_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _RECORD_ID.fullmatch(value):
        raise ValueError(f"{label} must be an Airtable record ID")
    return value


def _record_id_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    result = [_record_id(item, label) for item in value]
    if len(result) != len(set(result)):
        raise ValueError(f"{label} contains duplicate record IDs")
    return result


def build_plan(manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be an object")

    client_id = _record_id(manifest.get("clientRecordId"), "clientRecordId")
    tasks = manifest.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("tasks must be a list")

    seen_tasks: set[str] = set()
    updates: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []
    verification: list[dict[str, Any]] = []

    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            raise ValueError(f"tasks[{index}] must be an object")

        task_id = _record_id(task.get("taskRecordId"), f"tasks[{index}].taskRecordId")
        if task_id in seen_tasks:
            raise ValueError(f"duplicate taskRecordId: {task_id}")
        seen_tasks.add(task_id)

        source_ids = _record_id_list(
            task.get("sourceMeetingIds"), f"tasks[{index}].sourceMeetingIds"
        )
        target_ids = _record_id_list(
            task.get("targetMeetingIds"), f"tasks[{index}].targetMeetingIds"
        )
        meetings = task.get("meetings")
        if not isinstance(meetings, list):
            raise ValueError(f"tasks[{index}].meetings must be a list")

        meeting_clients: dict[str, list[str]] = {}
        for meeting_index, meeting in enumerate(meetings):
            if not isinstance(meeting, dict):
                raise ValueError(
                    f"tasks[{index}].meetings[{meeting_index}] must be an object"
                )
            meeting_id = _record_id(
                meeting.get("recordId"),
                f"tasks[{index}].meetings[{meeting_index}].recordId",
            )
            if meeting_id in meeting_clients:
                raise ValueError(f"duplicate meeting evidence: {meeting_id}")
            meeting_clients[meeting_id] = _record_id_list(
                meeting.get("clientRecordIds"),
                f"tasks[{index}].meetings[{meeting_index}].clientRecordIds",
            )

        if set(meeting_clients) != set(source_ids):
            raise ValueError(f"task {task_id} meeting evidence does not match source links")

        if not source_ids:
            excluded.append({"taskRecordId": task_id, "reason": "source-empty"})
            continue
        if target_ids:
            excluded.append({"taskRecordId": task_id, "reason": "target-not-empty"})
            continue

        client_sets = [meeting_clients[meeting_id] for meeting_id in source_ids]
        if any(len(client_ids) != 1 for client_ids in client_sets):
            excluded.append(
                {"taskRecordId": task_id, "reason": "ambiguous-client-scope"}
            )
            continue
        if any(client_ids[0] != client_id for client_ids in client_sets):
            excluded.append(
                {"taskRecordId": task_id, "reason": "out-of-scope-client"}
            )
            continue

        # One task per request limits the effect of a stale read or bad payload.
        updates.append(
            {
                "baseId": BASE_ID,
                "tableId": TASKS_TABLE_ID,
                "records": [
                    {
                        "id": task_id,
                        "fields": {TARGET_FIELD_ID: source_ids},
                    }
                ],
                "fieldIds": [SOURCE_FIELD_ID, TARGET_FIELD_ID],
            }
        )
        verification.append(
            {
                "taskRecordId": task_id,
                "expectedSourceMeetingIds": source_ids,
                "expectedTargetMeetingIds": source_ids,
            }
        )

    return {
        "clientRecordId": client_id,
        "eligibleCount": len(updates),
        "excluded": excluded,
        "updates": updates,
        "verification": verification,
    }


def main() -> int:
    try:
        manifest = json.load(sys.stdin)
        plan = build_plan(manifest)
    except (ValueError, json.JSONDecodeError) as error:
        # Keep errors structured and omit stack traces because manifests contain client IDs.
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2

    json.dump(plan, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
