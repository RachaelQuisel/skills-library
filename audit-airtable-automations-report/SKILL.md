---
name: audit-airtable-automations-report
version: 1.0.0
description: >
  Write a full markdown audit report of the Airtable-native automations in a base. Use this skill when the user
  wants a written document of trigger conditions, email recipients and the automation cascade map (for an
  Automation Inventory table built with an Omni prompt, use audit-airtable-automations instead). Fits requests
  to document, audit, review, or understand Airtable automations — including questions like
  "what automations send emails to partners?", "map the automation cascade", "document
  all automations before we do cleanup", or "what triggers partner emails?". The skill
  produces a full audit document covering trigger conditions (watched fields and filter
  formulas, not vague "any update" labels), field writes, email recipients (decoded
  from Airtable's expression-tree AST into readable strings), cascade chains between
  automations, and per-automation hyperlinks back to Airtable. Requires the Airtable MCP
  and Chrome DevTools MCP (with Airtable open and authenticated in the browser).
compatibility:
  tools:
    - mcp__airtable__list_tables
    - mcp__airtable__describe_table
    - mcp__chrome-devtools__list_pages
    - mcp__chrome-devtools__navigate_page
    - mcp__chrome-devtools__list_network_requests
    - mcp__chrome-devtools__get_network_request
    - mcp__chrome-devtools__evaluate_script
---

# Airtable Automations Audit

This skill audits all automations in an Airtable base by combining the public Airtable
MCP (for schema fallbacks) with Airtable's internal v0.3 API (for automation definitions
and view filters, accessed via the authenticated browser session).

Output: `airtable_audit/automations_audit.md` with header/status, summary table,
a dedicated email-sending section (recipients and subjects decoded from AST), a cascade
map showing which automations could fire which others, and per-automation breakdowns
linking back to Airtable. Bases with no email automations skip the email section.

The goal: anyone reading the audit can answer "*why* does this automation fire?" and
"*what else fires* when this one writes?" without opening Airtable. Vague labels like
"Record updated (any field)" or "enters tentative view" hide whether a trigger is
narrow (one watched field) or broad (any change) and have caused real cascade-risk
misreads in the past.

---

## Flow at a glance

```
1. Navigate to /automations  →  triggers readForWorkflows (full schema) + listWorkflows
2. Save responses            →  get_network_request(responseFilePath=...) for both
3. Build schema maps         →  parse readForWorkflows into table/field/view maps
                                (fallback: mcp__airtable__list_tables identifiersOnly)
4. Fetch workflow details     →  evaluate_script: Promise.all(workflow/{id}/read) with headers
5. View filters              →  evaluate_script: Promise.all(view/{id}/readData) with headers
6. NORMALIZE                 →  normalize_workflows.py — raw AST → parser-ready records
7. Parse & write             →  parse_and_write.py — emits the audit doc
```

**Do not skip step 6.** The `/v0.3` API returns deeply-nested expression trees;
`parse_and_write.py` expects flat records. `normalize_workflows.py` is the bridge — without
it the parser reads nothing useful.

The whole audit can normally be run in one pass once the browser is authenticated.
Allow ~2 minutes for a base with ~50 automations.

---

## Phase 1 — Session setup

Navigate to the **automations page**, not the base root. This single navigation fires
two key requests automatically:
- `readForWorkflows` — 1.5–2MB JSON with all tables, fields, views, and choices
- `listWorkflows` — all automation IDs and names

```
mcp__chrome-devtools__navigate_page(type: "url",
  url: "https://airtable.com/<appId>/automations")
mcp__chrome-devtools__list_network_requests(
  resourceTypes: ["fetch", "xhr"], pageSize: 40)
```

From the network list, identify the reqids for:
- `GET /v0.3/application/<appId>/readForWorkflows` → save as schema
- `GET /v0.3/application/<appId>/listWorkflows` → save as automation list
- Any `GET /v0.3/...?secretSocketId=socXXX` → note the socket value and the `pageLoadId`

**Capture the socket and headers from an existing successful request.** Inspect any
`/v0.3/` request with `get_network_request(reqid=...)` and note:
- `secretSocketId=socXXX` from the URL
- `x-airtable-page-load-id` from the request headers
- `x-airtable-inter-service-client-code-version` from the request headers

