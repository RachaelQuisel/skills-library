---
name: audit-softr-app
version: 1.0.0
description: >
  Audit a Softr app — every page, every block, every Airtable field touched — and map
  the read/write dependencies between Softr and Airtable. Use this skill whenever the
  user asks to document, audit, review, map, or understand a Softr portal or app,
  including questions like "what fields does the portal display?", "which pages write
  to table X?", "show me every form and what it writes to Airtable", "what views does
  Softr use?", "what data restrictions are applied per block?", "draw me the dependency
  map between Softr and Airtable", "where is field Y exposed in the portal?", or "what
  does this Softr app actually do?". The skill produces a single markdown audit document
  with: a page index, a field-level audit grouped by Airtable table (reads, writes,
  search/sort/restrict per field), and a per-page breakdown covering data sources,
  views, displayed fields, button writes, form fields, and form branching logic.
  Requires Chrome DevTools MCP, with the Softr studio open and the user signed in.
compatibility:
  tools:
    - mcp__chrome-devtools__list_pages
    - mcp__chrome-devtools__select_page
    - mcp__chrome-devtools__evaluate_script
---

# Softr App Audit

This skill produces a complete read/write audit of a Softr app: every page, every
dynamic block, every Airtable field that Softr touches, and the data restriction logic
applied on top.

The deliverable is a single markdown document at `softr_audit/softr_audit.md`, backed
by two JSON indices (`field_usage_by_table.json`, `page_index.json`) and a raw payload
dump (`raw_pages.json`) that can be re-parsed without re-hitting the API.

The goal: anyone reading the audit can answer "what does Softr show?", "what does
Softr write?", "what view/filter is each block scoped to?", and "if I change field X
in Airtable, what pages or buttons break?" without ever opening the Softr builder.

Three things make this audit useful beyond what Softr's UI exposes:
1. **View names are surfaced.** The Softr AI co-builder describes pages and blocks
   but never returns the Airtable view name. This skill queries Softr's internal
   studio API directly, where view names are always present.
2. **Forms are fully decoded.** `conditionalForm` blocks have a multi-step
   branching structure that the co-builder summarises but doesn't expand. The script
   walks every step, section, and field, captures Airtable field mappings, and
   records the step-to-step routing logic so partner-facing form flows are
   inspectable.
3. **One field-level index per table.** Instead of paging through 20+ pages to
   reverse-engineer which page reads or writes a given field, the audit groups every
   field by table and lists exactly which pages read it, which write it (via buttons
   or forms), and where it appears in search, sort, or restriction conditions.

---

## Flow at a glance

```
1. List pages       →  fetch /v1/applications/{appId}/pages/new?utilityOnly=false
                       to get every page's id/path/name
2. Per-page fetch   →  fetch /v1/applications/{appId}/pages/{pageId} for every
                       non-utility page; save the full array to raw_pages.json via
                       evaluate_script(filePath=...) so the ~4MB payload doesn't
                       round-trip through the tool channel
3. Build the doc    →  scripts/build_audit.py reads raw_pages.json, parses each
                       block's collection + elements JSON strings, and emits
                       softr_audit.md + the two JSON indices
```

Allow ~1 minute for a typical app (20–30 pages). Step 2 is sequential per-page; the
parser in step 3 is fast.

---

## Phase 1 — Auth check and discover pages

The Softr studio API uses cookie auth. The user must have the Softr builder open in
Chrome and be signed in. Check this first:

```javascript
// Run via mcp__chrome-devtools__evaluate_script after selecting the Softr studio tab
async () => {
  const r = await fetch(
    `https://studio-api.softr.io/v1/applications/${appId}/pages/new?utilityOnly=false`,
    { credentials: 'include' }
  );
  return { ok: r.ok, status: r.status };
}
```

If `ok: false` or status 401/403, ask the user to open
`https://studio.softr.io/applications/<appId>` in Chrome and sign in, then retry.

If `ok`, the response is an array of page objects with the shape:

```json
{ "id": "...", "name": "Shipment Log", "path": "/shipment-log", "enabled": true,
  "page_payload": null, ... }
```

`page_payload` is `null` on this endpoint — block data only comes back on the
per-page endpoint used in Phase 2.

**Skip these utility paths** — they have no Airtable footprint and clutter the audit:

```
/404  /401  /login  /link-expired  /account
```

**Do NOT blanket-skip `/onboarding`, `/onboarding-setup`, or `/sign-up`.** In portals with
an onboarding flow these are real content pages with large write surfaces — an `onboarding`
block can write 20+ Airtable fields. Check each app's page list before excluding anything
beyond the five above.

---

## Phase 2 — Fetch every page payload

For each non-utility page, fetch the per-page endpoint and accumulate into a single
JSON array. Write the array directly to disk via `evaluate_script(filePath=...)` so the
4MB-class payload never has to come back through the tool channel and into context.

