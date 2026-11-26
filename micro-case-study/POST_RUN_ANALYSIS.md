# Post-Run Analysis — update_mcs_fields.py

**Date:** 2026-04-20
**Script:** `update_mcs_fields.py`
**Mode tested:** `--skip-api` (file-system portion only; Airtable API portion requires a PAT scoped to base `appExample0000047` which is not currently available in this environment)

## End-to-end test sequence

| # | Command | Purpose | Result |
|---|---|---|---|
| 1 | `python3 update_mcs_fields.py --skip-api --dry-run` | Pure preview, no writes | PASS — report + diff printed, no file changes |
| 2 | `python3 update_mcs_fields.py --skip-api` | Apply file-system changes | PASS — SKILL.md patched, `update_skill.py` deleted |
| 3 | `python3 update_mcs_fields.py --skip-api` (re-run) | Idempotency | PASS — patched SKILL.md re-restored & re-patched to same content; obsolete script reports `[no-op]` |
| 4 | `diff SKILL.md.bak SKILL.md` | Scope-of-change audit | PASS — exactly 4 line changes, all inside mapping-table region |
| 5 | Grep for transcript-mining markers | Mining workflow intact | PASS — `fldExample0000048` present (1), `appExample0000049` present (1) |
| 6 | Grep for legacy field IDs | Legacy fields untouched in doc | PASS — `fldExample0000050` present (1), `fldExample0000051` present (2) |
| 7 | `ls update_skill.py` | Obsolete script gone | PASS — file not found |

## SKILL.md diff (from SKILL.md.bak → SKILL.md)

```
@@ mapping-table region @@
 | Project Name | Project Name | `fldExample0000052` |
-| Industry | Industry | `fldExample0000050` |
+| Industry | Industry (single-select) | `fldPENDING_Industry_(single-select)` (new; legacy free-text `fldExample0000050` kept intact) |
 | Situation | **Problem** | `fldExample0000053` |
 | Approach | Approach | `fldExample0000054` |
 | Analysis | Analysis | `fldExample0000055` |
 | Value | **Result 1** | `fldExample0000056` |
+| Result 2 | Result 2 (independent) | `fldPENDING_Result_2_(independent)` (new; legacy auto-mirror `fldExample0000051` kept intact) |
 | Date Completed | Date Completed | `fldExample0000057` |
...
 | Result 1 Icon | Result 1 Icon | `fldExample0000058` |
 | Result 2 Icon | Result 2 Icon | `fldExample0000059` |
+| Engineer | Engineer | `fldPENDING_Engineer` |
+| Build Time | Build Time | `fldPENDING_Build_Time` |
 | Highlight (Human) | Highlight (Human) | `fldExample0000060` |
```

**Blast radius assessment:** Changes are confined to the mapping table (lines 131, 135-136, 149-152 of the backup). No headline, no workflow prose, no ROI guidance, no Visual Assets section, no Engineer Review section, no Intake Form Fields section changed.

## Airtable portion — deferred

The Airtable field-creation steps were skipped because no PAT with `schema.bases:write` for base `appExample0000047` is available in this shell. The script's `--skip-api` path prints the intended field specs (Engineer singleCollaborator, Build Time singleSelect x4, Industry singleSelect x18, Result 2 singleLineText) and fills SKILL.md with placeholder `fldPENDING_*` IDs.

### To complete the migration

1. Generate an Airtable PAT with scopes:
   - `schema.bases:read` on base `appExample0000047`
   - `schema.bases:write` on base `appExample0000047`
2. Run:
   ```bash
   cd ~/.claude/skills/micro-case-study
   AIRTABLE_PAT='patXXXX.XXXX' python3 update_mcs_fields.py --dry-run
   AIRTABLE_PAT='patXXXX.XXXX' python3 update_mcs_fields.py
   ```
3. The script will create the four fields, then patch SKILL.md with the real field IDs (replacing the `fldPENDING_*` placeholders).
4. Per `feedback_no_secrets_in_chat.md` — do not paste the PAT into chat; set it via `export` in your shell and revoke/regenerate after the migration.

## Risk notes

- **Safe to re-run any number of times.** SKILL.md is always restored from `SKILL.md.bak` before patching, and field creation is gated on "name already exists."
- **Existing fields untouched.** `fldExample0000050` (legacy Industry) and `fldExample0000051` (legacy Result 2 auto-mirror) are not renamed, not deleted, not reconfigured — honouring `feedback_no_break_automations.md`.
- **New MCS records going forward** should populate the new fields (`Engineer`, `Build Time`, `Industry (single-select)`, `Result 2 (independent)`). Old records keep their existing values.
- **Downstream automations** that read `Industry` by field ID (`fldExample0000050`) continue to work unchanged. When you're ready to cut over, audit Zaps/automations and migrate them to the new field ID before deprecating the old — don't delete.

## Open follow-ups

- [ ] Run Airtable portion with a scoped PAT (see above)
- [ ] After real run: re-verify `describe_table` returns 4 new fields with the expected types and option lists
- [ ] Separately plan the legacy-field backfill/cutover (audit automations, backfill new field from old, then deprecate old) — this is explicitly NOT in scope of this script
- [ ] Consider deleting `SKILL.md.bak` once the new workflow is proven over a few weeks
