---
name: audit-airtable-automations
version: 1.0.1
description: >
  Build an inventory of every automation that touches a given Airtable base — Airtable-native
  automations AND external automations (Zapier, Apps Script, Make, n8n, webhooks, custom
  scripts) — and produce an Omni prompt that creates an `Automation Inventory` table in
  the base, populated with one record per automation. Works on any Airtable base. Use
  whenever the user asks to inventory, index, document, audit, list, map, or catalog the
  automations in a base, even if they don't say "audit" — phrases like "what triggers X",
  "what fires when Y happens", "automations review", or "map the automation cascade" all
  belong here. Requires the Airtable MCP and Chrome DevTools MCP (with Airtable open and
  authenticated in the browser).
compatibility:
  tools:
    - mcp__airtable-pat__list_tables
    - mcp__airtable-pat__describe_table
    - mcp__chrome-devtools__list_pages
    - mcp__chrome-devtools__navigate_page
    - mcp__chrome-devtools__list_network_requests
    - mcp__chrome-devtools__get_network_request
    - mcp__chrome-devtools__evaluate_script
tags:
  - skill
---

# Airtable Automation Inventory

## Purpose in plain English

This skill helps you find the automations connected to an Airtable workspace and document what each one does.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


This skill produces an **Omni prompt** at `airtable_audit/omni_prompt.md` that, when
pasted into Airtable Omni inside the target base, creates an `Automation Inventory`
table and populates it with one record per automation. It covers Airtable-native
automations (discovered by scanning Airtable's internal API) AND external automations
(supplied via an inventory file the user provides).

The skill itself never writes to Airtable. It scans, reads the inventory file if one is
provided, and emits the Omni prompt sequence. The user pastes the prompts into Omni;
Omni creates the table and records.

The skill is generic — works on any Airtable base, no fixed folder paths or hard-coded
base IDs.

## Schema

Two linked tables:
- **`Automation Inventory`** — one row per automation (24 fields covering trigger, outputs, status, ownership, and runtime rollups)
- **`Automation Logs`** — one row per run, linked back to its Inventory entry (8 fields)

Full field definitions live in `references/canonical_schema.md`. The skill uses this as
the default when the base has no inventory yet. If the base already has an
`Automation Inventory` table, the skill detects it (Phase 1b) and matches the existing
schema's field names instead — see Phase 1b for how detection works.

The Omni prompts in Phase 5 embed the canonical schema inline so they're paste-ready
without needing the reference file open.

---

## Phase 1 — Get the base ID, detect an existing inventory, resolve IDs

### 1a. Confirm the target base

If the user hasn't named the base, ask. Confirm the `appXXX` ID before proceeding —
the rest of the skill is base-scoped.

### 1b. Detect an existing Automation Inventory (and Logs) table

Before generating Omni prompts that create tables, check whether the base already has
inventory and logs tables. Look for any table whose name contains "automation" +
"inventory" (case-insensitive); same for "automation" + "logs".

If `Automation Inventory` exists:
- `describe_table` at `full` detail to capture its schema (field names, types,
  single-select choices, linked-record relationships)
- Save to `airtable_audit/existing_inventory_schema.json`
- In Phase 5, **skip Prompt 1** (table creation) and use the existing schema's field
  names when populating records
- If a canonical field is missing from the existing schema (e.g., no `Owner`), fold the
  data into the nearest existing field rather than proposing schema changes — only
  propose adding a field when there's no reasonable home at all

If `Automation Logs` exists:
- Save its schema to `airtable_audit/existing_logs_schema.json` too
- Phase 5 won't try to create it

If neither exists:
- Phase 5 Prompt 1 creates both tables using the canonical schema (see
  `references/canonical_schema.md`)

Adoption-by-default is deliberate: every base evolves its own variant of an inventory
schema, and forcing them to converge to a new schema is more disruptive than matching
what's there.

### 1c. Get table ID → name map

```
mcp__airtable-pat__list_tables(baseId: "<appId>", detailLevel: "tableIdentifiersOnly")
```

Save as `{ tableId: tableName }`. Field and view ID resolution happen in Phase 3 (after
the scan), because the scan output determines which tables actually need resolution.

---

## Phase 2 — Fetch all Airtable-native automation data

Airtable's automation data lives in an internal v0.3 API that requires an authenticated
browser session. Use Chrome DevTools MCP to run the fetch from within the browser.

### 2a. Get a fresh secretSocketId

The API requires a `secretSocketId` query parameter that is session-scoped and **expires
quickly** (within minutes of inactivity, and any page reload generates a new one that
invalidates the old).

**Step 1 — load the page:**
```
mcp__chrome-devtools__navigate_page(type: "url", url: "https://airtable.com/<appId>")
```

If you have an automation ID, navigate directly to it: `https://airtable.com/<appId>/<wflId>`.

**Step 2 — capture the socket ID from recent traffic:**
```
mcp__chrome-devtools__list_network_requests(resourceTypes: ["fetch", "xhr"], pageSize: 30)
```

Look for a request like `/v0.3/application/<appId>/...?secretSocketId=socXXXXX`. Any
recent successful v0.3 request will have the current socket ID in its URL.

If a fetch returns "Failed to fetch" or 401-ish behavior mid-run, the socket has
rotated — reload the page and re-capture.

### 2b. Fetch all workflow details

Run `scripts/fetch_automations.js` via `evaluate_script`, substituting `APP_ID` and
`SECRET_SOCKET_ID`. The script fetches the workflow list and reads each workflow in
parallel.

Each automation object returned contains:

| Field | Notes |
|---|---|
| `id`, `name`, `url` | `url` is `https://airtable.com/<appId>/<wfId>` — use as Script Location |
| `enabled`, `deploymentStatus` | `enabled = (deploymentStatus === 'deployed')`. There is no `isEnabled` field — using it returns `undefined` and silently labels everything OFF |
| `description` | Author-supplied description shown in the Airtable UI |
| `triggerTypeId` | See trigger type reference (2c) |
| `trigInputs` | `{ tableId, viewId, fieldId, cronType }` — convenience shortcuts |
| `triggerConditions.watchFields` | Field IDs for `wttRECORDUPDATED0` — which fields, when changed, fire the trigger |
| `triggerConditions.filterFieldIds` | Field IDs referenced anywhere in the filter tree |
| `triggerConditions.filtersObj` | Raw filter tree for `wttRECORDMATCHES0` triggers |
| `actions[]` | Per-action type, target table, `fieldsWritten` (real `fldXXX` IDs), email recipients/subject, script length, etc. |

Save the raw JSON to `airtable_audit/raw_automations.json` before proceeding.

### 2c. Trigger type reference

| ID | Meaning | Where the condition lives |
|----|---------|---------------------------|
| `wttCRON0000000000` | Schedule (CRON) | `trigInputs.cronType` |
| `wttRECORDCREATED0` | Record created | Just `tableId` |
| `wttRECORDMATCHES0` | Record matches conditions | `triggerConditions.filtersObj` |
| `wttRECORDUPDATED0` | Record updated | `triggerConditions.watchFields` |
| `wttBRZzRXx3C2jyIc` | Record enters view | `trigInputs.viewId` (fetch filter in 2e) |
| `wttCONNECTIONINPT` | External / button trigger | Manual; no condition |

For `wttRECORDUPDATED0`, render the specific watched fields in Trigger Detail. Only
render "any field" when `watchFields` is genuinely empty.

### 2d. Action type reference

| ID | Meaning |
|----|---------|
| `watOUTLOKSENDMAIL` | Send Outlook email |
| `watSENDEMAIL00000` | Send email (native Airtable) |
| `watFINDRECORDS000` | Find records |
| `watCUSTOMSCRIPT00` | Run script |
| `watUPDATERECORD00` | Update record |
| `watCREATERECORD00` | Create record |
| `watBETUHIcuho4hit` | Conditional logic (may contain nested actions, including email) |
| `watAIGENERATESTR0` | AI generate text |
| `watGSHEETSCREATE0` | Create Google Sheet |

When walking actions, recurse into `watBETUHIcuho4hit` branches — nested email and write
actions belong in Outputs.

---

## Phase 3 — Resolve field and view IDs for the scanned automations

After the scan, every automation in `raw_automations.json` references table IDs, field
IDs (in `watchFields`, `filterFieldIds`, action `fieldsWritten`), and view IDs (for
view-based triggers). Resolve those to human-readable names so the Inventory records
don't read as walls of `fldXXX` codes.

### 3a. Field ID → name maps

Enumerate every unique `tableId` referenced anywhere in the scan output (trigger inputs,
watched fields, filter operands, action fieldsWritten). For each, fetch a field map:

```
mcp__airtable-pat__describe_table(baseId: "<appId>", tableId: "<id>", detailLevel: "identifiersOnly")
```

Use `identifiersOnly` — large tables blow past token limits at `full` detail.

### 3b. View ID → name maps

The same `describe_table` calls return a `views` array. Build a nested map
`{ tableId: { viewId: viewName } }`.

### 3c. View filter formulas (for view-based triggers only)

For each automation with `triggerTypeId === 'wttBRZzRXx3C2jyIc'`, the `viewId` tells you
*which* view but not *which records enter it*. Capture the view's filter formula so the
Inventory record's Trigger Condition can show it.

Two options:

1. `describe_table` at `full` detail — returns view filter info inline. Watch token limits.
2. v0.3 read endpoint with `includeDataForViewIds` scoped in (uses Chrome session like Phase 2).

Save to `airtable_audit/view_filters.json` keyed by viewId. If capture fails, render
`(filter not captured)` in the record's Trigger Condition.

---

## Phase 4 — Read the external automations inventory file

Non-Airtable automations (Zapier, Apps Script, Make, n8n, webhooks, custom scripts)
won't show up in the v0.3 scan. They have to be supplied.

Ask the user: "Is there an inventory file listing external automations that touch this
base?" Accept any of:

- A path to a YAML or markdown file
- Pasted YAML/markdown content
- "No" — proceed with Airtable-native only

If a file or content is provided, parse it. The expected YAML structure and two
worked examples live in `references/external_inventory_template.md` — read that file
for the exact field names (they match the canonical schema). Each entry under
`external_automations:` maps 1:1 to one Inventory record. Save parsed entries to
`airtable_audit/external_inventory.json`.

If the user says "no," proceed with Airtable-native only and note that in the run
summary so the user knows the Inventory will be incomplete until they document external
automations.

---

## Phase 5 — Generate the Omni prompt sequence

Build `airtable_audit/omni_prompt.md` as a numbered sequence of self-contained Omni
prompts. Each prompt is pasteable independently — Omni loses context between messages,
so each prompt must restate the table name and any other context it needs.

Keep individual prompts under ~250 words where possible. Bulk-record prompts will run
longer because they list record data; that's fine.

**Schema branching:** If Phase 1b found existing tables, skip the table-creation
prompts (5a, 5b below) and use the existing schemas' field names when populating
records. Map automation data into the closest equivalent existing fields.

### Prompt 5a — Create Automation Logs table (skip if it exists)

```
Create a new table in this base called "Automation Logs" if it doesn't already exist.
The table should have these fields:

- Log ID (single line text) — primary field
- Automation (will link to Automation Inventory — create after Inventory exists)
- Logged At (date with time)
- Outcome (single select) with choices: Success, Failed, Skipped, Partial
- Notes (long text)
- Affected Record IDs (long text)
- Duration ms (number, integer)
- Error (long text)

Do not delete or rename existing fields if the table already exists.
```

### Prompt 5b — Create Automation Inventory table (skip if it exists)

```
Create a new table in this base called "Automation Inventory" if it doesn't already
exist. The table tracks one row per automation in the base. Add these fields:

- Automation Name (single line text) — primary field
- Trigger Type (single select) with choices: Record matches conditions, Record updated, Record created, Scheduled, View entry, Form submission, Webhook, External
- What It Does (long text)
- Source Table (single line text)
- Group (single select) with choices: A - Has script action, B - No script action, Sweep, External, Webhook
- Fields Written (long text)
- Status (single select) with choices: Live, Built not deployed, Disabled, Off
- Source File (single line text) — path to script file, or "(Airtable UI only)" / "(Zapier zap)" / "(Apps Script)"
- Deployed (checkbox)
- Logger Added (checkbox) — whether this automation writes to Automation Logs on each run
- Automation Logs (link to Automation Logs table, allow multiple)
- Last Run (single line text) — placeholder; description: "Convert to ROLLUP of Automation Logs > Logged At with MAX aggregation"
- Total Runs (single line text) — placeholder; description: "Convert to COUNT of linked Automation Logs (no filter)"
- Last Outcome (single line text) — logger-stamped; do not convert to rollup
- Failed Runs (single line text) — placeholder; description: "Convert to COUNT of Automation Logs where Outcome = Failed"
- Skipped Runs (single line text) — placeholder; description: "Convert to COUNT of Automation Logs where Outcome = Skipped"
- Last Note (single line text) — logger-stamped; do not convert to rollup
- Trigger Condition (long text)
- Owner (single line text)
- Last Updated (date, US format M/D/YYYY)
- Dependencies (long text)
- Pain Points Addressed (single line text)
- Deliverable (single line text)
- Notes (rich text)
```

### Prompt 5c — Convert rollup placeholders (optional but recommended)

```
In the "Automation Inventory" table, convert these placeholder text fields to their
intended rollup or count types, based on the description on each field:

- Last Run → Rollup of linked Automation Logs records, rolling up the "Logged At" field with MAX aggregation
- Total Runs → Count of linked Automation Logs records (no filter)
- Failed Runs → Count of linked Automation Logs records filtered to Outcome = "Failed"
- Skipped Runs → Count of linked Automation Logs records filtered to Outcome = "Skipped"

Leave Last Outcome and Last Note as single-line text — they are logger-stamped, not
rolled up.
```

### Prompts 2..N — Add records in batches

Group records into batches of ~5 per prompt. For each batch:

```
Add these records to the "Automation Inventory" table. For each record, if a record
already exists where Automation Name matches exactly, update it instead of adding a
duplicate.

Record 1:
- Automation Name: "<name>"
- Trigger Type: <one of the single select choices>
- What It Does: <plain-language one or two sentences>
- Source Table: <table name>
- Group: <A - Has script action | B - No script action | Sweep | External | Webhook>
- Fields Written: <enumerated field writes across all actions>
- Status: <Live | Built not deployed | Disabled | Off>
- Source File: <Airtable workflow URL, or "(Airtable UI only)" / "(Zapier zap)" / etc.>
- Deployed: <checked | unchecked>
- Logger Added: <checked | unchecked — usually unchecked at audit time>
- Trigger Condition: <watched fields list, or filter formula, or cron schedule>
- Owner: <if known, else blank>
- Last Updated: <YYYY-MM-DD or blank if unknown>
- Dependencies: <upstream/downstream automations or systems>
- Pain Points Addressed: <if known, else blank>
- Deliverable: <if known, else blank>
- Notes: 

Record 2: ...
```

For Airtable-native automations, source data from `raw_automations.json` + the ID maps:
- `Trigger Condition` always names watched fields explicitly (never just "any update"
  unless watchFields is genuinely empty)
- `Fields Written` enumerates every field write across all actions
- `Group` is `A - Has script action` if any action is `watCUSTOMSCRIPT00`, otherwise
  `B - No script action` (use `External` / `Webhook` for those trigger types, `Sweep`
  for CRON-triggered cleanup automations)
- `Source File` is the automation's `url` for Airtable-native, or path/URL for external
- `Deployed` is the `enabled` boolean from the v0.3 fetch
- `Status` = `Live` if `enabled`, else `Off`. Use `Built not deployed` / `Disabled` only
  if you can distinguish from the v0.3 data

For external automations, source data from `external_inventory.json` — pass through as
provided. External entries have `Group` = `External` or `Webhook` depending on system.

### Prompt N+1 — Ask Omni to fill in scan gaps

The v0.3 scan misses two things the skill cannot extract from JS alone:

1. **Conditional-logic branch contents** (`watBETUHIcuho4hit` then/else actions and the
   emails / field writes nested inside them)
2. **Reconstructed filter formulas** for `wttRECORDMATCHES0` triggers — the raw
   `filtersObj` is captured but rendering it as a human-readable AND/OR expression is
   error-prone in JS

Rather than fix these in the scanner, push them to Omni. Emit a final prompt that lists
every automation whose Fields Written or Trigger Condition came back incomplete, and ask
Omni to open each one in Airtable and fill in the record.

```
For each of the following automations, open the source file URL in a new tab inside
Airtable, inspect the trigger filter and any Conditional-logic action branches, and
update the matching record in "Automation Inventory":

- "<automation name>" — Source File: <URL>
  Fill in Trigger Condition with the human-readable filter formula.
  Fill in Fields Written with every field write across all action branches.
  Fill in any nested email recipients in Notes if present.

- "<next automation>" — Source File: <URL>
  ...
```

Only include automations where the scanner returned an empty or "(not captured)" value
in a critical field. Skip automations the scanner fully populated.

---

## Idempotency

The Phase 5 prompts are safe on re-run:

- Table creation is conditional ("if it doesn't already exist")
- Record adds dedupe by Name match ("if a record already exists where Name matches
  exactly, update it instead")

On a re-audit, paste the new prompt sequence and Omni updates in place.

---

## Handling large responses

If `evaluate_script` returns truncated output (>100k chars), split the workflow list
into batches of 20 and run separate calls, then merge before saving.

If `describe_table` for a large table exceeds token limits at `full`, use
`identifiersOnly` and capture view filters via the v0.3 read endpoint (Phase 3c option 2).

---

## Output files

| File | Contents |
|------|---------|
| `airtable_audit/raw_automations.json` | Raw JSON from the Airtable v0.3 fetch |
| `airtable_audit/view_filters.json` | View filter formulas keyed by viewId (Phase 3c) |
| `airtable_audit/external_inventory.json` | Parsed external automations the user supplied |
| `airtable_audit/omni_prompt.md` | The pastable Omni prompt sequence — primary deliverable |

Create the `airtable_audit/` directory if it doesn't exist.

---

## References

- `scripts/fetch_automations.js` — fetches workflow list + per-workflow detail via v0.3 API
- `references/external_inventory_template.md` — empty inventory scaffold for external automations
