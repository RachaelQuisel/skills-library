# Post-Run Analysis — update_mcs_fields.py

**Date:** 2026-04-20
**Script:** `update_mcs_fields.py`
**Mode tested:** `--skip-api` (file-system portion only; Airtable API portion requires a PAT scoped to base `app8V74T72TT2SB0h` which is not currently available in this environment)

## End-to-end test sequence

| # | Command | Purpose | Result |
|---|---|---|---|
| 1 | `python3 update_mcs_fields.py --skip-api --dry-run` | Pure preview, no writes | PASS — report + diff printed, no file changes |
| 2 | `python3 update_mcs_fields.py --skip-api` | Apply file-system changes | PASS — SKILL.md patched, `update_skill.py` deleted |
| 3 | `python3 update_mcs_fields.py --skip-api` (re-run) | Idempotency | PASS — patched SKILL.md re-restored & re-patched to same content; obsolete script reports `[no-op]` |
| 4 | `diff SKILL.md.bak SKILL.md` | Scope-of-change audit | PASS — exactly 4 line changes, all inside mapping-table region |
| 5 | Grep for transcript-mining markers | Mining workflow intact | PASS — `flduLY0o5WsNiX1eL` present (1), `appMjlaeg7cFYivss` present (1) |
| 6 | Grep for legacy field IDs | Legacy fields untouched in doc | PASS — `fldoOn2odwxB0PEfG` present (1), `fldHpvofpyDNf8sb4` present (2) |
| 7 | `ls update_skill.py` | Obsolete script gone | PASS — file not found |

## SKILL.md diff (from SKILL.md.bak → SKILL.md)

```
@@ mapping-table region @@
 | Project Name | Project Name | `fldfGsRLU1ENqTXAm` |
-| Industry | Industry | `fldoOn2odwxB0PEfG` |
+| Industry | Industry (single-select) | `fldPENDING_Industry_(single-select)` (new; legacy free-text `fldoOn2odwxB0PEfG` kept intact) |
 | Situation | **Problem** | `fld1RBmjZUzGNifdR` |
 | Approach | Approach | `flddUNLOO62CCy79Y` |
 | Analysis | Analysis | `fldKS4hw4scuocsyV` |
 | Value | **Result 1** | `fld0bp8xzpAUrjsG7` |
+| Result 2 | Result 2 (independent) | `fldPENDING_Result_2_(independent)` (new; legacy auto-mirror `fldHpvofpyDNf8sb4` kept intact) |
 | Date Completed | Date Completed | `fldb3nmqVhKarB0PS` |
...
 | Result 1 Icon | Result 1 Icon | `fldFccMBzWxY1u0C7` |
 | Result 2 Icon | Result 2 Icon | `flddeJvoeH4XcSfez` |
+| Engineer | Engineer | `fldPENDING_Engineer` |
+| Build Time | Build Time | `fldPENDING_Build_Time` |
 | Highlight (Human) | Highlight (Human) | `fldijTkoO3K2bSHpk` |
```

**Blast radius assessment:** Changes are confined to the mapping table (lines 131, 135-136, 149-152 of the backup). No headline, no workflow prose, no ROI guidance, no Visual Assets section, no Engineer Review section, no Intake Form Fields section changed.

## Airtable portion — deferred

The Airtable field-creation steps were skipped because no PAT with `schema.bases:write` for base `app8V74T72TT2SB0h` is available in this shell. The script's `--skip-api` path prints the intended field specs (Engineer singleCollaborator, Build Time singleSelect x4, Industry singleSelect x18, Result 2 singleLineText) and fills SKILL.md with placeholder `fldPENDING_*` IDs.

### To complete the migration

1. Generate an Airtable PAT with scopes:
   - `schema.bases:read` on base `app8V74T72TT2SB0h`
   - `schema.bases:write` on base `app8V74T72TT2SB0h`
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
- **Existing fields untouched.** `fldoOn2odwxB0PEfG` (legacy Industry) and `fldHpvofpyDNf8sb4` (legacy Result 2 auto-mirror) are not renamed, not deleted, not reconfigured — honouring `feedback_no_break_automations.md`.
- **New MCS records going forward** should populate the new fields (`Engineer`, `Build Time`, `Industry (single-select)`, `Result 2 (independent)`). Old records keep their existing values.
- **Downstream automations** that read `Industry` by field ID (`fldoOn2odwxB0PEfG`) continue to work unchanged. When you're ready to cut over, audit Zaps/automations and migrate them to the new field ID before deprecating the old — don't delete.

## Open follow-ups

- [ ] Run Airtable portion with a scoped PAT (see above)
- [ ] After real run: re-verify `describe_table` returns 4 new fields with the expected types and option lists
- [ ] Separately plan the legacy-field backfill/cutover (audit automations, backfill new field from old, then deprecate old) — this is explicitly NOT in scope of this script
- [ ] Consider deleting `SKILL.md.bak` once the new workflow is proven over a few weeks
