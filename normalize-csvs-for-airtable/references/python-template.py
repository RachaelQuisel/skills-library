#!/usr/bin/env python3
"""
CSV-to-Airtable normalizer template.

WHAT THIS IS
------------
A canonical pattern for taking N source CSVs (typically multi-year historical
spreadsheets from a client) and producing a single import-ready CSV for
Airtable. Copy this file into the client's work folder, edit the FILES list
and the field mapping, run it.

WHAT IT DOES
------------
- Reads each source CSV using a per-file config (handles schema drift)
- Emits ONE row per logical event into a unified output
- Auto-corrects only unambiguous typos (double slashes, 2-digit years)
- Flags everything else for client review WITHIN THE SAME CSV (Status column)
- Logs every auto-correction in a separate changes.csv for audit

DESIGN RULES (do not break these without asking the user)
---------------------------------------------------------
1. ONE output CSV with all rows + a Status column. NOT two split files.
2. Preserve name fields verbatim. No .strip(), no .title(), no encoding repair.
3. Auto-correct ONLY unambiguous patterns. Flag everything ambiguous.
4. Tracking ID = Source File + Source Row + Sub-key. Stable across re-runs.
5. Do not fuzzy-match to Airtable records in Python. Use Airtable's built-in
   text-to-linked-record conversion after import.
6. Do not dedupe automatically. Flag duplicates and let a human decide.

USAGE
-----
1. Copy this file to <client folder>/normalize.py
2. Edit SOURCE_DIR and OUT_DIR (or rely on the default __file__-relative paths)
3. Edit FILES below to describe each source CSV's layout
4. Edit the sub_records() function if the event structure differs from
   "many sub-events per source row" (the default pattern)
5. Run: python3 normalize.py
6. Outputs land in ./outputs/ with today's date stamped in the filename

WIDE vs LONG FORMAT
-------------------
This template produces LONG format: one output row per sub-event (e.g., one
trainee with 4 modules emits 4 rows). Long format is best for relational
analytics and linked-record import to Airtable.

For WIDE format (one row per source row, all sub-events as side-by-side
columns like `Module 1 Date`, `Module 1 Trainer`, `Module 2 Date`, ...),
the structure is different — see the EA training tracker as a worked
example: `~/Claude-Work/CLIENTS/Guardians_of_Love_Jessica_Peoples/
Exports/training-tracker-migration/normalize_training_trackers.py`.

Wide format is right when the destination Airtable table should mirror
the source spreadsheet shape (so the client recognizes it). Long format
is right when you want relational reporting. Ask the user before assuming.
"""

import csv
import re
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

# =========================================================================
# PATHS - edit if needed
# =========================================================================
ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "source-csvs"       # put your source CSVs here
OUT_DIR = ROOT / "outputs"
OUT_DIR.mkdir(exist_ok=True)

TODAY = date.today().isoformat()
ALL_EVENTS_PATH = OUT_DIR / f"{TODAY}_all_events.csv"
CHANGES_PATH = OUT_DIR / f"{TODAY}_changes.csv"

# =========================================================================
# PER-FILE CONFIGS - edit this list for each client
# =========================================================================
# Each file gets a config describing its layout. Column indices are 0-based
# positions AFTER dropping the leading row-id column (if present).
#
# `sub_records_template` describes how each source row expands into N output
# rows. For a training tracker where each row has multiple modules, you'd
# list each module's date and trainer column positions. For a single-event
# file, use one entry per row.
#
# Replace this example with your actual file shapes.

