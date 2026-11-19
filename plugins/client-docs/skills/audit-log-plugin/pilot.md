# Execute skill audit pilot

The pilot automation is the `execute` skill (`execute/SKILL.md`). It carries out a markdown plan task by task, marks tasks 🟥, 🟨, or 🟩, and updates the progress percentage. This slice records that work in a local append-only log. The automation run verifier reads that diary and gives one of three answers: verified, not achieved, or unknown. It does not deploy a collector or a hosted database.

## Trigger

A person asks the agent to execute, start building, implement the plan, go, or begin, and a plan document is already present. There is no schedule and no deadline. `expected_by` stays empty. A run that never starts is not detectable from a clock; there is nothing to expect until someone invokes the skill.

## Systems

- The plan file. A task is a checklist line that starts at column 0 with a checkbox and a 🟥, 🟨, or 🟩 emoji. Indented subtasks, including the ones in the `create-plan` template, are not tasks. `execute` flips the top-level line only, and the progress share counts only those lines.
- The workspace files the plan names.
- `execute/scripts/log_event.py`, called by the skill. The skill does not write free-form audit notes.
- The local log `execute/.audit/events.jsonl` (override with `--log`).
- A verification for every task. If the plan names a command, that command is the verification. If it names none, `execute` checks the finished work against the task text and logs `verification.ran` with command `review: <task title>`. A normal `create-plan` document can therefore reach `verified` without a test command on every task. `review: <task title>` is self-attested: the same agent reports that it checked the work. That is weaker evidence than a command the plan named, such as tests, a build, or a type-check. The owner can decide later whether to stop treating it as proof.

Workspace id for this pilot: `6f0d1c3a-7b2e-4a51-9c8d-0e1f2a3b4c5d`. Source: `execute`.

## Success predicate

A finished run is **verified** only when all of the following are true:

- Every top-level task in the plan is 🟩.
- Each of those tasks has a passing `verification.ran` after its last `task.files_changed` and before its latest `task.completed`. A task with no file-change event still needs a passing verification before `task.completed`. A pass or fail that sits outside that window does not count.
- The progress percentage equals the share of top-level tasks marked 🟩, rounded to the nearest integer, with halves rounding up.
- Every changed file, other than the plan file named on `run.started`, is named in the plan or listed in `approved_files` on a `run.escalated` event for that run.

The automation run verifier is `audit-log-plugin/scripts/automation_run_verifier.py`. It reads the diary and gives one of three answers: `verified`, `not_achieved`, or `unknown`.

Missing evidence is **unknown**, not verified. That includes a run with no `run.completed`, a 🟩 task with no in-window verification result (nothing logged, or only results that sit outside the window), a log that cannot be read, and a plan that cannot be parsed. A `verification.ran` with result `fail` inside the window, a task that is not 🟩, a progress percentage that does not match, or a changed file that was neither named nor approved is **not_achieved**.

Execution status, business outcome, and telemetry health stay separate fields in the automation run verifier report and in the storage contract.

## Correction

One correction type: reopen a task marked 🟩 without passing proof.

- Scope is this run's plan file. The script sets that task back to 🟥, unchecks it, and recomputes the progress percentage.
- It appends `correction.reopened` on the same run and attempt, linked to the original `task.completed` by `target_event_id` and `target_source_event_id`.
- It does not edit code, does not create commits, and does not change future skill behavior. A future-behavior change would be a new rule version, which this correction does not create.
- If the task already has passing proof, the script refuses and leaves the plan untouched.
- Applied is not verified. After a readback of the plan, the event status is `applied`. It is not marked `verified`.

Command: `python3 audit-log-plugin/scripts/reopen_task.py --plan PATH --log PATH --task-id "TASK TITLE"`.

## Authorization

The workspace operator authorizes the correction by invoking that command (or explicitly asking for that reopen) for a named task. The script's write authority is the named plan file and the log. It has no authority to change any other file.

## Retention and history

Event rows are kept for 30 days after `observed_at`. The log script and the SQL contract append events; they do not rewrite them. A later rule version does not replace the snapshot a run already points at. See `schema/001_init.sql` and `references/event-contract.md`.

## Out of scope for this slice

Hosted collector, connected chat tools, notifications, cross-workspace investigation, and any correction other than the reopen above.
