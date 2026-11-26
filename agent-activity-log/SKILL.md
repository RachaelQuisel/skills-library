---
name: agent-activity-log
description: Scaffold and operate an opt-in Agent activity log table that records what the agent did, decided, and got blocked on across a long-running or multi-session Airtable workflow. Use whenever a workflow skill is being set up for an agent-driven motion (recurring triage, multi-step plan, automated monitoring, agentic workflow), or when the user asks for "agent activity tracking," "audit log of agent decisions," "agent memory," "track what the agent did," or similar. Opt-in — disclose before scaffolding.
license: MIT
metadata:
    version: 1.0.3-rq.1
    upstream_author: airtable
    upstream_version: '1.0.0'
    local_fork: rachael-quisel
    forked: 2026-08-10
---

# Agent activity log

## Purpose in plain English

This skill helps you keep a record of an assistant's actions, decisions, and unresolved problems during a workflow.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


A typed audit log of agent decisions, blockers, and outcomes. Opt-in for users who are explicitly building an agent-driven workflow. Humans and the next agent session can read back what the agent did and why, without trusting a context-window summary that may be gone by then.

This skill owns the schema and the disclosure language. Workflow skills compose this skill rather than re-implementing the pattern.

## Local fork notice

This is a forked copy of `airtable/skills/plugins/airtable/skills/agent-activity-log` (upstream v1.0.0, MIT), edited on 2026-08-10 for Rachael's environment. Changes:

