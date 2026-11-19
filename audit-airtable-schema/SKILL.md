---
name: audit-airtable-schema
version: 1.0.0
description: >
  Audit the complete schema of an Airtable base — every table, every field — and map the
  dependencies and logic spread across the system. Use this skill whenever the user asks
  to document, audit, review, map, or understand the data structure of an Airtable base,
  including questions like "what tables exist in this base?", "what fields are in X?",
  "how do these tables connect?", "what formulas reference Field Y?", "draw me an ERD",
  "what does this base look like?", or "where is the logic hidden?". The skill produces
  a single markdown audit document with: a Mermaid ERD showing every linked-record
  relationship, per-table sections covering every field (type, description, formula text,
  cross-table references), a cross-table dependency map (rollups, lookups, formula
  references), and AI-drafted descriptions for fields that don't have one in Airtable.
  Requires the Airtable MCP.
compatibility:
  tools:
    - mcp__airtable__list_tables
    - mcp__airtable__describe_table
---

# Airtable Base Schema Audit

This skill produces a complete schema audit of an Airtable base: every table, every
field, every dependency. The output is a single markdown document at
`airtable_schema_audit/schema_audit.md` plus a standalone Mermaid ERD source at
`airtable_schema_audit/erd.mmd`.

The goal: anyone reading the audit can answer "what does this base contain?", "how do
these tables connect?", and "if I change field X, what else does that touch?" without
opening Airtable.

Three things make this audit useful beyond a plain field list:
1. **Field descriptions are filled in.** Airtable lets users add descriptions per field,
   but most bases don't. For every field without one, draft a 1–2 sentence description
   from the field name, type, options, table context, and linked tables. Drafted
   descriptions are tagged `_(AI-drafted)_` in the output so the user can spot which
   still need human review.
2. **Dependencies are explicit.** Linked-record fields, rollups, lookups, and formula
   `{Field Name}` references all surface as edges in either the ERD or the cross-table
   dependency section. The reader doesn't have to chase fields manually.
3. **One ERD covers the whole base.** Mermaid syntax means the diagram lives inside the
   markdown — no external rendering, no broken image links.

---

## Flow at a glance

```
1. List tables       →  mcp__airtable__list_tables(detailLevel: tableIdentifiersOnly)
2. Describe each     →  mcp__airtable__describe_table(tableId, detailLevel: "full")
                        for every table — captures field types, descriptions, choices,
                        formula text, linked-record metadata
3. Draft descriptions → for every field whose `description` is empty/missing, write a
                        1–2 sentence draft. Save all drafts to description_drafts.json
4. Build the doc     → scripts/build_audit.py reads raw schema + drafts, emits
                        schema_audit.md + erd.mmd
```

Allow ~3 minutes for a base with ~30 tables. The heavy step is step 2 (one MCP call per
table); steps 3 and 4 are fast.

---

## Phase 1 — Get the table list

```
mcp__airtable__list_tables(baseId: "<appId>", detailLevel: "tableIdentifiersOnly")
```

Returns `[{id, name}, ...]`. Save the list — you'll iterate over it in Phase 2.

---

## Phase 2 — Describe every table

For each table, call:

```
mcp__airtable__describe_table(
  baseId: "<appId>",
  tableId: "<tableId>",
  detailLevel: "full"
)
```

`full` returns:
- Table-level: `id`, `name`, `description`, `fields`, `views`. **Note:** the
  Airtable MCP's `describe_table` does NOT currently include `primaryFieldId` —
  the build script falls back to the first field in the `fields` array, which
  Airtable always places at index 0 as the primary field.
- Per field: `id`, `name`, `description`, `type`, and `options` (type-specific)

Save each response into a combined JSON array at
`airtable_schema_audit/raw_schema.json`. The build script expects a JSON array of full
table objects (one per table).

### Field type cheat-sheet

These are the types whose `options` contain dependency information the build script
parses. Other types (text, number, date, etc.) just need name + description:

