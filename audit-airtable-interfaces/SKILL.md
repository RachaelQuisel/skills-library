---
name: audit-airtable-interfaces
description: >
  Audit an Airtable base's Interfaces (Interface Designer apps): every interface, page, data element and button, and which clicks, forms and edits fire automations. Use when the user asks to document, audit, review or map Airtable interfaces, find which buttons trigger which automations, or trace a UI action into a workflow. Run after audit-airtable-schema and audit-airtable-automations-report.
version: 1.0.0
---
# Airtable Interfaces Audit

This skill produces a complete audit of an Airtable base's **Interfaces** (the published
apps built in Interface Designer): every interface, every page, every data element, every
button/action, and — the part that matters most — **how interface actions trigger the
base's automations**.

Output: `<base>_interfaces_audit/interfaces_audit.md`. It answers, without opening Airtable:

- **What interfaces and pages exist** and what each is for (the left-nav apps, plus the
  forms and record-detail pages that aren't in the nav).
- **Where data can be READ** — every element's source table and filters.
- **Where data can be MODIFIED** — editable grids (cell edit / inline create / delete),
  editable record fields, and forms (which table each writes to).
- **Which clicks/edits fire an automation** — buttons wired to `triggerWorkflow`, form
  submissions, `updateRow` buttons that write a watched field, and inline create/edit on
  tables that have create/update automations. Each is cross-referenced to the
  **automations audit** so you can trace a button press all the way into a workflow (and,
  via the automations cascade map, into the workflows *that* one triggers).

This is the third audit in the set. Run it **after** the schema and automations audits so
the cross-reference is available:

1. `audit-airtable-schema` → tables and fields
2. `audit-airtable-automations-report` → workflows + cascade map (produces `automations_normalized.json`)
3. `audit-airtable-interfaces` → **this** — the human/UI entry points into all of it

---

## Mental model: how interfaces are structured

```
Interface (page bundle, pbdXXX)         e.g. "Orders", "Logistics", "Analytics"
  └─ Page (pagXXX)                       a screen in the left nav
       ├─ layout type                    dashboard | queryContainer | recordContainer | formContainer
       └─ elementById{}                  the widgets on the page
            ├─ queryContainer / levels / grid / kanban / gallery / calendar
            │                            ── a data view (reads ONE table; may be editable)
            ├─ bigNumber / chart / pivotTable / dashboard
            │                            ── a read-only visualization
            ├─ cellEditor                ── one field of one record (read or write)
            ├─ formContainer             ── a form that creates/updates rows
            └─ button                    ── an action (see action table below)
```

Two page collections come back from the API:

- **`pageBundles[]`** — the interfaces and their nav pages (`dashboard` / `queryContainer`
  layouts). Each page has `metadata.name`, `metadata.isHiddenFromNavigation`, `isPublished`.
- **`unparentedPageMetadata[]`** — pages **not** in the nav: `formContainer` pages
  (standalone data-entry forms; each has `formSourceTableIdIfExists`) and `recordContainer`
  pages (the record-detail screens that open when you expand a row — this is where most
  field editors and buttons live). Many have `name: null`; the parser names them after
  their record table.

A `recordContainer` page's primary record table is at the **page-level**
`value.rootRowContainer.tableId` (not inside an element).

---

## The four interface → automation linkage paths

This is the heart of the audit. An interface can set off an automation four ways:

| # | Interface action | How it's detected | Fires |
|---|---|---|---|
| **A** | Button with `action.type = "triggerWorkflow"` | `workflowTriggerConnectionsById` maps `(pageId, buttonElementId)` → `workflowId` | that workflow directly |
| **B** | Form page submitted | automation whose `trigInputs.formId == pageId` | `wttFORMSUBMITTED0` automation |
| **C** | Button with `action.type = "updateRow"` setting field F on table T | automation on T whose `watchFields`/`filterFieldIds` includes F | `wttRECORDUPDATED0` / `wttRECORDMATCHES0` automation |
| **D** | Inline grid create/edit, or form create, on table T | automations on T: `wttRECORDCREATED0` (create), any-field `wttRECORDUPDATED0` (edit), `wttRECORDMATCHES0`/`wttBRZzRXx3C2jyIc` (either, if the row matches) | those automations |

Path A is an explicit wiring. Paths B–D are **implicit**: the interface writes data, and a
data-triggered automation happens to watch it. Those are the dangerous, easy-to-miss ones —
a button labeled "Confirm Order" silently drives the whole Sales Order status state machine.

`workflowTriggerConnectionsById` is the key that makes path A resolvable. A `triggerWorkflow`
button's own JSON does **not** name the workflow — only the connection record does. A button
with no matching connection is an **orphaned trigger** (deleted workflow or never published) —
flag it.

---

## Flow at a glance

```
1. Open an interface in edit mode   → /<appId>/<pageId>/edit  (triggers readForPages)
2. Save readForPages (as JSON)       → master: schema + bundles + unparented + connections
3. Enumerate all page IDs            → bundles[].pages[] + unparentedPageMetadata[]
4. Fetch every page's readDraft       → evaluate_script Promise.all → all_page_drafts.json
5. Build the audit                   → build_interfaces_audit.py (cross-refs automations)
```

Allow ~2 minutes for a base with ~90 pages. Everything is **read-only GET** — this audit
never writes to the base.

---

## Phase 1 — Session setup

Navigate to an **interface page in edit mode** (the user usually has one open). This fires
the master request automatically:

```
mcp__chrome-devtools__navigate_page(type:"reload")   # if already on a /<appId>/<pageId>/edit URL
mcp__chrome-devtools__list_network_requests(resourceTypes:["fetch","xhr"], pageSize:80)
```

Find and note from the request list / headers (inspect any `/v0.3/` request with
`get_network_request`):

- `GET /v0.3/application/<appId>/readForPages…` — the master (see Phase 2)
- `GET /v0.3/page/<pageId>/readDraft…` — a single page layout (confirms `expectedPageLayoutSchemaVersion`)
- `secretSocketId=socXXX` (from any `/v0.3/` URL)
- `x-airtable-page-load-id` (from request headers)
- `x-airtable-inter-service-client-code-version` — **optional**. It is often absent from the
  `readForPages`/`readDraft` request headers. If you can't find it, **omit it entirely** — do
  not send the string `undefined`. The fetches below return 200 without it. (Only add it if a
  `/v0.3/` request actually carries it and you start seeing 401s without it.)

The socket is valid for the whole page session. 401s are caused by **missing headers**, not
socket expiry (same as the automations skill). `x-time-zone` does **not** need to match the
captured request — any valid zone works for schema/layout reads.

---

## Phase 2 — Master document (`readForPages`)

The browser requests `readForPages` with `x-airtable-accept-msgpack: true`, so the captured
response is **msgpack (binary)**, not JSON. **Do not** try to parse the network-panel copy.
Instead re-fetch it as JSON via `evaluate_script` (omit the msgpack header → server returns
JSON):

```js
async () => {
  const appId = '<appId>', sock = '<socketId>';
  const headers = {
    'x-airtable-inter-service-client':'webClient',
    // include the next line ONLY if you actually found a code-version; otherwise delete it:
    // 'x-airtable-inter-service-client-code-version':'<codeVersion>',
    'x-airtable-page-load-id':'<pageLoadId>',
    'x-airtable-application-id':appId,
    'x-time-zone':'America/New_York','x-requested-with':'XMLHttpRequest',
    'x-user-locale':'en','accept':'application/json, text/javascript, */*; q=0.01',
    'x-airtable-client-queue-time':'0'
  };
  const params = { shouldIncludeSchemaChecksum:false, expectedPageLayoutSchemaVersion:26,
    shouldPreloadQueries:false, shouldPreloadAllPossibleContainerElementQueries:false,
    includeDataForExpandedRowPageFromQueryContainer:false,
    includeDataForAllReferencedExpandedRowPagesInLayout:false,
    includePageLayoutTypeInfo:true, navigationMode:'edit' };
  const url = `https://airtable.com/v0.3/application/${appId}/readForPages`
    + `?stringifiedObjectParams=${encodeURIComponent(JSON.stringify(params))}`
    + `&requestId=reqPagesIdx001&secretSocketId=${sock}`;
  const r = await fetch(url,{credentials:'include',headers});
  const txt = await r.text();
  return JSON.stringify({ ok:r.ok, status:r.status, body:txt });
}
```

Save with `filePath`. Because `evaluate_script(filePath:…)` persists the function's **return
value**, a returned `JSON.stringify(...)` lands on disk as a JSON-encoded string (a string
containing JSON) — and if you stringify the `{ok,status,body}` wrapper, `body` is itself a
JSON string, so the file is **double-encoded**. That is expected and fine: the build script's
`load_json_maybe_double()` peels however many layers it takes. The only requirement is that
`raw/readForPages.json` decodes (after peeling) to the `{msg, data}` object. Simplest reliable
recipe: in the fetch function `return JSON.stringify({msg: j.msg, data: j.data})` where
`j = await r.json()`, and save that to `raw/readForPages.json`. `shouldPreloadQueries:false`
keeps it to schema+layout (no row data — we are documenting structure, not records).

`data` carries:

| Key | Use |
|---|---|
| `tableSchemas[]` | tables, columns (`t.columns` — **not** `fields`), choices → ID resolution |
| `pageBundles[]` | interfaces + their nav pages (`.pages[].metadata`, `.pageLayoutTypeInfo`) |
| `unparentedPageMetadata[]` | form + record-detail pages (`formSourceTableIdIfExists`, redirects) |
| `pageSections[]` | nav grouping of bundles (optional) |
| `workflowTriggerConnectionsById` | **(pageId, buttonElementId) → workflowId** — path A |
| `sharesById` | publish/share settings (who can see each interface) |

---

## Phase 3 — Every page's layout (`readDraft`)

Collect all page IDs from `pageBundles[].pages[]` + `unparentedPageMetadata[]` — **dedupe
them** (`[...new Set(ids)]`); the two collections don't overlap here but a Set guards against
it. (Typical result: ~32 bundle pages + ~60 unparented = ~90.) Then fetch each page's layout
in one parallel call (same headers as Phase 2):

```js
const op = encodeURIComponent(JSON.stringify({expectedPageLayoutSchemaVersion:26}));
const results = await Promise.all(ids.map(async (id,i) => {
  const url = `https://airtable.com/v0.3/page/${id}/readDraft?stringifiedObjectParams=${op}`
    + `&requestId=reqDraft${i}&secretSocketId=${sock}`;
  const r = await fetch(url,{credentials:'include',headers});
  if(!r.ok) return {id, httpError:r.status};
  const j = await r.json();
  return {id, value: j.data && j.data.value ? j.data.value : j.data};
}));
window.__drafts = results;
return JSON.stringify({total:results.length, errors:results.filter(r=>r.httpError).map(r=>r.id)});
```

Then save: `evaluate_script(function:"() => JSON.stringify(window.__drafts)", filePath:"…/raw/all_page_drafts.json")`.

`readDraft` returns the **working draft** (edit-mode) layout, which is what you want for an
audit — it includes unpublished changes. Each `value` has `elementById` (the widgets),
`rootRowContainer` (record-detail page's table), and canvas/slot maps (layout geometry,
ignored by the parser).

### Element & action reference

**Element types** (`element.type`):

| Type | Reads | Editable? | Notes |
|---|---|---|---|
| `queryContainer` | `source.tableId` | via `editability` | list with `savedFilterSets`/`presetFilters`, `endUserControls` |
| `levels` | `leafTableId` / `queryByLevel` | `editability` | grouped grid/list; `expandedRowByTableId` → detail page |
| `grid`,`kanban`,`gallery`,`calendar` | `query.source…tableId` | `editability` | other view styles |
| `bigNumber`,`chart`,`pivotTable`,`dashboard` | `query.source…tableId` | read-only | KPI/visualization; `filters` per element |
| `cellEditor` | `source.row.tableId` + `columnId` | `isReadOnly:false` ⇒ writable | one field of one record |
| `formContainer` | `action.tableId` | writes | `action.type` = `createRow`/`updateRow`; `requiredColumnIds`, `prefilledCellValueByColumnId` |
| `button` | — | — | see actions below |
| `section`,`sectionGridRow`,`verticalStack`,`text`,`rowActivityFeed` | — | — | layout/chrome, no data |

`editability = {canUpdateAllVisibleCells, canCreateRowsInline, canDestroyRows}`.

**Button actions** (`button.action.type`):

| Action | Meaning | Key fields |
|---|---|---|
| `triggerWorkflow` | run an automation (path A) | resolve workflow via `workflowTriggerConnectionsById` |
| `updateRow` | write fields to the current row (path C) | `columnUpdateSet[]` = `{columnId, value, updateBehavior}` |
| `deleteRow` | delete the current row | `rowInput.tableId` |
| `addForeignRow` | create + link a record | `tableId`, `foreignColumnId`, `embeddedFormButton.pageId` |
| `openFormModalDialog` | open an embedded create form | `tableId`, `embeddedFormButton.pageId` |
| `navigateToSelectedPage` | go to another interface page | `selectedPageId` |
| `navigateToStaticUrl` | open a URL (often `…/<pageId>/form`) | `url` |

Buttons may carry `visibilityFilters` (only shown when the row matches — render it; a
"Send PO" button visible only when `Order Status ∈ {…}` documents the real workflow gate)
and a confirmation modal (`isConfirmationModalEnabled`, `confirmationModalMessage`).

### Filter AST

Page elements use the **`filterSet`/`conjunction`** shape (same as view filters in the
automations skill): each entry is a leaf `{columnId, operator, value}` or a nested
`{type:"nested", conjunction, filterSet:[…]}`. Unary ops (`isEmpty`, `isNotEmpty`) have
`value:null`. Date-relative values use `{mode:"withinExactDates"|"daysAgo", …}`. The parser's
`render_filters()` handles all of these.

---

## Phase 4 — Build the audit

Run from the repo root (or use absolute paths). The script lives at
`.claude/skills/audit-airtable-interfaces/scripts/build_interfaces_audit.py`:

```bash
python .claude/skills/audit-airtable-interfaces/scripts/build_interfaces_audit.py \
  --raw-dir <base>_interfaces_audit/raw \
  --automations <base>_automations_audit/automations_normalized.json \
  --base-name "<Base Name>" \
  --base-id <appId> \
  --out <base>_interfaces_audit/interfaces_audit.md \
  --date <YYYY-MM-DD>
