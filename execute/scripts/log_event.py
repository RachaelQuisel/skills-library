#!/usr/bin/env python3
"""Append one redacted audit event as a UTC JSON line.

The script is dependency-free. A repeated delivery with the same
(workspace_id, source, source_event_id) is acknowledged and not written again.
The acknowledgement is printed only after the new line has been flushed and
fsynced, or after the existing line has been found under the file lock.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover - pilot runs on POSIX
    fcntl = None

EVENT_TYPES = (
    "run.started",
    "task.started",
    "task.files_changed",
    "verification.ran",
    "task.completed",
    "run.escalated",
    "run.completed",
    "correction.reopened",
)

EXECUTION_STATUSES = (
    "queued",
    "running",
    "waiting",
    "completed",
    "failed",
    "cancelled",
    "unknown",
)

DEFAULT_LOG = Path("execute/.audit/events.jsonl")
PILOT_WORKSPACE_ID = "6f0d1c3a-7b2e-4a51-9c8d-0e1f2a3b4c5d"

SECRET_KEY = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|authorization|credential|private[_-]?key)",
    re.IGNORECASE,
)
SECRET_VALUE = re.compile(
    r"(?i)\b(?:bearer\s+\S+|sk-[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{16}|"
    r"ghp_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,})"
)

TASK_EVENTS = {
    "task.started",
    "task.files_changed",
    "verification.ran",
    "task.completed",
    "correction.reopened",
}


class EventRejected(ValueError):
    """The event is not valid and was not written."""


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def parse_utc(value: str) -> str:
    """Return a canonical UTC timestamp, or raise EventRejected."""
    raw = value.strip()
    iso = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(iso)
    except ValueError as exc:
        raise EventRejected(f"timestamp is not ISO-8601: {value}") from exc
    if parsed.tzinfo is None:
        raise EventRejected("timestamp must include a UTC offset")
    if parsed.utcoffset().total_seconds() != 0:
        raise EventRejected("timestamp must be UTC")
    return parsed.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def canonical_uuid(value: str, field: str) -> str:
    try:
        return str(uuid.UUID(str(value)))
    except (TypeError, ValueError, AttributeError) as exc:
        raise EventRejected(f"{field} must be a UUID") from exc


def redact(value):
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            if isinstance(key, str) and SECRET_KEY.search(key):
                cleaned[key] = "[REDACTED]"
            else:
                cleaned[key] = redact(item)
        return cleaned
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        return SECRET_VALUE.sub("[REDACTED]", value)
    return value


def hash_plan(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# These can happen again on the same attempt after correction.reopened.
REOCCURRENCE_TYPES = {
    "task.started",
    "task.files_changed",
    "verification.ran",
    "task.completed",
}


def default_source_event_id(run_id: str, attempt_id: str, event_type: str, data: dict) -> str:
    """Stable base id. An exact retry of the same base collapses.

    Task events also get an occurrence suffix from derived_source_event_id.
    """
    parts = [run_id, attempt_id, event_type]
    task_id = data.get("task_id")
    if task_id:
        parts.append(str(task_id))
    fingerprint = None
    if event_type == "verification.ran":
        fingerprint = f"{data.get('command', '')}\n{data.get('result', '')}"
    elif event_type == "task.files_changed":
        fingerprint = "\n".join(data.get("files") or [])
    elif event_type == "run.escalated":
        approved = "\n".join(data.get("approved_files") or [])
        fingerprint = f"{data.get('reason', '')}\n{approved}"
    elif event_type == "correction.reopened":
        fingerprint = str(data.get("target_event_id"))
    if fingerprint is not None:
        parts.append(hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:12])
    return ":".join(parts)


def _applied_reopen_count(record: dict, existing_events: list[dict]) -> int:
    task_id = record["data_redacted"].get("task_id")
    count = 0
    for prior in existing_events:
        if prior.get("event_type") != "correction.reopened":
            continue
        if prior.get("workspace_id") != record["workspace_id"]:
            continue
        if prior.get("source") != record["source"]:
            continue
        if prior.get("run_id") != record["run_id"]:
            continue
        if prior.get("attempt_id") != record["attempt_id"]:
            continue
        data = prior.get("data_redacted") or {}
        if not isinstance(data, dict) or data.get("task_id") != task_id:
            continue
        if data.get("status") not in (None, "applied"):
            continue
        count += 1
    return count


def derived_source_event_id(record: dict, existing_events: list[dict]) -> str:
    """Id used when the caller does not pass --source-event-id.

    For task.started, task.files_changed, verification.ran, and task.completed,
    the id ends in :n. n is how many applied correction.reopened events for
    that task are already in the log on this attempt. A retry before the next
    reopen still derives the same id and is rejected. After a reopen, n
    increases, so the next delivery is stored.
    """
    base = default_source_event_id(
        record["run_id"],
        record["attempt_id"],
        record["event_type"],
        record["data_redacted"],
    )
    if record["event_type"] not in REOCCURRENCE_TYPES:
        return base
    return f"{base}:{_applied_reopen_count(record, existing_events)}"


def build_data(options: dict) -> dict:
    data = {}
    if options.get("data_json"):
        try:
            extra = json.loads(options["data_json"])
        except json.JSONDecodeError as exc:
            raise EventRejected("--data-json must be a JSON object") from exc
        if not isinstance(extra, dict):
            raise EventRejected("--data-json must be a JSON object")
        data.update(extra)

    event_type = options["event_type"]
    if event_type == "run.started":
        plan_path = options.get("plan_path") or data.get("plan_path")
        if not plan_path:
            raise EventRejected("run.started requires --plan-path")
        plan_hash = options.get("plan_hash") or data.get("plan_hash")
        if not plan_hash:
            path = Path(plan_path)
            if not path.is_file():
                raise EventRejected(f"plan file not found: {plan_path}")
            plan_hash = hash_plan(path)
        data["plan_path"] = str(plan_path)
        data["plan_hash"] = str(plan_hash)
    if event_type in TASK_EVENTS:
        task_id = options.get("task_id") or data.get("task_id")
        if not task_id:
            raise EventRejected(f"{event_type} requires --task-id")
        data["task_id"] = str(task_id)
    if event_type == "task.files_changed":
        files = options.get("files") or data.get("files")
        if not files:
            raise EventRejected("task.files_changed requires at least one --file")
        data["files"] = [str(item) for item in files]
    if event_type == "verification.ran":
        command = options.get("command")
        if command is None:
            command = data.get("command")
        result = options.get("result") or data.get("result")
        if command is None or command == "":
            raise EventRejected("verification.ran requires --command")
        if result not in {"pass", "fail"}:
            raise EventRejected("verification.ran requires --result pass or fail")
        data["command"] = str(command)
        data["result"] = result
    if event_type == "run.escalated":
        reason = options.get("reason") or data.get("reason")
        if not reason:
            raise EventRejected("run.escalated requires --reason")
        data["reason"] = str(reason)
        approved = options.get("approved_files")
        if approved is None:
            approved = data.get("approved_files") or []
        data["approved_files"] = [str(item) for item in approved]
    if event_type == "run.completed":
        status = options.get("execution_status") or data.get("execution_status")
        if status is not None:
            if status not in EXECUTION_STATUSES:
                raise EventRejected(f"unknown execution status: {status}")
            data["execution_status"] = status
    if event_type == "correction.reopened":
        target = options.get("target_event_id") or data.get("target_event_id")
        if target:
            data["target_event_id"] = canonical_uuid(str(target), "target_event_id")
        elif "target_event_id" not in data:
            data["target_event_id"] = None
        source_target = options.get("target_source_event_id")
        if source_target is None:
            source_target = data.get("target_source_event_id")
        data["target_source_event_id"] = source_target
        data["scope"] = data.get("scope") or "this_run"
        data["status"] = data.get("status") or "applied"
        if options.get("requested_by"):
            data["requested_by"] = options["requested_by"]
    return redact(data)


def _delivery_key(event: dict) -> tuple:
    return (event["workspace_id"], event["source"], event["source_event_id"])


def append_event(log_path, event: dict) -> dict:
    """Append one event. Return an ack. Duplicates are not written again."""
    if fcntl is None:
        raise EventRejected("file locking requires a POSIX platform")
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    for field in (
        "workspace_id",
        "source",
        "run_id",
        "attempt_id",
        "event_type",
    ):
        if not event.get(field):
            raise EventRejected(f"missing {field}")
    if event["event_type"] not in EVENT_TYPES:
        raise EventRejected(f"unknown event type: {event['event_type']}")
    if not isinstance(event["source"], str) or not event["source"].strip():
        raise EventRejected("source must be a non-empty string")
    supplied_id = event.get("source_event_id")
    if supplied_id is not None and (
        not isinstance(supplied_id, str) or not supplied_id.strip()
    ):
        raise EventRejected("source_event_id must be a non-empty string")

    data = event.get("data_redacted", event.get("data", {}))
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise EventRejected("event data must be an object")

    observed = utc_now()
    occurred = parse_utc(event["occurred_at"]) if event.get("occurred_at") else observed
    record = {
        "event_id": canonical_uuid(event["event_id"], "event_id")
        if event.get("event_id")
        else str(uuid.uuid4()),
        "workspace_id": canonical_uuid(event["workspace_id"], "workspace_id"),
        "source": event["source"],
        "run_id": canonical_uuid(event["run_id"], "run_id"),
        "attempt_id": canonical_uuid(event["attempt_id"], "attempt_id"),
        "event_type": event["event_type"],
        "occurred_at": occurred,
        "observed_at": observed,
        "data_redacted": redact(data),
    }

    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        chunks = []
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            chunks.append(chunk)
        try:
            existing = b"".join(chunks).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise EventRejected(f"log is not UTF-8: {path}") from exc
        parsed = []
        for raw in existing.splitlines():
            if not raw.strip():
                continue
            try:
                prior = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise EventRejected(f"log contains a non-JSON line: {path}") from exc
            if not isinstance(prior, dict):
                raise EventRejected(f"log contains a non-object line: {path}")
            parsed.append(prior)
        if supplied_id:
            record["source_event_id"] = supplied_id
        else:
            record["source_event_id"] = derived_source_event_id(record, parsed)
        key = _delivery_key(record)
        for prior in parsed:
            try:
                prior_key = _delivery_key(prior)
            except KeyError as exc:
                raise EventRejected(f"log line is missing a delivery key: {path}") from exc
            if prior_key == key:
                return {
                    "status": "duplicate",
                    "event_id": prior.get("event_id"),
                    "run_id": prior.get("run_id"),
                    "attempt_id": prior.get("attempt_id"),
                    "source_event_id": prior.get("source_event_id"),
                }
        encoded = json.dumps(record, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        payload = encoded + "\n"
        if existing and not existing.endswith("\n"):
            payload = "\n" + payload
        os.write(fd, payload.encode("utf-8"))
        os.fsync(fd)
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)

    return {
        "status": "accepted",
        "event_id": record["event_id"],
        "run_id": record["run_id"],
        "attempt_id": record["attempt_id"],
        "source_event_id": record["source_event_id"],
        "observed_at": record["observed_at"],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Append one audit event as a JSON line.")
    parser.add_argument("--log", default=str(DEFAULT_LOG), help="JSONL log path")
    parser.add_argument("--type", required=True, dest="event_type", choices=EVENT_TYPES)
    parser.add_argument("--workspace-id", default=PILOT_WORKSPACE_ID)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--source", default="execute")
    parser.add_argument("--source-event-id")
    parser.add_argument("--plan-path")
    parser.add_argument("--plan-hash")
    parser.add_argument("--task-id")
    parser.add_argument("--file", action="append", dest="files")
    parser.add_argument("--command")
    parser.add_argument("--result", choices=("pass", "fail"))
    parser.add_argument("--reason")
    parser.add_argument("--approved-file", action="append", dest="approved_files")
    parser.add_argument("--occurred-at")
    parser.add_argument("--target-event-id")
    parser.add_argument("--target-source-event-id")
    parser.add_argument("--execution-status", choices=EXECUTION_STATUSES)
    parser.add_argument("--requested-by")
    parser.add_argument("--data-json", help="Extra JSON object merged into the event data")
    return parser


def main(argv=None) -> int:
    args = _parser().parse_args(argv)
    options = vars(args)
    try:
        data = build_data(options)
        payload = {
            "workspace_id": args.workspace_id,
            "source": args.source,
            "run_id": args.run_id,
            "attempt_id": args.attempt_id,
            "event_type": args.event_type,
            "occurred_at": args.occurred_at,
            "data_redacted": data,
        }
        if args.source_event_id:
            payload["source_event_id"] = args.source_event_id
        ack = append_event(args.log, payload)
    except EventRejected as exc:
        print(json.dumps({"status": "rejected", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(ack, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