| Type | Relevant `options` fields | What it tells you |
|---|---|---|
| `singleSelect`, `multipleSelects` | `choices: [{id, name, color}]` | enum values — listed in the audit |
| `formula` | `formula` (text), `result.type`, `isValid` | the formula text. Parsed for `{Field Name}` refs |
| `multipleRecordLinks` | `linkedTableId`, `prefersSingleRecordLink`, `inverseLinkFieldId` | a link to another table → ERD edge |
| `rollup` | `recordLinkFieldId`, `fieldIdInLinkedTable`, `formula` | aggregates a field from a linked table |
| `lookup` | `recordLinkFieldId`, `fieldIdInLinkedTable` | pulls a value from a linked table |
| `count` | `recordLinkFieldId` | counts records in a linked table |

The build script handles all of these. You don't need to do any field-level processing
in Phase 2 — just save the raw response.

### Handling large tables

A table with 200+ fields may push a single `describe_table` at `full` past the response
token limit. If you see truncation, retry that one table with `detailLevel:
"identifiersOnly"` to get the field list, then loop in smaller chunks via
`detailLevel: "full"` per table is the only option the MCP offers — there is no
field-level filter. In practice, this rarely happens; if it does, fall back to keeping
that table's data at `identifiersOnly` and noting in the audit that descriptions
weren't available for it.

---

## Phase 3 — Draft missing field descriptions

After Phase 2 you have `raw_schema.json` with every field's existing description (where
present). For each field where `description` is empty, missing, or whitespace-only,
draft a 1–2 sentence description based on:

- The **field name** (often the strongest signal — `Load Date`, `Partner Email`, etc.)
- The **type and options** — a `singleSelect` with choices `Allocated`, `Loaded`,
  `Delivered` is a workflow status; a `multipleRecordLinks → Partners` named "Partner"
  is the foreign key.
- The **surrounding fields** in the same table — what's the table modeling overall?
- The **linked tables** — if this field is a rollup of `Total Weight` from `Line Items`,
  describe it as "total weight rolled up from the shipment's line items."

Save drafts as a JSON file at `airtable_schema_audit/description_drafts.json`:

```json
{
  "<tableId>": {
    "<fieldId>": "Date the shipment is scheduled to leave the warehouse."
  }
}
```

Keep drafts to 1–2 sentences. Don't repeat the field name verbatim. Don't fabricate
business meaning that isn't supported by the schema — when uncertain, write something
descriptive of the data type and let the user revise.

Examples of good drafts:
- `Load Date` → "Date the shipment is scheduled to leave the warehouse."
- `FS` (linked to People) → "Field service staff member assigned as the primary owner of this shipment."
- `Boxes Total` (number) → "Sum of box counts across all line items for the shipment."

Examples of drafts to avoid:
- "The Load Date." (just restates the name)
- "Date field." (just restates the type)
- "Important shipment metadata used by automations." (vague, claims unsupported context)

---

## Phase 3.5 — Merge rollup/lookup conditions (do this if you have an automations capture)

**The public Metadata API and the MCP do not return a rollup's or lookup's filter.** They
return the link field, the target field, and the aggregation formula — and stop. This is not a
cosmetic omission. A base can carry several rollups that are *identical* at the public API
level and differ only by a hidden condition.

Real example (MatchPoint, 2026-07): four rollups on `Consultants` all rolled up
`Clearances.Is Valid` through the same link field. Through the MCP they were four duplicates.
In truth each filtered on a different `Type` — and one of them filtered on the **wrong** type,
so "does this consultant hold a State Police clearance?" was silently answering "does this
consultant hold a TB test?". An audit built from the public API alone renders that as four
redundant fields and misses the defect entirely.

The internal `readForWorkflows` schema **does** expose them, at
`columns[].typeOptions.filters`. If you ran `audit-airtable-automations-report` you already have that
capture. Merge it in:

```bash
python scripts/merge_internal_options.py \
  --raw airtable_schema_audit/raw_schema.json \
  --internal airtable_audit/describes_workflows.json
```

This writes a pre-rendered human string to `options.conditionsRendered` on each affected
field, which `build_audit.py` appends to the Notes cell as **only where** `…`. Select-option
IDs are resolved to labels. The script is idempotent — safe to re-run.