FILES = [
    # {
    #     "name": "Example Tracker 2020-2022",
    #     "filename": "example-tracker-2020-2022.csv",
    #     "skip_rows": 1,                  # how many header rows to skip
    #     "has_leading_id_col": True,      # drop column A if it's a row-id col
    #     "valid_year_range": (2017, date.today().year + 5),
    #     # one entry per sub-event the row encodes; each entry tells the
    #     # normalizer which columns hold that sub-event's data
    #     "sub_records": [
    #         {"code": "M1",  "label": "Module 1",        "date_col": 2,  "trainer_col": 3},
    #         {"code": "M2",  "label": "Module 2",        "date_col": 4,  "trainer_col": 5},
    #         {"code": "CPR", "label": "CPR/First Aid",   "date_col": 6,  "trainer_col": 7},
    #     ],
    #     "person_last_name_col": 0,
    #     "person_first_name_col": 1,
    #     "agency_col": 8,
    #     "phase": "pre-approval",         # any tag you want carried through
    # },
]

# =========================================================================
# LOOKUP NORMALIZATION
# =========================================================================
# Values you EXPECT to see in lookup-style columns (Agency, Trainer, etc.).
# Anything not in these sets gets flagged for review WITH the raw value
# preserved. Edit per client.

EXPECTED_AGENCIES = {"EA", "PARTNER"}     # example - edit per client

# Lookup values that are not people / not lookups at all - special handling
NON_PERSON_TRAINERS = {"outside", "online"}

# Explicit date-typo repair table. Add patterns ONLY where there's a single
# plausible interpretation (after considering all possible digit insertions/
# removals within the program's valid year range). Anything ambiguous stays
# flagged. Each repair is logged to changes.csv with before/after.
#
# Examples from the EA training tracker migration:
#   "12/20/219": "12/20/2019",   # 3-digit year, only valid expansion
#   "4/30/2036": "4/30/2026",    # off by one decade
#   "3/31/3023": "3/31/2023",    # off by 1000
#   "5/20/82020": "5/20/2020",   # extra leading digit in 5-digit year
#   "11/102018": "11/10/2018",   # missing slash in M/DDYYYY
#   "10/.30/2020": "10/30/2020", # stray punctuation
DATE_REPAIRS = {
    # Add per-client repairs here after running the script and reviewing
    # the unique unparseable/out-of-range strings in review rows.
}


# =========================================================================
# PARSE HELPERS - rarely need editing
# =========================================================================

def parse_date(raw, valid_year_range):
    """
    Returns (iso_date_or_None, change_record_or_None, flag_or_None).

    Auto-corrects ONLY:
      - Double slashes (e.g., '2//24/26' -> '2/24/26')
      - 2-digit years (e.g., '26' -> '2026')
      - Whitespace

    Flags (does not correct):
      - Out-of-range years
      - Unparseable strings (gibberish, Excel serials, names in date cells)
    """
    if raw is None:
        return None, None, None
    original = raw
    cleaned = raw.strip()
    if cleaned == "":
        return None, None, None

    change = None

    # Apply explicit typo-repair table first (single-plausible-interpretation only).
    if cleaned in DATE_REPAIRS:
        repaired = DATE_REPAIRS[cleaned]
        change = ("known typo repaired", cleaned, repaired)
        cleaned = repaired

    if "//" in cleaned:
        fixed = re.sub(r"/+", "/", cleaned)
        change = ("double-slash collapsed", cleaned, fixed)
        cleaned = fixed

    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{2,4})$", cleaned)
    if not m:
        return None, change, f"date unparseable: {original!r}"

    mo, dy, yr = m.group(1), m.group(2), m.group(3)

    if len(yr) == 2:
        yr_int = int(yr)
        # Python convention: 00-69 -> 2000s, 70-99 -> 1900s
        expanded = 2000 + yr_int if yr_int <= 69 else 1900 + yr_int
        new_change = ("2-digit year expanded", f"{mo}/{dy}/{yr}", f"{mo}/{dy}/{expanded}")
        if change:
            change = (
                f"{change[0]} + {new_change[0]}",
                original,
                f"{mo}/{dy}/{expanded}",
            )
        else:
            change = (new_change[0], original, f"{mo}/{dy}/{expanded}")
        yr = str(expanded)

    try:
        d = datetime(int(yr), int(mo), int(dy)).date()
    except ValueError:
        return None, change, f"date invalid calendar value: {original!r}"

    lo, hi = valid_year_range
    if d.year < lo or d.year > hi:
        return None, change, f"date out of expected range ({d.isoformat()}): {original!r}"

    return d.isoformat(), change, None