The socket is valid for the **entire automation page session** as long as the page
stays open. It does NOT expire in seconds — the 401s you may encounter are caused by
**missing required headers** (see Phase 3), not socket expiry.

**⚠️ Do NOT try to intercept fetch via `initScript`.** Airtable's bundled JS modules
capture a reference to the native `fetch` before any `initScript` wrapper runs. The
interceptor will never fire. Use `get_network_request` to save already-made responses,
and `evaluate_script` with explicit headers to make new ones.

---

## Phase 2 — Schema (tables, fields, views, choices)

**Primary: save `readForWorkflows` directly from the network panel.**

```
mcp__chrome-devtools__get_network_request(
  reqid: <readForWorkflows reqid>,
  responseFilePath: "airtable_audit/describes_workflows.json")
```

**⚠️ `responseFilePath` does not honour your filename.** Chrome DevTools MCP writes to
`<stem>.network-response` (e.g. `describes_workflows.network-response`), dropping the
`.json` extension. Rename after each save, or the later phases won't find their inputs:

```bash
cd airtable_audit && mv describes_workflows.network-response describes_workflows.json \
                  && mv raw_automations.network-response  raw_automations.json
```

This response contains `data.tableSchemas` — a list of all tables with full field
metadata (id, name, type, choices) and all views (id, name, type). Parse it to build:
- `table_map.json` = `{ tableId: tableName }`
- `field_map.json` = `{ tableId: { fieldId: fieldName } }`
- `view_map.json`  = `{ tableId: { viewId: viewName } }`
- `choices_map.json` = `{ fieldId: { selXXX: optionName } }` (for singleSelect/multiSelect) — **optional, build on demand** (see note below)

**`columns` vs `fields`:** In `readForWorkflows`, each table entry stores fields under
`t["columns"]`, not `t["fields"]`. The MCP `list_tables` response uses `t["fields"]`.
Always read with `t.get("columns") or t.get("fields", [])` so the parser handles both
sources without modification.

**`choices_map` is optional.** Only build it if any automation uses a
`wttRECORDMATCHES0` trigger (or a find-records action) that filters on a singleSelect or
multiSelect value. If no automations reference choice IDs, skip this map entirely.

**Fallback: MCP `list_tables` with `identifiersOnly`.** If `readForWorkflows` parsing
fails or is incomplete, `mcp__airtable__list_tables(baseId, detailLevel: "identifiersOnly")`
returns all tables, fields, and views via the public API with no browser dependency.
The result may be large (>65K chars) and get saved to a file by the harness — process
it with Python rather than reading it inline.

**Note:** `includeDataForTableIds: null` on the `/v0.3/application/{appId}/read`
endpoint returns 401 even with a valid socket and correct headers. Only specific table
ID arrays work on that endpoint. Use `readForWorkflows` or the MCP instead.

**Caveat — personal views:** The schema endpoints omit views with `personalForUserId`
set. After Phase 4 you'll have the `viewId`s used as triggers; for any that aren't in
your view_map, fall back to:
```
mcp__airtable__describe_table(baseId: "<appId>", tableId: "<tableId>",
  detailLevel: "identifiersOnly")
```
Merge the returned `views` arrays into `view_map.json`.

---

## Phase 3 — Automations

### Step 3a — Get the workflow list

Save the `listWorkflows` response directly:

```
mcp__chrome-devtools__get_network_request(
  reqid: <listWorkflows reqid>,
  responseFilePath: "airtable_audit/raw_automations.json")
```

**`listWorkflows` returns skeleton data only** — trigger type ID and action type IDs,
but no conditions, no field writes, no inputExpressions. It is only useful for
getting the list of workflow IDs and names.

### Step 3b — Fetch full workflow details in parallel

For each workflow ID from step 3a, call `GET /v0.3/workflow/{id}/read`. Do this in
a single `evaluate_script` call using `Promise.all` so all fetches fire simultaneously:

