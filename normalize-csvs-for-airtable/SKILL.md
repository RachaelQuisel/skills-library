---
name: normalize-csvs-for-airtable
version: 1.0.3
description: Normalize messy multi-year/multi-file CSVs into one import-ready CSV for Airtable. Use when the user shares historical spreadsheets (training trackers, attendance logs, applicant intake files, etc.) that need to land in an existing Airtable base, and the data has schema drift across years, inconsistent formatting, or unknown lookup values. Triggers on phrases like "normalize these CSVs", "migrate this spreadsheet to Airtable", "import historical data", "build a normalizer", "multi-year files", "CSV to Airtable", "data audit migration", "wide format", "mirror the source spreadsheet".
tags:
  - skill
---

# Normalize CSVs for Airtable

## Purpose in plain English

This skill helps you combine inconsistent spreadsheet exports into a clean file ready for Airtable import.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


A workflow for taking N source CSVs (typically multi-year historical spreadsheets from a client) and producing one import-ready CSV plus a client-facing assessment document — without over-engineering.

## When to use

- Client gives you 2+ CSVs covering historical data that needs to land in Airtable
- Files have schema drift (different columns, headers, layouts across years)
- Data quality is mixed — typos, inconsistent agency/trainer names, encoding issues
- The destination Airtable base has existing tables that should be linked to

## Anti-patterns — do NOT do these

These are over-engineering traps. Skip them unless the user explicitly asks.

- **Don't fuzzy-match in Python** to existing Airtable records. Import as text, then use Airtable's "convert field to linked record" feature, which auto-matches by name.
- **Don't split outputs into normalized.csv + review.csv.** One CSV with a `Status` column (`ready` / `needs client review`) is simpler for the client to consume.
- **Don't touch names** (`.strip()`, `.title()`, encoding repair, compound-surname splitting) unless the user explicitly says so. Preserve verbatim. This applies to trainer/lookup values too — case variants (`emerson` vs `Emerson`) carry signal about data-entry inconsistencies.
- **Don't add Excel serial date conversion**, fancy regex, or speculative validators unless the data has many such cases.
- **Don't dedupe automatically.** Flag duplicates; let a human decide.
- **Don't add tests**, type hints, or argparse for one-off migration scripts. They're write-once.
- **Don't restructure the client's normalizer** without first writing/showing the template pattern you plan to apply.
- **Don't claim "no data lost" without verifying the Airtable import step.** "Nothing was deleted" applies only to the normalizer pipeline (source → CSV). Airtable imports can drop data via column-mapping mistakes or field-type conversions. After import, always recommend: (a) confirm total record count matches the CSV, (b) spot-check 10 random rows for full field population.
- **Don't re-import the whole file if Airtable dropped data.** Build a targeted update CSV with just `Tracking ID + the missing columns` and use Airtable's "Update existing records, match on Tracking ID" import. Re-importing the whole file risks creating duplicates.

## Workflow (8 steps)

### Step 1 — Inventory source files
- `ls` the directory the user pointed to. Confirm file names and sizes.
- Read the first 5 rows + the last 5 rows of each file. Count lines.
- Note schema differences across files: leading row-id columns, header typos, title rows, column counts.

### Step 2 — Inventory the live Airtable base
- Use `mcp__airtable__list_tables_for_base` to see existing tables.
- Identify which tables the new data should LINK to (people, lookup libraries, etc.). Don't propose new fields that duplicate existing tables.
- See `~/.claude/projects/-Users-rachaelquisel/memory/feedback_inventory_live_schema_first.md` for the rationale.

### Step 3 — Draft target schema using the prompt skeleton
- Open `references/target-schema-prompt-skeleton.md`.
- Fill it in with the columns, types, and select options needed.
- **Decide wide format vs long format — this is a real choice, not a default.**
  - **Wide format** = one row per parent entity (e.g., one row per trainee), with all sub-events as side-by-side columns (`Module 1 Date`, `Module 1 Trainer`, `Module 2 Date`, ...). **Use when:** the client reads the source spreadsheet day-to-day and recognizes its shape; the data is going into Airtable as a flat reference table; relational reporting isn't required.
  - **Long format** = one row per sub-event (e.g., one row per module completion). **Use when:** the destination is a relational design with linked records to library tables; analytics queries are the primary use case ("how many trainings did Emerson run in Q1?"); the source has many sub-events per row that vary widely.
  - **Default:** ask the user which they prefer. Don't assume long. The EA migration started long, then pivoted to wide because the client recognized the source-spreadsheet shape — that pivot is expensive to do mid-script, so confirm upfront.

### Step 4 — Confirm schema with the user before writing code
- Show the filled-in schema + disambiguation rules.
- Ask 1-2 questions max — don't ladder. The questions you actually need:
  - "Are these the right lookup values [list], or are there more?"
  - "Should X column be linked or text?"
- Once approved, proceed.

