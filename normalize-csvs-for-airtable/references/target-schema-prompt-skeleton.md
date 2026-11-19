# Target Schema Prompt Skeleton

Fill this in before writing any Python. Show it to the user and get confirmation.

```
TARGET TABLE: <table name>

ONE ROW PER: <what each row represents — e.g. "one training completion",
              "one applicant", "one invoice line">

COLUMNS (exact names, types, and options):

  Meta columns (always include these for migration traceability):
    - Tracking ID:       Formula  (source-file + source-row + sub-key)
    - Source File:       Text     (which CSV this came from)
    - Source Row:        Number   (1-indexed row in that source CSV)
    - Status:            Single select  (Options: 'ready', 'needs client review')
    - Review Reason:     Long text  (blank for ready rows)

  Domain columns (edit per client):
    - <Field Name>:     <Type>  (Options if select: ..., ...)
    - <Field Name>:     <Type>
    - ...

  Raw + Normalized pairs (for any lookup-style field that may get linked to
  another table after import):
    - <Field> (raw):         Text  — preserved verbatim
    - <Field> (normalized):  Text  — strip + title-cased, used for matching

SOURCE FILES:
  - <path-1>  — describe the shape (header rows, leading id col, etc.)
  - <path-2>
  - ...

  Schema differences across files: <list them>

DISAMBIGUATION RULES (see references/disambiguation-rules.md for canon):

  Auto-correct (log to changes.csv):
    - Double-slash in date strings → single slash
    - 2-digit years → 4-digit
    - [client-specific additions go here]

  Flag for review (set Status='needs client review', do NOT modify the value):
    - Out-of-range dates
    - Unparseable dates
    - Lookup values not in the expected set
    - Apparent in-file duplicates
    - [client-specific additions]

  Preserve verbatim (do not touch):
    - All name fields
    - [anything else the user said to preserve]

PROCESS:
  1. Show me 10 sample normalized rows + the changes.csv + the top review
     reasons before doing the full run.
  2. Confirm the rules behaved as expected.
  3. Run full normalization.
  4. Write the client-facing assessment document.
  5. Hand off the all_events.csv for Airtable import.
```

## Filled-in example (GoL Training Tracker, 2026-05-22)

For reference, this is what the skeleton looked like when filled in for the
Guardians of Love training tracker migration:

```
TARGET TABLE: Training Completion (in appp6pbBbaxuOLu2v)

ONE ROW PER: one training event (a specific module completed by one trainee
             on one date with one trainer)

COLUMNS:
  Meta:
    - Tracking ID:     Formula   ({Source File} & " R" & {Source Row} & " " & {Sub-Record Code})
    - Source File:     Text
    - Source Row:      Number
    - Status:          Single select ('ready', 'needs client review')
    - Review Reason:   Long text

  Domain:
    - Phase:                  Single select ('pre-approval', 'post-approval')
    - Module Code:            Text  (M1, M2, M3, M4, CPR, M5, M6)
    - Module Label:           Text
    - Date:                   Date  (YYYY-MM-DD)

  Raw + Normalized pairs (linked-record targets after import):
    - Trainee Last Name (raw):    Text
    - Trainee First Name (raw):   Text
    - Agency (raw):               Text
    - Agency (normalized):        Text     → links to Organization
    - Trainer (raw):              Text
    - Trainer (normalized):       Text     → links to Contact

SOURCE FILES: 5 CSVs from SharePoint, 2017-2028 (pre-approval) + 2018-2026 (post-approval)
  Differences: 2023-2025 has no leading row-id col; 2017-2022 use 'Trianer' typo
  in M2 header; post-approval has a title row above headers; column layouts
  otherwise consistent within phase.

DISAMBIGUATION RULES:
  Auto-correct:
    - Double-slash in dates
    - 2-digit years → 4-digit

  Flag for review:
    - Out-of-range dates (< 2010 or > today+5)
    - Unparseable dates (gibberish, names typed in date cells, Excel serials)
    - Agency values not in {GOL, DIUP}
    - Trainer = 'Outside' or 'Online' (these are delivery modes, not people)

  Preserve verbatim:
    - All trainee names (no .strip, no encoding repair, no compound-surname splitting)

PROCESS: (followed exactly as written above)
```
