---
name: update-projects
version: 1.0.1
description: Set up and reconcile Projects, Outcomes (Objectives), and Tasks for a client into XRAY's upstream Projects & Tasks at XRAY base (appQAdxI2hDNJj1g5). Records sync down to per-client planning bases automatically. Use when Rachael says "set up the build plan in my planning base", "push the projects, outcomes, and tasks to Airtable", "the outcomes table is empty", "create the projects, outcomes, and tasks", "push the build doc to the planning base", or whenever she has a Project → Outcome → Task build doc and wants it reflected in her planning Airtable base. Also use to dedupe duplicated task records or reconcile a build doc against existing records.
tags:
  - skill
---

# Update Projects, Outcomes, and Tasks for a Client

## Purpose in plain English

This skill helps you reconcile a client's projects, intended results, and tasks in XRAY's work-tracking system.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Set up and maintain the standard XRAY build-plan hierarchy (Projects → Outcomes → Tasks) for a client. All writes land in the upstream **`appQAdxI2hDNJj1g5` ("Projects & Tasks at XRAY")** base. Records sync down to the per-client planning base within ~30-60 seconds.

## Constants

Pulled to the top so they aren't repeated inline throughout the skill.

- **Source base:** `appQAdxI2hDNJj1g5` — "Projects & Tasks at XRAY"
- **Projects table:** `tblOaFlYpPXlHrT2c`
- **Objectives table:** `tblyZxi1nYrGICXrf` (synced to client bases as `Outcomes`)
- **Tasks table:** `tblvlJq7I2GvIQEyP`
- **Clients table:** `tblVS1aUCNeqtVq5U`
- **Rachael's user ID** (Owner, Project/Account Manager, Assigned To): `usr5vnH7D87XIP57C`. Always use object form `{"id": "usr5vnH7D87XIP57C"}` for collaborator fields — bare string returns HTTP 422 `INVALID_VALUE_FOR_COLUMN` (verified 2026-05-27).

## Routing rule (read first — REWRITTEN 2026-07-30, supersedes everything below)

**ONE route: `tasks.xray.tech/api`. Rachael, 2026-07-30: "you cannot touch projects and tasks base, only tasks.xray.tech." No Airtable MCP writes to `appQAdxI2hDNJj1g5`. No REST. No exceptions, no interim caveat.** See memory `tasks-only-via-xray-tasks-api`.

- **Tasks** → `tasks.xray.tech/api` with `X-Api-Key: $(cat ~/.config/xray/tasks-api-key)`. Create, accept, patch, reject. Follow the `create-task` skill's Hard Rules on every create: project resolved, outcome named in the description (v1 can't write the link), canonical priority (`"Medium"`/`"High"` write values only), mandatory same-title-same-project dedupe first.
- **Projects — create/update is BLOCKED.** The v1 API only exposes `GET /api/projects?q=<name>` (search, min 2 chars, max 10 results). Report the block to Rachael; she edits in the Task Inbox UI or it waits for tasks.xray.tech v2. Do NOT use MCP.
- **Outcomes — create/update is BLOCKED.** The v1 API only exposes `GET /api/outcomes?projectId=<recId>`. Same handling: report, UI, or v2. Do NOT use MCP.
- Reads for reconnaissance also go through the API where it covers them. If the API fails, **report the error and stop**.

**Any instruction below this point that says to write via `mcp__airtable__*` is RETIRED.** It's kept for historical field-shape reference only (select-option strings, collaborator format) — those details feed the v2 build, not live writes.

The `~/.config/xray/airtable-tasks-pat` file has been deleted from the local filesystem. If you find yourself about to write code that reads it, stop — you're on the wrong path. Old scripts that used it were deleted from `references/`; see the Reference scripts section below.

## Why the per-client base isn't the write target

A per-client planning base (e.g., `Guardians of Love and XRAY` at `appQ2DVUVGLq7mFg9`) **looks like** Rachael's project-management environment, but its key tables are externally synced and **read-only**. Direct writes to those synced tables fail with:

```
403 INVALID_PERMISSIONS: Your record could not be created because the underlying table is externally synced
```

Always write upstream to `appQAdxI2hDNJj1g5`. The client base is a viewing layer.