```

`--automations` is optional but **strongly recommended** — without it, sections 2b–2d can't
name the triggered workflows. The script makes no network calls.

### Output structure

1. **Summary** — interface/page/button counts, action mix, write-surface count.
2. **Interface inventory** — per bundle: pages, layout, live/hidden/unpublished. Plus the
   forms (→ source table, post-submit redirect) and record-detail pages.
3. **Interface → automation trigger map** — the four-path table (2a–2d). The headline.
4. **Data read/write surface by page** — one row per page: tables read, **editable fields
   qualified as `Table.Field`** (record-field editors + inline-grid columns, with `[+create]`
   / `[+delete]` / `FORM-createRow` row-level tags), and the **directly-connected automations**
   that page's buttons/form can fire (paths 2a–2c).
5. **Page navigation map** — row-expand, button nav, embedded forms, form redirects.
6. **Per-page detail** — every page: reads (with filters), forms, buttons (resolved
   actions + visibility), and the editable fields grouped by table (`Table.Field`).

**Hyperlinks.** Every page reference links to `https://airtable.com/<appId>/<pageId>` and
every automation reference links to its workflow (`…/<workflowId>`), so the document is
navigable straight into Airtable. Page-name resolution falls back to the page's record table
for the many unnamed record-detail pages (e.g. "Sales Order detail (pagPQ8IZ…)").