```js
async () => {
  const sock = '<secretSocketId>';
  const pageLoadId = '<x-airtable-page-load-id>';
  const codeVersion = '<x-airtable-inter-service-client-code-version>';
  const headers = {
    'x-airtable-inter-service-client': 'webClient',
    'x-airtable-inter-service-client-code-version': codeVersion,
    'x-airtable-page-load-id': pageLoadId,
    'x-airtable-application-id': '<appId>',
    'x-time-zone': 'America/New_York',
    'x-requested-with': 'XMLHttpRequest',
    'x-user-locale': 'en',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'x-airtable-client-queue-time': '0'
  };
  const ids = ['wflXXX', 'wflYYY', ...];
  const results = await Promise.all(ids.map(async (id, i) => {
    const url = `https://airtable.com/v0.3/workflow/${id}/read?stringifiedObjectParams=%7B%7D`
      + `&requestId=reqAudit${String(i).padStart(3,'0')}${id.slice(-4)}`
      + `&secretSocketId=${sock}`;
    const r = await fetch(url, { credentials: 'include', headers });
    if (!r.ok) return { id, httpError: r.status };
    return { id, data: await r.json() };
  }));
  window.__wfDetailResults = results;
  return JSON.stringify(results.map(r => ({ id: r.id, ok: !r.httpError })));
}
```

Then save with `filePath`:
```
evaluate_script(
  function: "() => JSON.stringify(window.__wfDetailResults)",
  filePath: "airtable_audit/workflow_details_raw.json")
```

**The required headers are not optional.** `evaluate_script` fetch calls without them
return 401 even with a valid socket. Read them from any existing successful `/v0.3/`
request via `get_network_request(reqid=...)`.

### Workflow data shape

Each `workflow/{id}/read` response has shape `{ msg, data: { workflow: { ... } } }`.
The workflow object contains:

| Field | Notes |
|---|---|
| `id`, `name`, `description` | Basic identity |
| `deploymentStatus` | `'deployed'` = enabled, anything else = disabled. There is no `isEnabled` field. |
| `trigger.workflowTriggerTypeId` | See trigger type reference below |
| `trigger.inputExpressions` | All trigger config — tableId, viewId, filtersObj, cron schedule. Keys vary by trigger type. |
| `graph.entryWorkflowActionId` | First action node ID — follow `nextWorkflowActionId` chain to get execution order |
| `graph.actionsById` | Map of all action and decision nodes. Decision nodes use `workflowDecisionTypeId` instead of `workflowActionTypeId`. |
| `graph.actionsById[id].inputExpressions` | All action config — target tableId, fields to write, find-records filter, script body, email recipients, etc. — all as AST nodes |

**Automation URL format:** `https://airtable.com/{appId}/{workflowId}` — there is no
`/automations/` segment in the path.

### Trigger type reference

| ID | Meaning | Where the condition lives |
|----|---------|---------------------------|
| `wttCRON0000000000` | Schedule (CRON) | `trigger.inputExpressions.type` (e.g. `"weeklyV2"`), `.config` (weekdays + triggerTimes), `.start` |
| `wttRECORDCREATED0` | Record created | `trigger.inputExpressions.tableId` — fires on every new record |
| `wttRECORDMATCHES0` | Record matches conditions | `trigger.inputExpressions.filtersObj` (operator/operands AST — see Filter AST section) |
| `wttRECORDUPDATED0` | Record updated | `trigger.inputExpressions.watchedFieldIds` (specific fields, not "any") |
| `wttBRZzRXx3C2jyIc` | Record enters view | `trigger.inputExpressions.viewId` — fetch view filter in Phase 4 |
| `wttCONNECTIONINPT` | External / button trigger | Manual; no condition |

The distinction between `wttRECORDUPDATED0` with `watchedFieldIds = []` (any update) vs a
specific list is the most common source of cascade-risk misreads. Render both explicitly.

### Decision type reference

Decision nodes live in `actionsById` alongside action nodes, identified by
`workflowDecisionTypeId` (not `workflowActionTypeId`).

| ID | Meaning | Decision-specific data |
|----|---------|------------------------|
| `wdtFANOUT00000000` | forEach loop | `inputExpressions.fanOutArray`: source node whose records to iterate |
| `wdtREDUCER0000000` | End of forEach | none — paired with the fan-out above |
| `wdtNWAY0000000000` | N-way conditional (if/else) | `inputExpressions.groups`: array of branch condition objects |

### Action type reference

