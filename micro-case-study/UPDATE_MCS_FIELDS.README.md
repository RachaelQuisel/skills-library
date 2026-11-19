# update_mcs_fields.py

One-shot migration script that adds four new fields to the MCS Airtable table
and patches the `SKILL.md` mapping table to point at them.

## What it changes

**Airtable — base `app8V74T72TT2SB0h`, table `tbl4fNYChMVv8pyda` (MCS):**

| Field | Type | Options |
|---|---|---|
| `Engineer` | Collaborator (single user) | — |
| `Build Time` | Single select | 2-4 hours, 5-10 hours, 11-20 hours, 21+ hours |
| `Industry (single-select)` | Single select | 18 canonical industries |
| `Result 2 (independent)` | Single-line text | — |

**Not touched** (per `feedback_no_break_automations.md`):
- Existing `Industry` (`fldoOn2odwxB0PEfG`) free-text field
- Existing `Result 2` (`fldHpvofpyDNf8sb4`) AI auto-mirror field

**File system:**
- `SKILL.md` is restored from `SKILL.md.bak`, then the mapping table rows for Engineer,
  Build Time, Industry, and Result 2 are patched to reference the new field IDs.
  Nothing else in `SKILL.md` is changed.
- `update_skill.py` (obsolete, from a prior run) is deleted.

## Safety

- **`--dry-run`** prints every intended change (API calls + diff) without any write.
- All field creations are **idempotent** — re-running skips fields that already exist.
- No renames, no deletes, no reconfigures of existing Airtable fields.
- SKILL.md always re-restores from the backup before patching, so repeat runs converge.

## Prerequisites

- Python 3.9+ (stdlib only, no `pip` deps)
- `AIRTABLE_PAT` env var — an Airtable Personal Access Token scoped to:
  - `schema.bases:read` and `schema.bases:write` on base `app8V74T72TT2SB0h`
  - (data scopes not required for this script)

## Usage

```bash
cd ~/.claude/skills/micro-case-study

# Preview — no writes
AIRTABLE_PAT=patXXXX.XXXX python update_mcs_fields.py --dry-run

# Apply
AIRTABLE_PAT=patXXXX.XXXX python update_mcs_fields.py

# SKILL.md / file changes only, skip Airtable API (for offline testing)
python update_mcs_fields.py --skip-api --dry-run
python update_mcs_fields.py --skip-api
```

## Verification (the script prints this checklist on completion)

1. `describe_table` on the MCS table → 4 new fields present with expected types/options.
2. `diff SKILL.md SKILL.md.bak` → only the mapping-table region changed.
3. Re-run the script → every step reports `no-op`.
4. Grep `SKILL.md` for `flduLY0o5WsNiX1eL` (Zoom Transcript 1) and `appMjlaeg7cFYivss`
   (CRM Enriched Debriefs base) → still present, transcript-mining workflow intact.
5. Existing `Industry` (`fldoOn2odwxB0PEfG`) and `Result 2` (`fldHpvofpyDNf8sb4`)
   still exist with original types.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 2 | `AIRTABLE_PAT` missing (and `--skip-api` not passed) |
| 3 | `SKILL.md.bak` missing — cannot restore |
