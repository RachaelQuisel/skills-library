---
name: execute
version: 1.0.1
description: Implement an existing plan step by step, updating the plan's emoji tracker as each step lands. Use when the user says "execute", "start building", "implement the plan", "go", or "begin", and a plan document already exists (typically from `create-plan` or `prd-to-plan`). This is the build phase of the align → create-plan → execute → deliver loop; for the planning phase itself, use `create-plan`.
tags:
  - skill
---
# Execute

## Purpose in plain English

This skill helps you carry out an existing plan step by step and update its progress as the work is verified.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Implement precisely as planned, in full. The plan is the contract — don't expand it, don't shortcut it.

## Why these rules exist

The discipline of separating plan from build is the whole point. The plan is where scope and decisions live; execution is where they get faithfully translated into code. Drifting from the plan mid-build undoes the work of planning and means the tracker no longer reflects reality. If the plan is wrong, stop and update it — don't quietly implement something different.

## Record the run

Record the run by calling `execute/scripts/log_event.py`. Do not write free-form audit notes. The script appends one UTC JSON line and rejects a duplicate `(workspace_id, source, source_event_id)`.

Use workspace `6f0d1c3a-7b2e-4a51-9c8d-0e1f2a3b4c5d`, source `execute`, and the same `--run-id` for the whole logical run. Mint a new `--attempt-id` only when you truly retry the run; reuse both ids on every event in that attempt. Omit `--source-event-id` unless you need a specific id. The script derives one from the run, attempt, event type, task, and payload, so an exact retry collapses. After a task is reopened on that same attempt, the next `task.started`, `task.files_changed`, `verification.ran`, and `task.completed` for it are stored instead of collapsed.

Mint the ids once, before the loop:

```bash
RUN_ID=$(python3 -c 'import uuid; print(uuid.uuid4())')
ATTEMPT_ID=$(python3 -c 'import uuid; print(uuid.uuid4())')
```

Before the loop, log `run.started` with the plan path. The script hashes the plan file. Do not list the plan file itself in `task.files_changed`; it is the tracker named by `run.started`.

```bash
python3 execute/scripts/log_event.py \
  --type run.started \
  --run-id "$RUN_ID" \
  --attempt-id "$ATTEMPT_ID" \
  --plan-path PATH_TO_THE_PLAN
```

A task is a checklist line that starts at column 0. `--task-id` is that line's title after the status emoji, without surrounding `**`. Indented subtasks are not separate tasks; do not mark or log them on their own. Progress percentage is the share of those top-level tasks marked 🟩, rounded to the nearest integer, half up.

Call the script from the repo root so the default log `execute/.audit/events.jsonl` is used.

## The loop

For each top-level task in the plan, in order:

1. Mark that task 🟨 In Progress in the plan file. Leave indented subtasks as they are. Update the overall progress percentage at the top. Then log `task.started` with `--task-id` set to the task title.
2. Read just enough surrounding code to match existing patterns. Don't refactor adjacent code unless the plan says to.
3. Implement the minimal change that satisfies the task. Match existing conventions — naming, structure, error handling. If this step changed files other than the plan tracker, log `task.files_changed` with one `--file` per changed path. Log `task.files_changed` again if a later fix changes more files.
4. Verify the task before marking it done. If the plan names a command (tests, build, type-check), run that command. If it names none, check the finished work against the task text and use command `review: TASK TITLE`. Log `verification.ran` with that command and `--result pass` or `--result fail`, including a failing run you then fix. Do not mark the task 🟩 unless a passing verification for it sits after the last file change.
5. Mark the task 🟩 Done. Update the percentage. Then log `task.completed` with the same `--task-id`.
6. Move to the next task.

When the loop finishes, log `run.completed`.

```bash
python3 execute/scripts/log_event.py \
  --type task.started \
  --run-id "$RUN_ID" \
  --attempt-id "$ATTEMPT_ID" \
  --task-id "TASK TITLE"

python3 execute/scripts/log_event.py \
  --type task.files_changed \
  --run-id "$RUN_ID" \
  --attempt-id "$ATTEMPT_ID" \
  --task-id "TASK TITLE" \
  --file path/to/changed-file

python3 execute/scripts/log_event.py \
  --type verification.ran \
  --run-id "$RUN_ID" \
  --attempt-id "$ATTEMPT_ID" \
  --task-id "TASK TITLE" \
  --command "the command you ran" \
  --result pass

python3 execute/scripts/log_event.py \
  --type task.completed \
  --run-id "$RUN_ID" \
  --attempt-id "$ATTEMPT_ID" \
  --task-id "TASK TITLE"

python3 execute/scripts/log_event.py \
  --type run.completed \
  --run-id "$RUN_ID" \
  --attempt-id "$ATTEMPT_ID"
```

## When to stop and surface

Pause and surface to the user instead of improvising when:
- A plan step turns out to be wrong, ambiguous, or blocked by something the plan didn't anticipate.
- A test fails and the failure isn't trivially this-step's-doing.
- You'd need to expand scope (touch a new file, change an interface) to complete the task.

Don't quietly rewrite the plan. Name the issue, propose the change, wait. Before you pause, log `run.escalated` with `--reason`. If the user approves a file the plan did not name, pass each approved path with `--approved-file` on that event. Do not log `run.completed` until you stop working the plan.

```bash
python3 execute/scripts/log_event.py \
  --type run.escalated \
  --run-id "$RUN_ID" \
  --attempt-id "$ATTEMPT_ID" \
  --reason "what blocked the step" \
  --approved-file path/the/user/approved
```

## What not to do

- No extra scope. If you notice an unrelated issue, log it for later; don't fix it now.
- No new abstractions, helpers, or refactors the plan didn't ask for.
- No emoji-only updates without the actual work. The tracker must reflect reality.
- No bulk completion of multiple steps before running verification — one task at a time.