```javascript
async () => {
  const appId = '<APP_ID>';
  const utilityPaths = new Set(['/404','/401','/login','/onboarding','/link-expired','/account']);
  const listRes = await fetch(
    `https://studio-api.softr.io/v1/applications/${appId}/pages/new?utilityOnly=false`,
    { credentials: 'include' }
  );
  const pages = await listRes.json();
  const contentPages = pages.filter(p => !utilityPaths.has(p.path));
  const all = [];
  for (const p of contentPages) {
    const r = await fetch(
      `https://studio-api.softr.io/v1/applications/${appId}/pages/${p.id}`,
      { credentials: 'include' }
    );
    all.push(await r.json());
  }
  return all;  // saved to softr_audit/raw_pages.json via filePath=
}
```

Call this as:

```
mcp__chrome-devtools__evaluate_script(
  function: <the above>,
  filePath: "softr_audit/raw_pages.json"
)
```

The tool will save the return value as JSON to that path. **Do not** return the array
inline — return `{ count: all.length }` and save with `filePath` if you want a sanity
check, then re-run with the array as the return value to save the real file. (Or just
run it once and trust the file write.)

Create `softr_audit/` if it doesn't exist.

---

## Phase 3 — Build the audit document

```bash
python3 .claude/skills/audit-softr-app/scripts/build_audit.py \
  --raw softr_audit/raw_pages.json \
  --out softr_audit/softr_audit.md \
  --field-index-out softr_audit/field_usage_by_table.json \
  --page-index-out softr_audit/page_index.json \
  --app-name "<App Name>" \
  --app-id <softr-app-uuid> \
  --schema-audit-rel ../airtable_schema_audit/schema_audit.md   # optional