**Editable-field enumeration.** Per-field editability comes from two sources: `cellEditor`
elements with `isReadOnly:false` (record-detail field editors) and inline-editable grids
(`canUpdateAllVisibleCells`), whose columns are read from
`levelsConfig.leafLevel.allOrderedDisplayColumnIds`. Both are rendered as `Table.Field`.

---

## Output files

| File | Contents |
|---|---|
| `raw/readForPages.json` | master `{msg,data}` (schema + bundles + connections), re-fetched as JSON |
| `raw/all_page_drafts.json` | list of `{id, value}` — every page's `readDraft` layout |
| `raw/all_page_ids.json` | the page-ID list (convenience) |
| `page_inventory.json` | bundles → pages with names/types (convenience) |
| `interfaces_audit.md` | the final document |

Create `<base>_interfaces_audit/raw/` if it doesn't exist.

---

## Validation

After building, sanity-check the document:

```bash
python scripts/check_pages.py <base>_interfaces_audit/interfaces_audit.md
```

It verifies every Markdown table is well-formed (no ragged rows) and reports counts of
unresolved IDs (`⚠️DELETED …`) and orphaned trigger buttons (`NO CONNECTION`).

**Interpreting `⚠️DELETED` counts — count distinct IDs, not references.** One deleted table
can produce dozens of `⚠️DELETED` references (every page, grid column, and field that touches
it), so the raw reference count is alarming but misleading. Before deciding it's a real finding
vs. a capture gap: (1) extract the **distinct** `tbl…`/`fld…` IDs from the report, and
(2) cross-check against a live table list — `mcp__airtable__list_tables(baseId, detailLevel:
"tableIdentifiersOnly")`. If the base's table count equals the parser's `tableSchemas` count
and the missing IDs genuinely aren't in the base, the references are **real findings** (stale
interface pages pointing at deleted tables) — call them out, don't suppress them. If many IDs
*do* exist in the base but not in `tableSchemas`, your capture was incomplete — re-fetch
`readForPages`.

