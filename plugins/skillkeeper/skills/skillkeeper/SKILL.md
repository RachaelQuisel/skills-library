---
name: skillkeeper
version: 1.0.6
description: Maintain or audit a repository of agent skills using named ownership, versioned inventories, sanitized regression tests, freshness evidence, controlled releases, rollback records, and failure alerts. Use when someone asks whether skills are current or trustworthy, wants to operationalize skill maintenance, needs to investigate a maintenance failure, or wants update and rollback controls.
---

# Skillkeeper

## Purpose in plain English

This skill helps you maintain a collection of skills with clear ownership, checks, update records, and evidence of problems.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Build evidence that a skill collection is maintained. Do not turn a green check into a broader claim than the recorded evidence supports.

Read [the maintenance contract](references/maintenance-contract.md) before changing a repository. Read [the alert policy](references/alert-policy.md) when checking or creating notifications.

## Start with the requested mode

Identify the repository, responsible owner, and requested mode from the conversation:

1. **Bootstrap** creates the maintenance structure for an existing collection.
2. **Health check** inspects inventory, coverage, freshness, workflow health, and release records.
3. **Failure investigation** explains a failed, missing, or stale check from recorded evidence.
4. **Release preparation** proposes a tested update or rollback without adopting it.

Ask only for missing information that changes the work. A scheduled check uses its saved repository, branch, workflow, and notification settings. It must report a missing required setting instead of guessing.

## Inspect before changing

1. Read repository instructions and the existing maintenance files.
2. Inventory actual skill entry points instead of assuming every directory is a skill.
3. Inspect current tests before running them. Check for network calls, production writes, secrets, and non-synthetic fixtures.
4. Record the exact branch and immutable commit being evaluated.
5. Preserve unrelated changes and existing skill behavior.

An inspection does not authorize edits, release adoption, external messages, or new schedules. Perform those actions only when the request includes them.

## Bootstrap a maintained collection

Create or extend the repository structure described in the maintenance contract. The minimum useful system includes:

- an inventory of every registered skill, its owner, exact baseline version, supported environments, freshness evidence, and regression coverage;
- a README for each registered skill that states its maintenance status and limits;
- a regression register with stable case identifiers;
- deterministic offline checks for inventory, required cases, skipped tests, versions, and documentation;
- a continuous integration workflow that runs on proposed and accepted changes, plus a periodic schedule;
- saved human-readable and structured evidence;
- release records with previous version, change reason, test evidence, approval, and rollback target;
- a notification policy for failures, missing successful runs, and stuck runs.

Do not automatically run every script in a repository. Register reviewed suites explicitly.

## Turn a failure into a regression

1. Capture the expected result, observed result, exact skill version, runtime, and evidence source.
2. Remove secrets, names, identifiers, customer content, and unnecessary fields. Prefer fully synthetic fixtures. Replacing names alone may not be sufficient.
3. Reproduce the failure with the old version.
4. Add a stable regression case that fails before the fix and passes after it.
5. Run the complete registered suite and the relevant live compatibility test when available.
6. Preserve the original failure record. Never delete a regression only to make the suite pass.

## Judge freshness honestly

Treat these as separate signals:

- **Repository freshness:** when instructions or code last changed.
- **Regression freshness:** when registered offline checks last passed.
- **Compatibility freshness:** when a named host, model, API version, and permission set were last verified live.

Only compatibility evidence supports a compatibility date. A workflow pass, README edit, or inventory refresh does not.

## Explain a failure

Use the run, job, step, log, artifact, and registered case evidence. Report:

1. the observed issue;
2. its impact on trust or coverage;
3. whether it is a failed assertion, dependency installation problem, permission problem, missing evidence, notification problem, or unknown;
4. a direct evidence link when available;
5. one next step.

Label facts, inference, and unknowns. Do not invent a root cause. A missing record does not prove success.

## Prepare updates and rollbacks

Use immutable commit identifiers. Prepare the candidate separately from the installed copy. Run the registered checks, document live compatibility evidence and remaining limits, and show the diff before adoption.

The responsible owner approves the release. Keep the previous version available. Rolling back skill instructions does not reverse business actions, migrations, or external API changes.

## Verify before reporting success

For repository changes, run the registered maintenance suite and validate the plugin or skill layout with the platform's supported validator. For notifications, verify a completed run and the configured delivery path. If access fails, report verification as unavailable. Never report the routine as healthy from missing data.

State exactly what was checked, what passed, what remains unverified, and who owns the next fix.