def preserve_lookup_value(raw, expected_set=None, non_person_set=None):
    """
    Returns (raw_preserved, value_for_match, flag_or_None).

    DOES NOT modify the value. Returns the trimmed value for case-insensitive
    comparison against `expected_set`, but the raw is preserved as-typed for
    audit (case variants like 'oswaldo' vs 'Oswaldo' carry signal about
    data-entry inconsistencies).

    Optionally flags values not in `expected_set` (case-insensitive).
    Optionally flags values that are 'modes' not people (e.g., 'Outside').
    """
    if raw is None:
        return None, None, None
    raw_preserved = raw
    cleaned = raw.strip()
    if cleaned == "":
        return raw_preserved, None, None

    if non_person_set and cleaned.lower() in non_person_set:
        return raw_preserved, cleaned, f"lookup is delivery mode, not a person: {cleaned!r}"

    if expected_set is not None and cleaned.upper() not in {v.upper() for v in expected_set}:
        return raw_preserved, cleaned, f"lookup value not in expected set: {cleaned!r}"

    return raw_preserved, cleaned, None


def is_blank_row(cells):
    return all((c is None or str(c).strip() == "") for c in cells)


# =========================================================================
# MAIN
# =========================================================================

def main():
    if not FILES:
        sys.exit(
            "FILES is empty. Edit the FILES list at the top of this script "
            "to describe each source CSV's layout."
        )
    if not SOURCE_DIR.exists():
        sys.exit(f"Source dir not found: {SOURCE_DIR}")

    all_rows = []
    changes_rows = []

    # Define the output schema. Adjust field names for the client's domain
    # but keep the meta columns (Tracking ID, Source File, Source Row, Status,
    # Review Reason) - they enable the Airtable conversion + audit story.
    output_fields = [
        "Tracking ID",
        "Source File",
        "Source Row",
        "Phase",
        "Sub-Record Code",
        "Sub-Record Label",
        "Person Last Name (raw)",
        "Person First Name (raw)",
        "Agency (raw)",
        "Agency (normalized)",
        "Trainer (raw)",
        "Trainer (normalized)",
        "Date",
        "Status",          # 'ready' or 'needs client review'
        "Review Reason",   # human-readable reasons, joined with '; '
    ]

    changes_fields = [
        "Source File", "Source Row", "Sub-Record Code", "Field",
        "Change Type", "Before", "After",
    ]

    for cfg in FILES:
        path = SOURCE_DIR / cfg["filename"]
        if not path.exists():
            print(f"  SKIP (file not found): {path.name}")
            continue
        print(f"Processing: {cfg['name']}")

        with open(path, newline="", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            rows = list(reader)

        data_rows = rows[cfg["skip_rows"]:]
        valid_year_range = cfg.get("valid_year_range", (2010, date.today().year + 5))

        for source_row_num, raw_cells in enumerate(data_rows, start=cfg["skip_rows"] + 1):
            if is_blank_row(raw_cells):
                continue

            cells = raw_cells[1:] if cfg["has_leading_id_col"] else raw_cells
            if is_blank_row(cells):
                continue

            last_name = cells[cfg["person_last_name_col"]] if len(cells) > cfg["person_last_name_col"] else ""
            first_name = cells[cfg["person_first_name_col"]] if len(cells) > cfg["person_first_name_col"] else ""
            agency_raw = cells[cfg["agency_col"]] if len(cells) > cfg["agency_col"] else None

            if not (last_name or "").strip() and not (first_name or "").strip():
                continue

            agency_raw_v, agency_norm, agency_flag = preserve_lookup_value(
                agency_raw, expected_set=EXPECTED_AGENCIES
            )

            for sub in cfg["sub_records"]:
                date_raw = cells[sub["date_col"]] if len(cells) > sub["date_col"] else None
                trainer_raw = cells[sub["trainer_col"]] if len(cells) > sub["trainer_col"] else None

                # Skip sub-events with nothing recorded
                if not (date_raw or "").strip() and not (trainer_raw or "").strip():
                    continue

                iso_date, date_change, date_flag = parse_date(date_raw, valid_year_range)
                trainer_raw_v, trainer_norm, trainer_flag = preserve_lookup_value(
                    trainer_raw, non_person_set=NON_PERSON_TRAINERS
                )

                if date_change:
                    changes_rows.append({
                        "Source File": cfg["name"],
                        "Source Row": source_row_num,
                        "Sub-Record Code": sub["code"],
                        "Field": "Date",
                        "Change Type": date_change[0],
                        "Before": date_change[1],
                        "After": date_change[2],
                    })

                flags = [f for f in (date_flag, trainer_flag, agency_flag) if f]
                status = "needs client review" if flags else "ready"

                all_rows.append({
                    "Tracking ID": f"{cfg['name']} R{source_row_num} {sub['code']}",
                    "Source File": cfg["name"],
                    "Source Row": source_row_num,
                    "Phase": cfg.get("phase", ""),
                    "Sub-Record Code": sub["code"],
                    "Sub-Record Label": sub["label"],
                    "Person Last Name (raw)": last_name,
                    "Person First Name (raw)": first_name,
                    "Agency (raw)": agency_raw_v,
                    "Agency (normalized)": agency_norm,
                    "Trainer (raw)": trainer_raw_v,
                    "Trainer (normalized)": trainer_norm,
                    "Date": iso_date or "",
                    "Status": status,
                    "Review Reason": "; ".join(flags),
                })

    # =====================================================================
    # WRITE OUTPUTS
    # =====================================================================
    with open(ALL_EVENTS_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=output_fields)
        w.writeheader()
        w.writerows(all_rows)

    with open(CHANGES_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=changes_fields)
        w.writeheader()
        w.writerows(changes_rows)

    # =====================================================================
    # POST-RUN ANALYSIS - printed to stdout, also written next to outputs
    # =====================================================================
    status_counts = Counter(r["Status"] for r in all_rows)
    review_reasons = Counter(r["Review Reason"] for r in all_rows if r["Review Reason"])
    by_source = Counter(r["Source File"] for r in all_rows)
    by_year = Counter(r["Date"][:4] for r in all_rows if r["Date"])
    by_agency = Counter((r["Agency (normalized)"] or "(blank)") for r in all_rows)

    summary_lines = []
    summary_lines.append("=" * 60)
    summary_lines.append(f"Outputs in: {OUT_DIR}")
    summary_lines.append(f"  All events:      {ALL_EVENTS_PATH.name}")
    summary_lines.append(f"  Changes audit:   {CHANGES_PATH.name}")
    summary_lines.append("")
    summary_lines.append(f"Total rows:        {len(all_rows):,}")
    for status, count in status_counts.most_common():
        summary_lines.append(f"  {status}: {count:,}")
    summary_lines.append(f"Auto-corrections:  {len(changes_rows):,}")
    summary_lines.append("")
    summary_lines.append("Rows by source:")
    for src, count in by_source.most_common():
        summary_lines.append(f"  {src}: {count:,}")
    summary_lines.append("")
    summary_lines.append("Rows by year:")
    for yr in sorted(by_year.keys()):
        summary_lines.append(f"  {yr}: {by_year[yr]:,}")
    summary_lines.append("")
    summary_lines.append("Agency distribution:")
    for ag, count in by_agency.most_common(15):
        summary_lines.append(f"  {ag!r}: {count:,}")
    summary_lines.append("")
    summary_lines.append("Top review reasons:")
    for reason, count in review_reasons.most_common(10):
        summary_lines.append(f"  ({count:>3}) {reason}")
    summary_lines.append("=" * 60)

    summary = "\n".join(summary_lines)
    print(summary)
    (OUT_DIR / f"{TODAY}_post_run_summary.txt").write_text(summary)


if __name__ == "__main__":
    main()