| ID | Meaning |
|----|---------|
| `watSENDTOSLACK000` | Send Slack message |
| `watSLACKSNDACTMSG` | Send Slack action message (with record context link) |
| `watOUTLOKSENDMAIL` | Send Outlook email |
| `watSENDEMAIL00000` | Send email (native Airtable) |
| `watBETUHIcuho4hit` | Send email (conditional branch) — same shape as `watOUTLOKSENDMAIL`; counts as email for cascade analysis |
| `watFINDRECORDS000` | Find records |
| `watCUSTOMSCRIPT00` | Run script — body at `inputExpressions.script` (type `literal`), inputs at `inputExpressions.inputObj` |
| `watUPDATERECORD00` | Update record |
| `watCREATERECORD00` | Create record |
| `watAIGENERATE0000` | AI generate text (free-form output) |
| `watAIGENERATESTR0` | AI generate (structured output with schema) |
| `watGSHEETSCREATE0` | Create Google Sheet |
| `watSENDTOMSTEAMS0` | Send Microsoft Teams message |
| `watAIGENERATESTR0` | AI generate (structured output) — `prompt`/`model`/`outputSchema` hold the real logic; always render the prompt |

---

## Phase 4 — View filters

For each automation with `trigger.workflowTriggerTypeId === 'wttBRZzRXx3C2jyIc'`, the
`viewId` tells you which view but not which records enter it. Fetch the view's filter
with a parallel `evaluate_script` call (same headers pattern as Phase 3):

```js
const url = `https://airtable.com/v0.3/view/${viewId}/readData`
  + `?stringifiedObjectParams=%7B%7D&requestId=reqVF${viewId.slice(-4)}`
  + `&secretSocketId=${sock}`;
