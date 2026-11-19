---
name: audit-log-plugin
version: 1.4.6
description: >
  The automation run verifier reads the execute-skill pilot audit diary and
  reports Verified, Not achieved, or Unknown. Use when the user asks whether an
  execute run is verified, why a plan run did or did not count, or to reopen a
  green task that lacks a passing verification. Reopening is the separate
  correction tool, not the automation run verifier. For carrying out the plan
  itself, use the execute skill.
---

# Audit log plugin

## Purpose in plain English

This skill helps you check the evidence for a completed automation run and explain whether its result was verified.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


This is the first slice of the audit log: a pilot definition, the storage contract, and local event logging for the `execute` skill. Read `pilot.md` for the success predicate and the correction. Read `references/event-contract.md` for event names, ids, and state lists. The hosted table shapes live in `schema/001_init.sql`.

## Run the automation run verifier

The automation run verifier reads the diary and gives one of three answers: Verified, Not achieved, or Unknown. From the repo root:

```bash
python3 audit-log-plugin/scripts/automation_run_verifier.py \
  --plan PATH_TO_THE_PLAN \
  --log execute/.audit/events.jsonl
```

Pass `--run-id` when the log holds more than one run. The report's `business_outcome` is `verified`, `not_achieved`, or `unknown`. Do not treat `unknown` as success. Do not treat `applied` on a correction as `verified`.

## Reopen an unproven done task

Only when the operator asks to fix this run, and only for a task marked 🟩 that has no passing verification in the required window:

```bash
python3 audit-log-plugin/scripts/reopen_task.py \
  --plan PATH_TO_THE_PLAN \
  --log execute/.audit/events.jsonl \
  --task-id "TASK TITLE"
```

This edits that plan file and appends `correction.reopened` linked to the original `task.completed`. It does not edit code or create a commit. If the task has passing proof, the command refuses.

Logging during an execute run stays in `execute/SKILL.md` and `execute/scripts/log_event.py`.
