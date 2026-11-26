# TODO — 10 airtable-best-practices gaps in this skill

Captured 2026-08-11 during a review of `SKILL.md` against `~/.claude/rules/airtable-best-practices.md`. Rachael requested a follow-up patch pass in a later session. This file exists so the gap list survives context loss.

Fix by editing `SKILL.md` in this same directory. Each numbered item below names the missing rule, the relevant section of `airtable-best-practices.md`, and the smallest patch that closes the gap.

## Missing from "Writing entries" section of SKILL.md

1. **`multipleRecordLinks` write format not stated.** The skill scaffolds per-target linked-record fields and writes to them, but never says the write value is `["recXXX", "recYYY"]` (array of record ID strings). Add to the "Writing entries — Airtable API rules" list. Ref: airtable-best-practices §4.

2. **`no-break-automations` rule not called out.** Once the log's field IDs are captured and other automations start reading them (which is the whole point of an audit log), those fields must not be renamed or deleted without checking `schema-dependencies.md`. Add as a paragraph at the end of "Field-ID discipline". Ref: airtable-best-practices §6.

## Missing from "Reading entries back" section of SKILL.md

3. **Linked-record filter trap not warned.** `filterByFormula` with `ARRAYJOIN`/`FIND`/`SEARCH` on the per-target linked-record fields silently returns 0. If a downstream tool tries to query "all log entries where Linked Student = recXXX", it must pull the recordset and filter locally. Add as a bullet. Ref: airtable-best-practices §5.

4. **MCP structured-filter choice-ID rule not stated.** Reading back "all Action = Decision" via MCP structured filters requires the `selXXX` choice ID from `get_table_schema`, not the display name. Add as a bullet. Ref: airtable-best-practices §5.

## Missing from the "Scaffolding" side (biggest gaps for a Rachael client base)

5. **Seven Deliverables trigger not called out.** Scaffolding this table on a client base IS a schema change. On any client base (CC / EA / EH / Example Client), the scaffold fires all seven deliverables — design doc, script, /rubric pass, dry-run, apply, diff doc, Automation Inventory row, post-run analysis. Add as a dedicated "Client-base scaffolding" section that references `~/.claude/rules/seven-deliverables.md`.

6. **Script sequence not stated.** Scaffolding must be a script that goes `write → dry-run → /review → --apply → post-run`, not a live MCP call spree. Add to the same "Client-base scaffolding" section.

7. **`no-cross-table-links` tension not acknowledged.** Rachael's standing rule is "no new linked-record fields unless asked." The whole point of this skill is per-target linked-record fields for reverse navigation. The skill must say: get explicit yes on EACH target-table linked field, not a blanket yes on the whole table. Ref: memory `feedback_no_cross_table_links`.

8. **"Re-pull LIVE schema first" not stated.** Before scaffolding per-target linked fields to Students / Service Plan / etc., live-query the destination tables to confirm they exist and get their current IDs. Never trust memory or a doc snapshot. Add to the scaffolding routine. Ref: memory `feedback_inventory_live_schema_first`.

9. **"Default to MCP, look up IDs yourself" not stated.** The scaffolding routine should not ask the user for IDs — it should MCP the base and enumerate. Add to scaffolding routine. Ref: memory `feedback_use_airtable_mcp_first`.

## Stale reference

10. **Pattern A / Pattern B section conflates two different tables** — `🤖 Automation Inventory` (config, one row per automation) vs `🤖 Automation Log` (per-fire activity, one row per fire). Discovery on CC (2026-08-11) showed CC has BOTH tables. Pattern A/B needs to be rewritten to distinguish:
    - Config table (`Automation Inventory`) — wrong target for agent activity
    - Per-fire activity table (`Automation Log`) — the real prior art on CC, built May 2026, uses `Code/log-automation.js` drop-in helper
    - Agent activity log (this skill) — decisions and blockers, different grain from either of the above

    The rewrite should recommend: separate table for agent-session logs, with a note that the CC pattern (per-fire logs via a drop-in JS helper) is a good model to imitate for reliability discipline.

## Suggested patch order

1. Do items 1–4 first — small, targeted edits within existing sections.
2. Do items 5–9 next — add a new "Client-base scaffolding" section, single write.
3. Do item 10 last — biggest edit (rewrite of Pattern A/B section based on the CC discovery).

Each patch should be small and reviewable — do not fold all ten into one Edit.
