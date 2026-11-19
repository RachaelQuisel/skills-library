# Diagnostic playbook

Step-by-step rerun of the dance to follow when Rachael says "the outcomes table is empty in my planning base" or any variant. Each step records what was tried, what response came back, and what to do about it.

Routing is fixed: tasks.xray.tech API for what it covers, Airtable MCP for everything else. See the parent SKILL.md's "Routing rule" for the full rationale. The old PAT-based path has been removed on purpose; don't try to restore it.

## Step 0: Recognize the symptom

The symptom is always one of:

- "I'm looking at my planning base and the Outcomes table is empty"
- "I see no outcomes / projects / tasks in `[client base URL]`"
- "Just create the records"

The user thinks her planning base is the system of record. It is not. It is a synced replica of `appQAdxI2hDNJj1g5`.

## Step 1: Identify which base she's looking at vs. which base writes go to

Rachael will send a URL like `https://airtable.com/appQ2DVUVGLq7mFg9/...`. That `appXXX` segment is the per-client planning base. Tables prefixed with `⚡️` in that base are externally synced and read-only.

The actual write target is `appQAdxI2hDNJj1g5` ("Projects & Tasks at XRAY"). Always.

## Step 2: Confirm the routes are attached

- **tasks.xray.tech API**: `~/.config/xray/tasks-api-key` exists and readable.
- **Airtable MCP**: `mcp__airtable__*` tools are attached in the session.

If either is missing, stop and surface — don't fall back to the deleted PAT.

## Step 3: Read the source schema and cache the field options

```
mcp__airtable__get_table_schema
  baseId: appQAdxI2hDNJj1g5
  tables: [
    {tableId: "tblOaFlYpPXlHrT2c"},  # Projects
    {tableId: "tblyZxi1nYrGICXrf"},  # Objectives
    {tableId: "tblvlJq7I2GvIQEyP"}   # Tasks
  ]
```

Save the response. The single-select option strings are strict; the Tasks Priority options especially (see `field-schemas.md`).

## Step 4: Find or create the client record

Fastest path — hit the read-only Clients endpoint:

```
GET https://tasks.xray.tech/api/clients
  header: X-Api-Key: <key>
```

Filter the response client-side by exact name. If not present:

```
mcp__airtable__create_records_for_table
  baseId: appQAdxI2hDNJj1g5
  tableId: tblVS1aUCNeqtVq5U
  records: [{fields: {Name: "[Client]", Status: "Active", Phase: "Discovery"}}]
```

Capture the returned `recXXX` ID.

## Step 5: Check for existing projects in the source (don't duplicate)

```
GET https://tasks.xray.tech/api/projects?q=<client name>
  header: X-Api-Key: <key>
```

Returns up to 10 matches. Apply the SKILL.md workflow step 3 decision rule: exact match → PATCH; new workstream → create alongside; ambiguous → ask Rachael before writing.

## Step 6: Create the projects

```
mcp__airtable__create_records_for_table
  baseId: appQAdxI2hDNJj1g5
  tableId: tblOaFlYpPXlHrT2c
  records: [ ... up to 50 project records ... ]
```

Use `Project Type: "Consulting Solution Sprints"`. Include `Origin Detail: "Claude Code — [Client] build batch [YYYY-MM-DD]"` for later idempotency.

## Step 7: Create the objectives

```
mcp__airtable__create_records_for_table
  baseId: appQAdxI2hDNJj1g5
  tableId: tblyZxi1nYrGICXrf
  records: [ ... up to 50 objective records, each linked to its project + client ... ]
```

Set `Owner: {"id": "usr5vnH7D87XIP57C"}`. Same `Origin Detail` batch tag.

## Step 8: Link existing tasks (if any are already in the source)

If `tasks.xray.tech` already has tasks for this client (Origin Detail has a known batch tag, or `GET /api/tasks/mine` filtered client-side on `projectName` returns them), split the re-parent:

```
# 1. Project + priority via tasks.xray.tech
PATCH https://tasks.xray.tech/api/tasks/<task_id>
  header: X-Api-Key: <key>
  body: {"project": "<project_id>", "priority": "High"}

# 2. Outcomes link via MCP (tasks.xray.tech PATCH does not accept Outcomes)
mcp__airtable__update_records_for_table
  baseId: appQAdxI2hDNJj1g5
  tableId: tblvlJq7I2GvIQEyP
  records: [{id: "<task_id>", fields: {Outcomes: ["<objective_id>"]}}]
```