---

## Handling failure modes

**`readForPages` is msgpack / unreadable.** Expected — re-fetch as JSON via `evaluate_script`
(Phase 2). Never parse the network-panel binary copy.

**401 on `evaluate_script` fetches.** Missing Airtable headers, not socket expiry. Copy the
full header set from any `/v0.3/` request via `get_network_request`.

**A page's `readDraft` errors.** Personal/unpublished pages occasionally 403. The parser
skips any page with no `value`; note the gap in the audit rather than failing the run.

**Button names a workflow that isn't in the automations audit.** The automations audit may
have been run earlier and missed a new workflow — re-run it, or note the workflow ID as
unresolved. A `triggerWorkflow` button with **no** `workflowTriggerConnectionsById` entry is
a genuine orphaned trigger (deleted/unpublished workflow) — keep it flagged.

**`⚠️DELETED TABLE/FIELD`.** The interface references a table/field absent from
`tableSchemas`. Real finding: a stale page. (Confirm `tableSchemas` is complete — its table
count should match the schema audit.)

**`TypeError: cannot use 'dict' as a dict key`.** A filter value arrived as a *list of
dicts* (structured date-relative or linked-record specs), which never reaches
`render_leaf`'s dict branch and lands in `Resolver.c()` as an unhashable key. `c()` is now
total (handles dict/list/non-str); if you hit a variant it still misses, extend `c()` rather
than special-casing the caller.

**A grid reports editable columns but `levelsConfig.leafLevel.allOrderedDisplayColumnIds`
is `[]`.** That's normal for plain `grid` elements — the real list is `visibleColumnIds` at
the element level. `editable_columns()` falls through to it. An empty result there means the
grid genuinely shows no columns, not a parse failure.

**Newly-written helper script blocked by the Bash classifier.** `Read` the script once before
running it (Claude Code quirk, not Airtable).