### Step 5 — Write the Python normalizer
- Copy `references/python-template.py` to `<client folder>/Exports/<task>-migration/normalize.py`.
- Edit the `FILES` list to describe each source CSV.
- Edit `EXPECTED_AGENCIES` (or the equivalent lookup set) to declare known values.
- Run it. Verify the summary numbers look right (row counts make sense, status split makes sense).

### Step 6 — Write a README colocated with the script
- One-page README at `<client folder>/Exports/<task>-migration/README.md`.
- What the script does, how to run, what the outputs are, what's IN scope vs out.
- See `feedback_readme_per_script.md`.

### Step 7 — Post-run analysis
- The script already prints + saves a summary file. Walk the user through:
  - Total events extracted
  - Status split (ready vs needs review)
  - Top review reasons
  - Year distribution (any anomalies?)
  - Lookup-value distribution (any surprises like agencies you didn't know existed?)
  - Top trainers / lookup values (for sanity check on the linked-table population)
- Surface SURPRISES, not expected counts. The user already knows the data is multi-year.

### Step 8 — Client-facing post-migration assessment
- Write a `<task>-assessment-YYYY-MM-DD.md` doc colocated with the script.
- This is what the user hands to their client. Different from internal docs.
- Structure:
  - **Summary**: total events, % ready, % flagged
  - **Files audited**: list with row counts and date ranges
  - **Decisions I made and why**: each normalization rule (auto-correct vs flag), the rationale, what data shape was chosen (long vs wide), how lookup values are being handled
  - **Surprises in the data**: things the client might not know (e.g., agency column had 13 distinct values not 2)
  - **Decisions still needed from the client**: numbered, specific questions
  - **Next steps**: what happens after client approves
- Use "normalize/normalization" not "clean/cleaning" — see `feedback_normalize_not_clean.md`.

### Step 9 — Verify the Airtable import wasn't lossy

**This step is non-optional.** Airtable imports can drop data via column-mapping mistakes or field-type conversions. The normalizer producing a clean CSV is necessary but not sufficient.

After the user imports the CSV into Airtable:

1. **Confirm total record count** in the Airtable table = expected row count from `post_run_summary.txt`. Mismatch = data loss; investigate before proceeding.
2. **Spot-check 10 random rows**: pick 10 Tracking IDs, find them in both the source CSV and Airtable, confirm every field landed where expected.
3. **Confirm name fields populated**: filter Airtable for `Last Name = blank` and verify the count matches the count in the CSV (not lower). If lower, names were dropped during import — investigate the column mapping.
4. **If data is missing in Airtable**: do NOT re-import the whole file (creates duplicates). Build a targeted update CSV with just `Tracking ID + missing columns` and use Airtable's "Update existing records, match on Tracking ID" import.

Never tell the user "the migration is complete" without doing steps 1-3.

## Output contract

The script always produces:

- `outputs/YYYY-MM-DD_all_events.csv` — every row from every source file, in one CSV, with these columns at minimum:
  - `Tracking ID` — `{Source File} R{Source Row} {Sub-Record Code}` for stable re-runs
  - `Source File` and `Source Row` — provenance
  - All the domain fields (raw + normalized side-by-side for lookups)
  - `Status` — `ready` or `needs client review`
  - `Review Reason` — semicolon-joined reasons (blank for ready rows)
- `outputs/YYYY-MM-DD_changes.csv` — every auto-correction logged with before/after
- `outputs/YYYY-MM-DD_post_run_summary.txt` — the numbers/distributions printed at run time

This contract means the client can import the all_events.csv into Airtable, filter on `Status = "ready"`, and import. The flagged rows wait in the same file with a flag.

## Principles

- **Get it in Airtable. Fix in Airtable, not in Python.** Most "issues" are faster to resolve once the data is in Airtable's UI than to engineer in code.
- **Preserve raw values alongside normalized ones.** Never replace a raw value silently.
- **Auto-correct only unambiguous typos.** Double slashes and 2-digit years are safe. Anything else needs human eyes.
- **Tracking ID stability**. Re-running the normalizer on a corrected source should produce the same Tracking IDs.
- **Don't model relational links in Python.** Airtable's text-to-linked-record conversion handles this once the table exists with the right reference data.

## Related memories to check

- `feedback_inventory_live_schema_first.md` — always read the live base before designing schema
- `project_gol_libraries_and_links.md` — for EA specifically, default to linked records to existing library tables
- `feedback_no_cross_table_links.md` — general rule: don't create cross-table links unless asked
- `feedback_normalize_not_clean.md` — client-facing vocabulary
- `feedback_readme_per_script.md` — README is co-located with the script, not an index
- `feedback_csv_over_direct_writes.md` — prefer CSV export → edit → re-import over direct API writes
- `feedback_match_miss_over_miscategorize.md` — leave blank rather than guess

## Reference files in this skill

- `references/python-template.py` — copy this into the client folder and edit
- `references/target-schema-prompt-skeleton.md` — fill in for each migration
- `references/disambiguation-rules.md` — auto-correct vs flag policy with rationale