| Source table (writable, at `appQAdxI2hDNJj1g5`) | Source ID | Synced to client base as | Write route |
|---|---|---|---|
| Projects | `tblOaFlYpPXlHrT2c` | `⚡️ Projects` | Airtable MCP |
| Objectives | `tblyZxi1nYrGICXrf` | `Outcomes` (renamed on sync) | Airtable MCP |
| Tasks | `tblvlJq7I2GvIQEyP` | `Tasks at XRay` | `tasks.xray.tech/api` |
| XRay's Clients | `tblVS1aUCNeqtVq5U` | `XRay's Clients` | `GET /api/clients` (read); MCP (create, rare) |

## Credentials and "remove" semantics

**Credentials**
- **tasks.xray.tech API key** at `~/.config/xray/tasks-api-key`. Sent as `X-Api-Key` header.
- **Airtable MCP** uses default OAuth; nothing to load from disk.

If Rachael pastes a token in chat, flag the exposure once, then proceed if she overrides. Recommend she rotate after the session.

**Neither route supports DELETE for these tables.** How to "remove" a record depends on the table — the valid Status options differ, so a one-size instruction would silently store an invalid value (exactly the bug the "Priority" gotcha describes). Use the table-specific recipe below.

| Table | To "remove" | Which route |
|---|---|---|
| **Projects** | `Status: Cancelled` | MCP `update_records_for_table` on `tblOaFlYpPXlHrT2c`. `Cancelled` is a valid option. |
| **Objectives** | `Archived: true` (there is no `Cancelled` option — valid Status values are `Backlog`, `Blocked`, `Ready to Start`, `In Progress`, `In Testing` only) | MCP `update_records_for_table` on `tblyZxi1nYrGICXrf`. |
| **Tasks** | Two-part write: `Triage Status: Rejected` (via `tasks.xray.tech PATCH`) **AND** `Archived: true` (via MCP). No `Cancelled` in Task Status. `tasks.xray.tech PATCH` does not accept `Archived`, and MCP is needed for that side of the write. Verified 2026-06-13. | See both routes above. |

**Collaborator fields** (Owner, Project/Account Manager, Assigned To) are single-collaborator fields. Always use object form `{"id": "usr5vnH7D87XIP57C"}` — never a bare string, never a name. Using the object form is what:

- Makes the records show up in `/tasks/mine` and any "Assigned to Rachael" filtered views
- Triggers owner-based notifications (Slack DMs, daily task digests, etc.)
- Lets the "X tasks assigned to me" rollups behave correctly

See `references/field-schemas.md` for the full field list per table.

## Workflow

1. **Verify routes.** Confirm `mcp__airtable__*` tools are attached and `~/.config/xray/tasks-api-key` exists. If either is missing, stop and surface — do not proceed.
2. **Find client.** `GET https://tasks.xray.tech/api/clients` (with `X-Api-Key`) to look up client record ID. Or via MCP: `list_records_for_table` on the Clients table with a `contains` filter on `Name`. Don't duplicate — match on the exact client name Rachael names.
3. **Check existing projects** for the client via `GET /api/projects?q=<client name>`. Decision rule:
   - If a project's `Project name` **exact-matches** one in the build doc → PATCH it (via MCP) to update fields; don't create a duplicate.
   - If the build doc names a **new workstream** the client doesn't have yet → create it alongside the existing ones.
   - If ambiguous (partial name overlap, e.g., "GoL Compliance" vs. "GoL Compliance Automation"), ask Rachael before creating.