1. Field-ID discipline baked in (Rachael's rule 14 + `~/.claude/rules/airtable-best-practices.md`).
2. `Timestamp` corrected from `createdTime` to `dateTime` populated by the agent — `createdTime` cannot be created via the REST API (§2 of best-practices).
3. Write-format rules added (singleSelect bare-name in REST vs. object in Scripting API; no `typecast: true`; batch cap of 10).
4. Read-back rule added (`returnFieldsByFieldId=true`; requested fields must include every field the code compares against).
5. Disclosure language rewritten in plain English (Rachael's voice; no first-person-as-agent throat-clearing).
6. Boundary named vs. Rachael's existing `Automation Inventory` / `Change Log` pattern on client bases.
7. Session-ID format specified.
8. Recursion note added.

Do not push to `airtable/skills` upstream. Sync only to Rachael's own skills repo when the standing `no-github-creation-pause` lifts.

## When this fires

Trigger phrases:

- "track what the agent is doing," "agent activity log," "audit log of agent decisions"
- "long-running workflow," "agent memory," "persistent state for the agent"
- "keep a record of what changed and why"
- Setup-mode invocations describing an agent-driven motion: "I want the agent to triage feedback every morning," "the agent should propose changes for me to approve," "set up a self-running workflow"

Surface proactively when the user's language signals they're building something the agent will run repeatedly or autonomously — not for one-shot interactions.

## Disclosure (opt-in, plain English)

Front-load the offer. The user agrees or declines; either is fine. Frame it as a table THEY get to read, not as the agent talking about itself.

Suggested language (adapt to the user's actual base and vocabulary):

> "This adds a table called `Agent activity log` to your base. Every meaningful decision or blocker gets one row, with a plain-English summary of what happened and why, plus links to the records that were touched. You can open it any time to see what got changed and where I got stuck. It's opt-in — say no and we skip it. Want it in?"

For Rachael's non-technical clients (Dana, Chris, Pat), use their actual base name and skip the word "agent." Example: "adds a table called `System Activity Log` to your Example Nonprofit base."

Frame as auditability for the user's benefit. Not surveillance.

## Schema

One `Agent activity log` table. Keep it out of stakeholder-facing Interfaces — this is internal audit data for the operator, not content the broader team should browse in the app.

### Core fields

Field-type notes and the reason each was chosen.

- **`Summary`** — `singleLineText`, primary. One-line what-happened.
- **`Timestamp`** — `dateTime`, includeTime true, timeZone UTC, dateFormat ISO. The agent populates this at write time. **Do not use `createdTime`** — that type cannot be created via the REST API (per airtable-best-practices §2). If the base is scaffolded via UI/Omni instead of API, `createdTime` is a reasonable alternative; the tradeoff is losing the agent's ability to backfill or replay entries with the original event time.
- **`Action`** — `singleSelect`. Minimum choices for auditability: `Decision`, `Blocker`, `Question`, `Error`, `Completion`. Add `Read`, `Create`, `Update`, `Delete` only if the workflow's audit story specifically needs them (usually it doesn't — see anti-patterns).
- **`Reasoning`** — `multilineText`. What the agent intended and why, including inputs considered and alternatives rejected.
- **`Outcome`** — `singleSelect`. Choices: `Completed`, `Partial`, `Failed`, `Blocked`.
- **`Status`** — `singleSelect`. Choices: `Open`, `Acknowledged`, `Resolved`, `Stale`. For blockers and questions that need human follow-up. Leave blank for entries that don't need follow-up.
- **`Session ID`** — `singleLineText`. Format: `YYYY-MM-DDTHH:MM:SS-<8char-random>` (example: `2026-08-10T14:32:07-a9k3lmqp`). Populated once at session start and reused for every write in that session. Uniqueness comes from the random suffix; the leading timestamp lets you sort sessions chronologically.

### ID discipline (non-negotiable — Rachael's rule 14)

The moment the table is scaffolded, capture the IDs of every field and the table itself. From then on, every reference in code, docs, automations, and this skill's own operational notes uses IDs first, names in parens.

Documentation format (Rachael's convention):
`Agent activity log (tblXXXXXXXXXXX) . Summary (fldXXXXXXXXXXX)`

The scaffolding routine should end with a printed block that the operator saves to the client's `Data Dictionary` and `schema-dependencies.md`:

```
Agent activity log (tblXXXXXXXXXXX)
  Summary        fldXXXXXXXXXXX  singleLineText
  Timestamp      fldXXXXXXXXXXX  dateTime
  Action         fldXXXXXXXXXXX  singleSelect
    Decision     selXXXXXXXXXXX
    Blocker      selXXXXXXXXXXX
    Question     selXXXXXXXXXXX
    Error        selXXXXXXXXXXX
    Completion   selXXXXXXXXXXX
  Reasoning      fldXXXXXXXXXXX  multilineText
  Outcome        fldXXXXXXXXXXX  singleSelect
  Status         fldXXXXXXXXXXX  singleSelect
  Session ID     fldXXXXXXXXXXX  singleLineText
  Target table   fldXXXXXXXXXXX  singleSelect
  Target record URL  fldXXXXXXXXXXX  url
  Linked <TableA>    fldXXXXXXXXXXX  multipleRecordLinks -> tblA
  Linked <TableB>    fldXXXXXXXXXXX  multipleRecordLinks -> tblB
  ...
```

### Linking to records the agent touched

Airtable's `multipleRecordLinks` field is bound to a single target table at field-creation time — there is no polymorphic linked-record field. Two viable patterns:

1. **Per-target linked-record fields (recommended)** — one `multipleRecordLinks` field per table the agent might touch. The agent populates whichever field matches; the others stay empty. Gives reverse-link navigation on the target record automatically.
2. **URL-only fallback** — a single `Target record URL` field holding the deep-link. No reverse-link navigation, simpler schema.

Most builds combine both: pattern 1 for the 3-5 tables touched most, pattern 2 as fallback for ad-hoc touches. Add a `Target table` (`singleSelect` of the workflow's tables) so a viewer can see which kind of record an entry touched without clicking through.

**Externally synced tables:** linking FROM the `Agent activity log` TO a synced target table works fine — the linked-record field lives on the log side. Writes to synced fields still 403, but this pattern doesn't do that.

## Writing entries — Airtable API rules

Every write MUST follow the API rules in `~/.claude/rules/airtable-best-practices.md`. The ones this skill hits:

1. **Field IDs only** in the write payload. Never field names.
2. **`singleSelect` write format:**
   - Raw REST / `mcp__airtable*` / `mcp__airtable-pat*`: value is a **bare name string**. Example: `"Decision"`.
   - Airtable Automation Run Script (Scripting API): value is an **object** `{name: "Decision"}`.
   These are opposite; both are verified live in the best-practices doc.
3. **No `typecast: true` in production writes.** Ever. It silently mints new choice options on a surprise value. Validate the value against a known-good list at write time and refuse to write if it isn't in the list.
4. **Batch cap is 10** records per POST/PATCH. The skill should never build a request of >10 records; chunk if needed.
5. **Externally synced tables:** any direct write returns 403 "Edits to synced field are not allowed from this origin." The `Agent activity log` itself will never be synced, but if the operator later syncs it to a downstream base, writes must go to the source.

## Reading entries back — Airtable API rules

If the skill ever reads log entries (e.g., to check whether the current `Session ID` already has a session-start row before writing another):

1. **Raw REST defaults to field NAMES.** A GET without `returnFieldsByFieldId=true` returns a `fields` dict keyed by name. Code like `record["fields"]["fldXXX"]` will silently return None. Every raw REST GET (list, per-record, pagination follow-ups) must include `returnFieldsByFieldId=true`. `mcp__airtable*` and airtable-cli return `cellValuesByFieldId` and are immune.
2. **Fetch every field the code will compare against.** The API returns only the fields listed in `fields[]`. An unrequested field reads as None and any equality check against it becomes dead code.

## Use guidance (during a session)

Write events as decisions are made or blockers surface. Pattern:

1. **At session start:** write an `Action = Completion`, `Outcome = Completed` entry with a `Summary` describing what the session is starting on. The `Session ID` chosen here ties the rest of the session together.
2. **On each meaningful decision:** `Action = Decision`. Full reasoning in `Reasoning`. Include alternatives considered and why they were rejected.
3. **On blockers:** `Action = Blocker`, `Status = Open`, link to affected records.
4. **On questions for the human:** `Action = Question`, `Status = Open`, link to affected records. The human answers by setting `Status = Acknowledged` and adding a comment on the record.
5. **On errors:** `Action = Error`, `Outcome = Failed`, error context in `Reasoning`.
6. **At session end:** `Action = Completion` with a `Summary` of session outputs and unresolved items.

Log meaningful decisions and changes. Not every tool call. Reads in particular usually don't need to be logged.

## Composition with Rachael's existing `Automation Inventory` / `Change Log`

Rachael's client bases (CC, EA, EH) already carry an `🤖 Automation Inventory` or per-client `Change Log` table as part of the Seven Deliverables (`~/.claude/rules/seven-deliverables.md`, item 6). Before scaffolding a new `Agent activity log`, check whether that table already exists. Two patterns:

**Pattern A — Parallel tables (recommended default).** Keep both. Different jobs:
- `Automation Inventory` / `Change Log` = human-authored, per-script-run summary written as part of the Seven Deliverables. Coarse-grained. One row per apply-run.
- `Agent activity log` = agent-authored, per-decision or per-blocker. Fine-grained. Multiple rows per session.

**Pattern B — Extend the existing table.** Add `Reasoning`, `Session ID`, `Status`, and the per-target linked fields to the existing `Automation Inventory` / `Change Log`. Reduces table sprawl; couples two different grain sizes into one schema. Only choose this if the base already has fewer than ~15 tables and the existing changelog table is under-used.

Ask the user which they want before scaffolding.

## Recursion note

The skill's own writes are Airtable operations. If a `PostToolUse` hook is ever wired to auto-log every Airtable MCP call, it MUST exclude writes to the `Agent activity log` table itself (match on the target `tbl` ID in the tool call payload) or the log will fill with entries about writing to the log.

## Composition into workflow skills

Any workflow skill (product-ops, sales-ops, marketing-ops, etc.) should:

1. Surface this pattern to the user when the trigger phrases above appear.
2. Compose `agent-activity-log` — don't re-implement the schema inline.
3. Pass through workflow-specific context — the tables the agent will be touching — so per-target linked-record fields get scaffolded for the right tables.
4. Hand off at session end with a link to the `Agent activity log` table (or an Interface view filtered to the current `Session ID`).

## Anti-patterns

- **Don't auto-create `Agent activity log` without disclosure.** Trust erodes when imposed.
- **Don't specify `Timestamp` as `createdTime` when scaffolding via API.** It won't create. Use `dateTime` populated by the agent.
- **Don't set `typecast: true` on writes.** Ever.
- **Don't build a POST/PATCH with more than 10 records.**
- **Don't read the log back without `returnFieldsByFieldId=true` on raw REST.**
- **Don't claim polymorphic linked-record fields.** Airtable's `multipleRecordLinks` binds to one target table.
- **Don't conflate the agent log with the workflow's normal tables.** Agent activity log = what the agent did while helping. Workflow tables = what the team is working on.
- **Don't over-log.** Meaningful decisions and changes only. Reads usually don't count.
- **Don't reference fields by name anywhere after scaffolding.** IDs first, names in parens.
- **Don't surveillance-frame the disclosure.** Auditability for the user's benefit, not monitoring the agent for its own sake.