const r = await fetch(url, { credentials: 'include', headers });
```

The response `data` object contains a `filters` key with the view's filter expression.
Save all view filter responses to `airtable_audit/view_filters_raw.json`.

**View filter shape:** `{ filterSet: [...], conjunction: "and" }` at the outer level.
Each entry in `filterSet` is either a leaf `{ columnId, operator, value }` or a nested
group `{ type: "nested", conjunction, filterSet: [...] }`.

If a view filter capture fails (e.g. socket expired mid-run), fall back to
`_(not captured — see view in Airtable)_` rather than erroring.

---

## Phase 5 — Filter AST decoding

Airtable uses two different AST shapes depending on context. Both appear in audits.

### Shape A — `operator` / `operands` (automation trigger filters, action find-records)

Used in `trigger.inputExpressions.filtersObj` and action `inputExpressions.filtersObj`.

```json
{
  "type": "object",
  "properties": [
    { "key": { "type": "literal", "value": "operator" },
      "value": { "type": "literal", "value": "and" } },
    { "key": { "type": "literal", "value": "operands" },
      "value": { "type": "tuple", "elements": [
        {
          "type": "object",
          "properties": [
            { "key": ..., "value": { "type": "literal", "value": "=" } },
            { "key": ..., "value": { "type": "tuple", "elements": [
              { "type": "literal", "value": "fldXXXXXXXXXXXXXX" },
              { "type": "literal", "value": true }
            ]}}
          ]
        }
      ]}}
  ]
}
```

Decode recursively:
- If `operator` is `and`/`or` → compound; recurse into each `operands` element
- If `operator` is a comparison (`=`, `!=`, `contains`, `isEmpty`, etc.) → leaf
  - `operands[0]` = field ID literal
  - `operands[1]` = comparison value (may be absent for `isEmpty`/`isNotEmpty`)

### Shape B — `filterSet` / `conjunction` (view filters)

Used in view filter responses and some older automation configs.

```json
{
  "filterSet": [
    { "columnId": "fldXXX", "operator": "isNotEmpty", "value": null },
    { "type": "nested", "conjunction": "and", "filterSet": [...] }
  ],
  "conjunction": "and"
}
```

Decode by walking `filterSet`, handling `type: "nested"` groups recursively.
Unary operators (`isEmpty`, `isNotEmpty`, `isChecked`, etc.) have `value: null` — omit the value when rendering.
Date-relative values have `{ mode: "daysAgo", numberOfDays: N }` — render as `daysAgo(N)`.

---

## Phase 6 — Normalize the raw workflow AST

`workflow/{id}/read` returns Airtable's internal expression trees. `parse_and_write.py`
expects flat records. Bridge them:

```bash
python scripts/normalize_workflows.py --dir airtable_audit --base-id <appId>
```

Reads `workflow_details_raw.json`, `view_filters_raw.json`, `field_map.json`,
`choices_map.json`; writes `automations_normalized.json` and `view_filters.json`.

What it resolves, and why each matters:

| Raw shape | Rendered as |
|---|---|
| `objectPropertyLookup` path `["cellValuesByFieldId", fldXXX]` | `{field:fldXXX}` → field name |
| `nodeIdentifier` with `nodeType: "trigger"` | `trigger record` (not an opaque `wtrXXX`) |
| `readProperty(readProperty(pickBranchData(…), "cellValuesByFieldId"), fldXXX)` | the field name |
| `map(X, propertyGetter("name"))` | unwrapped to `X` |
| `spread` / `array` operands inside a filter | rendered, not dropped to `null` |
| `wdtNWAY` `groups[]` | `` `Status` isAnyOf "A", "B" `` per branch |
| decision `nextWorkflowNodeIds[]` + `nextWorkflowNodeId` | branch-aware execution order |

**Graph traversal is not a flat chain.** Action nodes link via `nextWorkflowActionId`, but
**decision** nodes use `nextWorkflowNodeIds` (the branch targets) *and* `nextWorkflowNodeId`
(the continuation after the branches rejoin). Walk both or every branch body is invisible.

**`view_filters_raw.json` shape is tolerated three ways.** `fetch_view_filters.js` returns a
dict keyed by viewId; an ad-hoc `Promise.all` capture typically returns a list of
`{id, filters}` or `{viewId, filters}`. The normalizer accepts all three, so you don't have to
match one — but if you write your own capture, prefer the `fetch_view_filters.js` shape.

---

## Phase 6.5 — Form-submitted triggers need a form map

`wttFORMSUBMITTED0` triggers carry `trigger.inputExpressions.formId` — a **`pagXXX` interface
page ID**, not a table ID. The normalizer surfaces it at `trigInputs.formId`; pass
`--form-map` to `parse_and_write.py` to resolve it to a name.

Build `{pagId: formName}` from the interfaces capture (`readForPages.json` →
`unparentedPageMetadata[]`, entries with `formSourceTableIdIfExists` set). If you haven't run
`audit-airtable-interfaces` yet, run its Phase 2 first — it's a single request.

This matters more than it sounds. A form trigger binds to **one specific form**, not to the
table. Several forms can create rows in the same table while only one fires the automation —
the others look identical to a user and silently skip it. On MatchPoint (2026-07) that was
exactly the case: three forms created `Consultants`, only one sent the onboarding email.
Without the form map the audit says "a form was submitted" and the gap stays invisible.

---

## Phase 7 — Parse and write

```bash
python scripts/parse_and_write.py \
  --raw airtable_audit/automations_normalized.json \
  --out airtable_audit/automations_audit.md \
  --base-name "<Base Name>" --base-id <appId> \
  --table-map airtable_audit/table_map.json \
  --field-map airtable_audit/field_map.json \
  --view-map  airtable_audit/view_map.json \
  --view-filters airtable_audit/view_filters.json \
  --choices-map airtable_audit/choices_map.json
