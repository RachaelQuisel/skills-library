# Event contract

Pilot source: `execute`. Pilot workspace: `6f0d1c3a-7b2e-4a51-9c8d-0e1f2a3b4c5d`. Local log: `execute/.audit/events.jsonl`, one JSON object per line. The hosted shape of the same facts is `schema/001_init.sql`.

## Identifiers

| ID | Role |
| --- | --- |
| `workspace_id` | Tenant boundary. Part of the delivery key. |
| `run_id` | One logical execute run. Reused across real retries. |
| `attempt_id` | One real retry. A new attempt gets a new id; events in that try reuse it. A correction is not a retry and keeps the original attempt id. |
| `event_id` | UUID minted when the line is first stored. |
| `source` | Producer name. The pilot uses `execute`. |
| `source_event_id` | Producer's id for this delivery. |

`run.started` carries `plan_path` and `plan_hash` (SHA-256 of the plan file bytes). A task is a checklist line that starts at column 0. `--task-id` is that line's title after the status emoji, without surrounding `**`. Indented subtasks are not tasks.

If `--source-event-id` is omitted, the script derives one. `run.started`, `run.completed`, and `run.escalated` use the run, attempt, event type, and the payload that distinguishes a different command, file list, or reason. An exact redelivery of that payload collapses.

`correction.reopened` uses that same base plus the `target_event_id` of the `task.completed` it corrects. A later reopen of a new completion is a different event. Retrying the same target collapses, so the reopen count does not increase and the next `task.completed` keeps the same `:{n}` suffix.

`task.started`, `task.files_changed`, `verification.ran`, and `task.completed` use that same base and then append `:{n}`. `n` is the number of applied `correction.reopened` events already stored for that workspace, source, run, attempt, and task. Before any reopen, `n` is 0, so a retry is still a duplicate. A reopen keeps the same attempt id; after it is stored, `n` increases and the next delivery of those task events is recorded. A retry of that new delivery is a duplicate again. A caller-supplied `--source-event-id` is stored unchanged and does not gain `:{n}`.

## Timestamps

`occurred_at` and `observed_at` are UTC ISO-8601 with a `Z` suffix. `observed_at` is when the script accepted the line. `occurred_at` defaults to that same instant. Naive and non-UTC timestamps are rejected.

The script prints an acknowledgement only after `fsync`, or after it has found the existing line under the file lock. Duplicate acknowledgement returns the original `event_id` and does not append. Exit `0` means accepted or duplicate. Exit `2` means rejected and not written.

## Delivery key

Canonical uniqueness is `(workspace_id, source, source_event_id)`. The same key in another workspace is a different event. The same key with a different payload is still a duplicate: the first stored body wins.

Secrets are redacted before the line is stored. Object keys that look like passwords, tokens, API keys, or credentials become `[REDACTED]`. Bearer tokens and common token prefixes inside strings are replaced the same way.

## Event types

| Event | Required data |
| --- | --- |
| `run.started` | `plan_path`, `plan_hash` |
| `task.started` | `task_id` |
| `task.files_changed` | `task_id`, `files` (one path per changed file other than the plan tracker) |
| `verification.ran` | `task_id`, `command`, `result` (`pass` or `fail`) |
| `task.completed` | `task_id` |
| `run.escalated` | `reason`. Optional `approved_files`. |
| `run.completed` | None. Optional `execution_status`. |
| `correction.reopened` | `task_id`, `target_event_id`, `target_source_event_id`, `scope` (`this_run`), `status`, `requested_by` |

`correction.reopened` links to the original `task.completed`. It does not delete or edit that line.

The plan file named on `run.started` is an allowed edit because the skill has to update the tracker. Every other changed path must appear in the plan text or in `approved_files`.

## State lists

Execution status: `queued`, `running`, `waiting`, `completed`, `failed`, `cancelled`, `unknown`.

Business outcome: `verified`, `not_achieved`, `unknown`.

Telemetry health: `current`, `delayed`, `incomplete`, `unavailable`, `unknown`.

Correction status: `requested`, `authorized`, `applied`, `verified`, `failed`, `rejected`.

Correction scope: `this_run`, `future_behavior`.

Evidence-link role: `supporting`, `contradicting`, `context`.

Applied is not the same as verified. A timeout does not prove that a remote write failed. Missing outcome evidence is `unknown`, not `verified` and not `not_achieved`.

## Automation run verifier order

For each done top-level task, take the latest `task.files_changed` and the latest `task.completed` by `(occurred_at, line order)`. A passing `verification.ran` must sit strictly after that file change (if any) and strictly before that completion. A pass or fail outside that window is missing proof (`unknown`), not a recorded failure. A `fail` inside the window, with no `pass` inside it, is `not_achieved`. An empty window is `unknown`, not `verified`. A late duplicate delivery does not create a second canonical event. After a reopen, the occurrence suffix makes the next task delivery a new canonical event. The automation run verifier (`audit-log-plugin/scripts/automation_run_verifier.py`) reads the diary and applies this order.