```

**Always pass `--app-name` and `--app-id`.** Without them the document is titled
"Softr App" with no link. (These used to be hardcoded to a previous client's app —
if you see another client's name in the header, you're on a stale copy of the script.)

`--schema-audit-rel` cross-links table headings in the Softr audit to anchors in an
existing Airtable schema audit. Omit if no schema audit exists, or if the relative
path is different.

### What the parser extracts

For every `type: dynamic` block on every page, the parser pulls:

| Signal | Where it lives |
|---|---|
| **Data source** (base/table/view) | `collection.dataSource.airtable.{baseId, tableName, viewName}` |
| **Displayed fields** (list/detail) | `elements.fields.items[].field.mappedTo` |
| **Search fields** | `collection.searchOptions.fields` |
| **Sort order** | `collection.sortOptions[]` (`{field, direction}`) |
| **Softr-side restriction** | `collection.condition.expressions[]` |
| **Inline write actions** | `collection.actions[]` of type `UPDATE_RECORD` / `CREATE_RECORD`, each with `fields[].mappedTo` |
| **Open-page actions** | `elements.recordActions.items[]` with `action: OPEN_PAGE` + `options.destination` |
| **Form writes** | `elements.form.steps[].sections[].fields[].name` (this `name` IS the Airtable field; decorative fields like `heading1`/`text` have empty `name`) |
| **Form route table** | `collection.dataSources[0].resourceIdentifier.keys` (because `collection.dataSource.airtable` is empty for forms) |
| **Form branching** | `elements.form.steps[].conditions[]` (each has `targetStep` + `expressions`) |

### Output structure

1. **Header + summary** — app id, page count, dynamic block count, form count,
   number of Airtable tables touched.
2. **Page Index** — table of all pages (path, status, blocks, tables touched).
3. **Field-Level Audit per Airtable table** — for each table, a row per touched
   field with columns: Read on / Written on / Search-Sort-Restrict. This is the
   primary "where is field X used?" lookup.
4. **Per-Page Breakdown** — for each page, every dynamic block with its source,
   view, sort, search, restrictions, displayed fields, form fields, branching, and
   action writes.

---

## Output files

| File | Contents |
|------|----------|
| `softr_audit/raw_pages.json` | Raw per-page API responses (one array) — keep so the parser can re-run without re-hitting the API |
| `softr_audit/softr_audit.md` | The final audit document |
| `softr_audit/field_usage_by_table.json` | Machine-readable index: `{table: {field: {reads, writes, form_writes, searches, sorts, restricts}}}` |
| `softr_audit/page_index.json` | Slim per-page summary: `{id, name, path, enabled, block_count, form_count, tables}` |

Create `softr_audit/` if it doesn't exist.

---

## Critical implementation details

These are the things that surprised us during the initial exploration. Internalise
them or the parser will silently produce wrong output.

**`collection` and `elements` are JSON strings, not objects.** The block payload
shows them as top-level keys but their values are stringified JSON. Always parse
defensively — wrap `JSON.parse` in a try/catch and fall back to `{}` because some
blocks leave them as literal `"{}"` or empty.

**Form blocks hide their data source in a different place.** A `conditionalForm` or
`form3` block leaves `collection.dataSource.airtable` empty. The actual write target
lives in `collection.dataSources[0].resourceIdentifier.keys` (the plural list of
"data sources" — different from the singular `dataSource`). The parser checks both
and falls back to the plural list.

**`onboarding` blocks are forms too.** An `onboarding` block carries the same
`elements.form.steps[].sections[].fields[]` shape as `conditionalForm`, but its block name
doesn't contain "form" — so a name-only check treats it as a read-only list and silently
drops its entire write surface. Detect forms by name **or** by the presence of
`elements.form.steps`. (`build_audit.py` now does both.)

**`vibe-coding` and `custom-code` blocks are opaque.** The former is Softr's AI-generated
custom block — its JS/CSS live at external `assets.softr-files.com` URLs, not in the page
payload. The latter is arbitrary embedded HTML/JS. Neither can be parsed; flag them in the
audit as unaudited code running in an authenticated session rather than ignoring them.

**Form fields' Airtable mapping is in `.name`, not `.mappedTo`.** This is the
single biggest gotcha. List/detail blocks use `field.mappedTo`. Form blocks use
`field.name`. Decorative form fields (`heading1`, `text`, `divider`, `image`)
have empty `name` and should be skipped, not written into the audit as `(empty)`.

**Block names like `list14` or `hero1` are Softr's internal template IDs.** They
don't reflect what the block actually does in this app — they reflect which template
the user picked. The `hrid` field is similar (`accepted`, `header1`). Both are
surfaced in the audit so you can correlate to the builder UI, but neither is a
meaningful "what does this block do" label.

**The page-list endpoint returns `page_payload: null`.** Block data only comes
back from the per-page endpoint `/v1/applications/{appId}/pages/{pageId}`. Always
do the two-step fetch.

**Auth is via browser cookies (`credentials: 'include'`).** The Softr studio API
checks the same session cookie as the studio UI. If the user isn't signed in, every
fetch returns 401. Don't try to work around this by injecting tokens — just ask the
user to sign in.

**Don't return 4MB through the tool channel.** A typical app produces 3–5MB of
raw page payloads. The Chrome DevTools `evaluate_script` tool accepts a `filePath`
parameter that writes the return value directly to disk — use it. Returning the
array inline will blow your context window.

---

## Known limitations & gaps

1. **Airtable view filter conditions not captured.** The audit reports which view
   each block uses, but does not read the filter conditions set inside Airtable for
   that view. Those filters are the actual data scoping layer — combine the Softr
   restriction (in this audit) with the Airtable view filter (in the
   `airtable_schema_audit` if available, or by opening the view) for a full
   security/access-control picture.

2. **Calendar blocks have minimal field info.** The `calendar1` block type uses a
   different shape than list/list-details and the parser only surfaces source +
   sort/search, not the per-event field mapping. Calendar pages should be
   manually inspected if the field mapping matters.

3. **Static blocks are ignored.** Navigation, hero, and footer blocks have no
   Airtable footprint and are filtered out. If a static block contains hardcoded
   data references (rare), the audit will miss them.

4. **Shared blocks are not de-duplicated.** If the app uses Softr's shared-block
   feature, each instance of the shared block is treated as a separate block. This
   inflates the block count slightly but doesn't lose information.

5. **Branching conditions reference field IDs, not names.** Form branching
   expressions look like `FORM_ANSWER:::step1:::dec26ce5-3c5c-...`. The UUID is the
   form field's internal id, not the Airtable field name. Resolving these to human
   labels would require a second pass — currently they're shown as-is so the
   structure is at least visible.

---

## Handling edge cases

**A block with `collection: "{}"` or no Airtable data.** Skipped — not all dynamic
blocks have a data source (some are interactive UI like signature pads).

**A page with `enabled: false`.** Included in the audit, marked as `_disabled_` in
the Page Index. Disabled pages still hold real configuration and are useful to
audit during cleanup work.

**A sort entry with no field name.** Sometimes Softr stores a sort entry with
`field: null` (orphaned config). The parser writes it as an empty-name row in the
field index — visible as a known minor artifact, not a parser failure.

**A field used in multiple blocks on the same page.** Each block is listed
separately in the per-page section. The field index dedupes by `(table, field,
page)` so a field appearing in two blocks on the same page shows that page once
per read/write column.

**Cross-base or cross-table data sources.** Each block records its own
`baseId`/`tableName`, so an app spanning multiple bases will produce a field-level
audit grouped by table. The audit doesn't currently split by base — if you need
that, group `field_usage_by_table.json` by the base recorded alongside each block
in `raw_pages.json`.