4. **Create projects** via `mcp__airtable__create_records_for_table` on the Projects table. Batch up to 50 in one call. Include `Origin Detail: "Claude Code — [Client] build batch [YYYY-MM-DD]"` on every record for later idempotency checks.
5. **Create objectives** via `mcp__airtable__create_records_for_table` on the Objectives table, each linked to its project and to the client. Batch up to 50. Same `Origin Detail` batch tag.
6. **Identify any existing tasks to re-link.** Query `GET /api/tasks/mine` or `mcp__airtable__list_records_for_table` on the Tasks table filtered by `contains` on `Origin Detail` (looking for prior batch tags for this client, or for tasks pushed earlier in this build). These are the tasks that already exist in the source and need their `Outcomes` link pointed at the new objectives.
7. **Create or link tasks.**
   - **New tasks** (from the build doc, not yet in the source): `POST https://tasks.xray.tech/api/tasks` — one per call, sleep 0.4s between (API has no batch endpoint).
   - **Existing tasks to re-link** (from step 6): `PATCH https://tasks.xray.tech/api/tasks/:id` for the `project` field only. To set the `Outcomes` link, use MCP `update_records_for_table` on the Tasks table (the tasks.xray.tech PATCH doesn't expose `Outcomes`). MCP handles up to 50 per batch.
8. **Verify sync.** Wait 30-60 seconds, then read the per-client planning base via MCP to confirm records appeared.
9. **If you re-ran a bulk-create for any reason**, reconcile duplicates by fetching records with the current batch tag and comparing against the canonical build doc. The Tasks API and MCP creates do not check for prior writes; re-running silently doubles the record count.

For full field-level details, see `references/field-schemas.md`.

For a step-by-step rerun of the GOL playbook (with the actual HTTP failures and root causes), see `references/diagnostic-playbook.md`.

## Critical select-option strings

These are strict. Wrong values either 502 or store as invalid strings that filter records out of views.

- **Tasks Priority** (read-format only): `P0: Urgent & Critical`, `P1: Top Priority`, `P2: Medium Priority`, `P3: Low Priority`, `P4: Lowest Priority`. Sending `"High"` succeeds silently but stores literally outside any valid option, hiding the task from `/tasks/mine` and other priority filters.
- **Objectives Priority**: `Low`, `Medium`, `High`, `On Fire`
- **Projects Priority**: `Low`, `Standard`, `High`
- **Project Type** (use this for client work): `Consulting Solution Sprints`
- **Visibility** (Objectives): `Internal (XRay) Only` or `Visible to public`. Default to internal.

Map build-doc priority levels: 1 → High / `P1: Top Priority`; 2 → Medium / `P2: Medium Priority`; 3 → Low / `P3: Low Priority`.

## Where MCP is narrower than raw Airtable REST — and how to stay in MCP

MCP covers everything the PAT did except two specific query patterns. Both have in-MCP workarounds; neither is a reason to reach for the PAT.

### 1. No `view=<viewId>` param

MCP's `list_records_for_table` has no `view` param. You can't say "give me the records in view `viwXXX`" and inherit that view's filter/sort/group setup.

**Workaround:** replicate the view's logic in the MCP filter DSL.

- Open the view in Airtable, note its filters and sort.
- Translate each filter to a `{operator, operands}` clause. Most Airtable UI filters map 1:1 (`is`, `contains`, `is any of`, date ranges → `=`, `contains`, `isAnyOf`, `isWithin`).
- Combine with `{operator: "and", operands: [...]}` at the top.
- Pass the same sort in the `sort` parameter.

Cost: you now maintain the filter logic in two places (the view and your code). If the view drifts, your code diverges. Fine for one-off runs; add a comment linking to the view for recurring code.

### 2. No `filterByFormula` on computed fields

MCP's filter DSL evaluates against **stored** values. Airtable computes formulas, rollups, and lookups server-side at query time — `filterByFormula` runs against those computed outputs. MCP's filter can't.

Examples of where this matters:
- Filtering by a `{Health Score}` formula field: `{Health Score} > 0.7`.
- Filtering by a rollup: `{Total Hours Logged} > 40`.
- Filtering by a lookup: `{Client Region (from Project)} = "US-West"`.
- Arbitrary formula expressions: `DATETIME_DIFF({Due}, TODAY(), 'days') < 7`, `REGEX_MATCH({Slug}, "^[a-z-]+$")`, `SEARCH("keyword", LOWER({Notes}))`.

**Workaround:** fetch broader, filter in code.

- Use the tightest MCP filter you can build on **stored** fields (Status, Priority, linked-record IDs, Archived flag, Origin Detail, raw dates).
- Return only the field IDs you need (`fieldIds`) so payload stays small.
- Apply the computed-field predicate in Python/JavaScript on the returned records.

This is slower than server-side `filterByFormula` for very large tables, but the XRAY tables here are small enough (thousands of rows, not millions) that the difference is invisible.

For arbitrary date math (`DATETIME_DIFF`, `WORKDAY`), MCP's `isWithin` with `pastNumberOfDays` / `nextNumberOfDays` / `daysAgo` covers the common cases. Reach for post-fetch filtering only when the date logic is genuinely custom.

## Reference scripts — deleted

The scripts `setup-gol.py`, `push-remaining-tasks.py`, and `dedup-tasks.py` have been deleted from `references/`. They loaded `~/.config/xray/airtable-tasks-pat` (also deleted) and are gone from the filesystem. Do not attempt to restore them from git — restore them and you're re-introducing the PAT dependency this skill removed.

Only `field-schemas.md` and `diagnostic-playbook.md` remain under `references/`.

Equivalents in the current routing:
- **Bulk create tasks** → loop `POST https://tasks.xray.tech/api/tasks` with 0.4s spacing. See the `create-task` skill for the exact call pattern.
- **Bulk create Projects / Objectives** → `mcp__airtable__create_records_for_table` with a `records` array of up to 50.
- **Bulk update / re-link Tasks' Outcomes** → `mcp__airtable__update_records_for_table` on `tblvlJq7I2GvIQEyP`, up to 50 per batch.
- **Dedup** → `GET /api/tasks/mine`, then filter client-side on `projectName` (the `?project=<id>` query param does not actually filter — verified against the app). Match against the canonical Markdown build doc. For each duplicate: split write per the "Credentials and remove semantics" section — `PATCH tasks.xray.tech/api/tasks/:id` with `Triage Status: Rejected`, then MCP `update_records_for_table` with `Archived: true`. The tasks.xray.tech PATCH does not accept `Archived`.

## Idempotency

- Always check for existing records by name before creating.
- Use `Origin Detail` as a batch tag (e.g., `Claude Code — [Client] build batch [date]`) so a re-run can detect prior writes.
- After any re-run, dedup by fetching (MCP `list_records_for_table` with `filters` on Origin Detail `contains` the batch tag) and reconciling against the canonical doc.

## Sequencing and rate

- MCP batch creates/updates: up to 50 records per call. One call typically covers all Projects and one call covers all Objectives for a client build. No sleep needed between MCP calls at this volume.
- tasks.xray.tech `POST /api/tasks`: one task per call. Sleep 0.4s between calls.
- On a 502, back off to 2s and retry once. If still failing, dump the offending payload and stop the batch.

## What NOT to do

- Don't write to the synced client base for Projects, Outcomes, or Tasks. All return 403.
- Don't write to a client base that isn't this engagement's. Verify base name matches client.
- Don't set Owner to anyone other than Rachael unless she explicitly says so.
- Don't run the bulk-create script in the background AND foreground in parallel; you'll create duplicates.
- Don't try to reconstruct or restore `~/.config/xray/airtable-tasks-pat`. The file has been deleted and the routing removed on purpose.

## Recovery: I created tasks under the wrong project or outcome

Re-parent via `PATCH /api/tasks/:id` on tasks.xray.tech:

```bash
API_KEY=$(cat ~/.config/xray/tasks-api-key)
curl -s -X PATCH "https://tasks.xray.tech/api/tasks/recXXXXXXXXXXXXXX" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $API_KEY" \
  -d '{"project": "recNEWPROJID"}'
```

If the `Outcomes` link needs to change too (the tasks.xray.tech PATCH does not currently expose Outcomes), use MCP:

```
mcp__airtable__update_records_for_table
  baseId: appQAdxI2hDNJj1g5
  tableId: tblvlJq7I2GvIQEyP
  records: [{id: "recXXX", fields: {Outcomes: ["recNEWOUTCOMEID"]}}]
```

The cascade lookups (`Project name (from Project)`, `Projects (from Outcomes)`, etc.) re-resolve automatically. No need to update the task's other fields.

## When this skill is the wrong answer

- Single ad-hoc task creation with no project/outcome context → `create-task`.
- Building the markdown build doc itself → `prd-to-plan` or `prd-to-issues`.
- Updating priority/status on a small number of tasks → `tasks.xray.tech/api PATCH` is faster.

## Verification checklist

- [ ] Source base counts: projects, objectives, tasks for this client match build doc
- [ ] Wait 30-60 seconds for sync
- [ ] Per-client planning base: Outcomes table populated, Tasks at XRay shows tasks with right Outcome links
- [ ] `/tasks/mine` at tasks.xray.tech returns the new tasks (priority must be read-format)