Skip it if you have no automations capture; the audit still builds, it just won't show
conditions. **Say so in the audit if you skipped it**, so a reader doesn't take
"four identical rollups" at face value.

---

## Phase 4 — Build the audit document

```bash
python scripts/build_audit.py \
  --raw airtable_schema_audit/raw_schema.json \
  --drafts airtable_schema_audit/description_drafts.json \
  --base-name "<Base Name>" \
  --base-id <appId> \
  --out airtable_schema_audit/schema_audit.md \
  --erd-out airtable_schema_audit/erd.mmd
```

The script:
- Resolves every linked-record field to its target table → ERD edges
- For each rollup/lookup, resolves the linked field to its source → cross-table dep list
- For each formula, regex-parses `{Field Name}` references → in-table and cross-table refs
- Merges drafted descriptions with the `_(AI-drafted)_` tag
- Emits the Mermaid ERD inline in the markdown AND as a standalone `.mmd` file (so it
  can be re-rendered without re-parsing the schema)

### Output structure

1. **Header + summary** — base name, ID, table count, field count, link count, count of
   AI-drafted descriptions.
2. **Entity-Relationship Diagram** — Mermaid `erDiagram`. Tables as nodes; linked-record
   fields as edges. Cardinality uses `}o--||` (many-to-one) when
   `prefersSingleRecordLink` is true, otherwise `}o--o{` (many-to-many).
3. **Cross-table dependencies** — one bullet per rollup, lookup, count, or formula that
   references another table. Format:
   `{TableA}.{FieldX} → rolls up {TableB}.{FieldY} via {LinkField}`
4. **Per-table sections** — alphabetical or in original order, each with:
   - Table description (existing or drafted)
   - Field-count and primary-field name
   - A table of every field: name, type, description, notes (formula text, link target,
     enum choices)

---

## Phase 5 — Validate markdown tables

The audit doc is almost entirely markdown tables (one per table section). A field
description or formula containing an unescaped `|` will silently break a row's column
count. After building, validate with the bundled checker:

```bash
python scripts/check_tables.py
```

It scans every `**/*.md` under the current directory and, for each markdown table,
verifies that every row has the same cell count as its header (counting only unescaped
pipes). Confirm `airtable_schema_audit/schema_audit.md` reports `OK`. If it flags a row,
the cause is almost always an unescaped `|` in a formula or description — the build
script escapes pipes via `md_escape`, so a failure points at a value that bypassed it;
fix the source and rebuild rather than hand-editing the output.

---

## Output files

| File | Contents |
|------|----------|
| `airtable_schema_audit/raw_schema.json` | Raw per-table `describe_table` responses (enriched in place by Phase 3.5) |
| `scripts/merge_internal_options.py` | Phase 3.5 — merges rollup/lookup filter conditions from the internal schema |
| `airtable_schema_audit/description_drafts.json` | AI-drafted descriptions, keyed by tableId/fieldId |
| `airtable_schema_audit/erd.mmd` | Standalone Mermaid ERD (also embedded in the audit doc) |
| `airtable_schema_audit/schema_audit.md` | The final audit document |
| `scripts/check_tables.py` | Markdown-table validator (Phase 5) — checks row/header cell-count parity |

Create `airtable_schema_audit/` if it doesn't exist.

---

## Handling edge cases

**Field with `description` set to an empty string vs. missing.** Treat both as "needs a
draft." Airtable sometimes returns `""` for fields the user explicitly cleared.

**Linked record with `linkedTableId` pointing at a table not in this base.** Rare, but
possible (cross-base syncs). The build script renders these as `linked: tblXXX (external)`
and skips the ERD edge.

**Rollups/lookups whose `fieldIdInLinkedTable` is missing.** Treat as "broken reference"
and call it out in the cross-table dependency section so the user knows there's a stale
link to clean up.

**Formula references that don't match a known field name.** Probably typed against a
since-renamed field. Render as `(unresolved: "Old Name")` in the dependency list.

**The ERD is unreadable on a big base.** Mermaid can render 30+ tables but the layout
gets dense. Keep entity blocks empty (table name only, no field rows inside) — field
detail belongs in the per-table sections, not the diagram.