## Step 9: Create remaining tasks from the build doc

Parse the `| # | Task | Who | Priority | How long | Notes |` table format. Skip rows whose titles already match an already-linked task. For each remaining row:

```
POST https://tasks.xray.tech/api/tasks
  header: X-Api-Key: <key>
  body: {"title": "...", "priority": "High", "project": "<project_id>", ... }
```

Sleep 0.4s between calls. tasks.xray.tech has no batch endpoint.

If the task needs an `Outcomes` link, follow up with the MCP update from Step 8.

## Step 10: Verify sync

Wait 30-60 seconds. Then read the per-client planning base via MCP:

```
mcp__airtable__list_records_for_table
  baseId: <per-client base ID, e.g., appQ2DVUVGLq7mFg9 for GoL>
  tableId: <Outcomes table ID in that base>
  filters: {operator: "contains", operands: ["Origin Detail", "<batch tag>"]}
```

Confirm new records appear. Sync usually completes in under a minute but can take longer under load.

---

## What I tried that failed (so the next session doesn't waste time)

| Attempt | Error | Root cause |
|---|---|---|
| `POST` to a `⚡️`-prefixed table in the client base | `403 externally synced` | The `⚡️` prefix means synced, read-only. Write to source `appQAdxI2hDNJj1g5`. |
| `POST` to `Outcomes` in the client base | `403 externally synced` | Same: synced from source. The lack of `⚡️` prefix on Outcomes is misleading; it's still synced. |
| `POST tasks.xray.tech/api/projects` | `404 Cannot POST` | tasks.xray.tech wraps Tasks (full lifecycle), Projects (search only), Outcomes (read only). Use Airtable MCP to create Projects and Objectives. |
| `POST tasks.xray.tech/api/outcomes` | `404 Cannot POST` | Same as above — reads only. Verified 2026-07-01. |
| `POST tasks.xray.tech/api/tasks` with `priority: "High"` | 201 success but task absent from `/tasks/mine` | `"High"` isn't a valid select option on the underlying field. Stores as-is but breaks priority-based filters. Use tasks.xray.tech's write format (`"High"` write → `"P1: Top Priority"` read) per the `create-task` skill. |
| `PATCH` priority to `"P2: High"` (guessed read-format) | `502 Failed to update task in Airtable` | Not a real option. Valid read-format strings: `P0: Urgent & Critical`, `P1: Top Priority`, `P2: Medium Priority`, `P3: Low Priority`, `P4: Lowest Priority`. |
| Filtering `/tasks/mine` by `?project=<id>` | Returned unfiltered results | The `?project=` param does not actually filter. Fetch and filter client-side on `projectName`. |
| Trying to set Task `Status: "Cancelled"` | Silently stored as invalid string | `Cancelled` is a valid Project Status but NOT a valid Task Status. Task Status options: `Backlog`, `Blocked`, `Ready to Start`, `In Progress`, `Done`. Use `Triage Status: Rejected` + `Archived: true` to remove a task. |
| Running the same bulk-create twice | Doubled the record count silently | Neither route checks for prior writes. Use `Origin Detail` batch tags and dedup by fetching + comparing against the canonical build doc. |

---

## After-action: dedup against canonical

If a build doc is the canonical task list, dedup by:

1. Fetch source tasks: `mcp__airtable__list_records_for_table` on `tblvlJq7I2GvIQEyP` with `filters: {operator: "contains", operands: ["Origin Detail", "<batch tag>"]}`.
2. Group tasks by `(Outcomes[0] recId, normalized Task title)`.
3. For each group with multiple records, keep the most recently created (highest `Created` timestamp) and mark the rest for removal.
4. For source tasks not present in the canonical doc, mark them for removal.
5. Print a diff showing canonical rows missing from source (need to be created).

Removal is a split write per the SKILL.md "Credentials and remove semantics" section:

```
# 1. Triage Status via tasks.xray.tech
PATCH https://tasks.xray.tech/api/tasks/<task_id>
  header: X-Api-Key: <key>
  body: {"triageStatus": "Rejected"}

# 2. Archived via MCP
mcp__airtable__update_records_for_table
  baseId: appQAdxI2hDNJj1g5
  tableId: tblvlJq7I2GvIQEyP
  records: [{id: "<task_id>", fields: {Archived: true}}]
```

Default should always be dry-run first — print the intended writes, get Rachael's sign-off, then apply. This matches the `[review-before-apply]` memory: write → dryrun → /review → fix → --apply → post-run.