```

The parser:
- Resolves all `fldXXX` / `tblXXX` / `viwXXX` IDs to readable names; flags unresolved IDs
  as `⚠️ DELETED FIELD (fldXXX)` / `⚠️ DELETED TABLE (tblXXX)` — a sign the automation
  references resources that no longer exist
- Decodes both filter AST shapes (operator/operands and filterSet/conjunction)
- Decodes cron schedules from `inputExpressions.type` + `inputExpressions.config`
  (weekday integers 0=Sun…6=Sat, triggerTimes as {hour, minute} objects)
- Renders action sequences in execution order by following `nextWorkflowActionId` chains
  from `graph.entryWorkflowActionId`
- Builds the cascade map by finding automations whose UPDATE actions write fields
  another automation watches/matches/filters on

### Document structure

1. **Header + status banner** — date, base id, total count
2. **Summary table** — one row per automation: hyperlink, on/off, trigger table, trigger type
3. **Per-automation details** — trigger condition in plain English, full action sequence
   with field writes and message previews
4. **Cascade map** — for each enabled automation, which other automations could fire it

---

## Phase 8 — Validate markdown tables

The summary table (and any other table in the doc) breaks silently if an automation
name, table name, or decoded value contains an unescaped `|` — the parser escapes pipes
via its `td()` helper, so a broken row means a value reached the output without going
through it. After writing, validate with the bundled checker:

```bash
python scripts/check_tables.py
```

It scans every `**/*.md` under the current directory and verifies each markdown table's
rows all match the header's cell count (counting only unescaped pipes). Confirm
`airtable_audit/automations_audit.md` reports `OK`; if a row is flagged, fix the
offending value's escaping in the parser and re-run rather than editing the output.

---

## Output files

| File | Contents |
|------|---------|
| `airtable_audit/describes_workflows.json` | `readForWorkflows` response (full schema + base metadata) |
| `airtable_audit/raw_automations.json` | `listWorkflows` response (skeleton — IDs and names only) |
| `airtable_audit/workflow_details_raw.json` | `workflow/{id}/read` responses for all workflows |
| `airtable_audit/automations_normalized.json` | Phase 6 output — parser-ready records |
| `airtable_audit/view_filters.json` | Phase 6 output — rendered view filters |
| `scripts/normalize_workflows.py` | Phase 6 — raw AST → parser-ready records |
| `airtable_audit/view_filters_raw.json` | `view/{id}/readData` responses for "enters view" triggers |
| `airtable_audit/table_map.json`, `field_map.json`, `view_map.json`, `choices_map.json` | ID resolution maps |
| `airtable_audit/automations_audit.md` | Final audit document |
| `scripts/check_tables.py` | Markdown-table validator (Phase 7) — checks row/header cell-count parity |

---

## ⚠️ Strip `testResult` before committing the raw captures

`workflow_details_raw.json` contains **real record data**, not just definitions. Airtable
caches the last test-run payload for every automation node under `testResult`, and those
payloads carry whatever rows the automation was tested against — names, emails, addresses,
attachments.

This is easy to miss because the file looks like configuration. On MatchPoint (2026-07) it held
**~210 consultants' personal email addresses**: real job-seeker PII, in a file whose name
suggests it holds workflow definitions.

Nothing in this skill reads `testResult`. Null the keys out and verify the audit rebuilds
identically:

```python
def strip(o):
    if isinstance(o, dict):
        return {k: (None if k in ("testResult", "testResults", "lastTestRunResult") else strip(v))
                for k, v in o.items()}
    if isinstance(o, list):
        return [strip(x) for x in o]
    return o
```

Then re-run Phases 6–7 and `diff` against the previous output — it should be byte-identical.
If it isn't, something *does* depend on the payloads and you need to look before stripping.

Also scan the extracted scripts for hard-coded credentials. Well-built ones use
`input.secret("NAME")`, which resolves at run time and is safe to commit; a literal key in the
script body is not.

Create `airtable_audit/` if it doesn't exist.

---

## Handling failure modes

**401 on evaluate_script fetch calls.** The cause is almost always missing Airtable
custom headers, not an expired socket. Read them from any existing `/v0.3/` request
via `get_network_request(reqid=...)` → request headers section. Include all headers
listed in Phase 3 step 3b.

**Socket actually rotated.** If the automations page is reloaded or navigated away
from, the socket changes. Re-navigate to `/automations` and re-read the new socket
from `list_network_requests`. Do not use sockets from previous page loads.

**`evaluate_script` response too large.** Always use the `filePath` parameter to write
responses directly to disk. The saved file may be double-encoded JSON (a string
containing a JSON string) — detect with `isinstance(json.loads(raw), str)` and decode
twice if so.

**Personal view missing from schema.** After Phase 4, if a `viewId` from an automation
trigger isn't in `view_map.json`, run `mcp__airtable__describe_table` with
`identifiersOnly` for that table and merge the returned views.

**Filter expression renders as `(unknown op)`.** Some automations use date arithmetic
or cross-action node references inside match filters. Render as a best-effort
placeholder — the linked Airtable URL in the audit doc is enough for manual review.

**Newly-written helper script gets blocked by the Bash classifier.** `Read` the script
once before running it. (Claude Code quirk — not an Airtable issue.)
