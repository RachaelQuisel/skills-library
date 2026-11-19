# eval_helper.py

Companion utility for the `workflow-eval` skill. Three subcommands, all stdlib-only.

## Setup

```bash
export AIRTABLE_PAT=<your-pat>
```

The PAT needs read access to the bases you'll snapshot. Required for `snapshot`; not needed for `diff` or `render`.

## snapshot: pull Airtable record state into JSON

```bash
python eval_helper.py snapshot \
  --base appXXX \
  --tables tblA,tblB,tblC \
  --out workflow_eval/<workflow-name>/runs/<case>/before.json
```

Optional `--since <ISO timestamp>` narrows to records modified after that time, useful when a table is large and you only care about post-trigger activity:

```bash
python eval_helper.py snapshot \
  --base appXXX --tables tblA \
  --since 2026-06-06T14:00:00Z \
  --out .../after.json
```

> **Use the same identifier form (table IDs or table names) for both BEFORE and AFTER snapshots.** The diff subcommand keys tables by whatever string you passed; mixing IDs and names will make diff treat them as different tables and report 100% added/deleted.

The output JSON has shape:
```json
{
  "captured_at": "2026-06-06T14:32:00Z",
  "base": "appXXX",
  "since": null,
  "tables": {
    "tblA": {
      "record_count": 27,
      "records": [ { "id": "rec...", "fields": {...}, "createdTime": "..." }, ... ]
    }
  }
}
```

## diff: diff two snapshots

```bash
python eval_helper.py diff \
  --before .../before.json \
  --after .../after.json \
  --out .../diff.json
```

Output structure (per table):
```json
{
  "tables": {
    "tblA": {
      "added":   [ {full record}, ... ],
      "updated": [ { "id": "rec...", "changes": { "fldX": {"before": ..., "after": ...} } } ],
      "deleted": [ {full record}, ... ],
      "summary": { "added": 3, "updated": 1, "deleted": 0 }
    }
  }
}
```

A summary line per table is also printed to stderr.

## render: render a result JSON into a Markdown post-run analysis

```bash
python eval_helper.py render \
  --result workflow_eval/<workflow-name>/runs/result.json \
  --out workflow_eval/<workflow-name>/POST_RUN_ANALYSIS_2026-06-06.md
```

The `result.json` structure is documented in `../references/post-run-template.md`. You (or Claude, on your behalf) write this file by hand after evaluating each case against its diff.

## Exit codes

- `0` - success
- `1` - argparse/CLI usage error
- non-zero with `ERROR:` to stderr, missing env var, Airtable HTTP error, malformed JSON

## What this helper does NOT do

- Does not trigger any workflow / automation / Zap. Per the parent skill's deliberate scope boundary, see `../SKILL.md`.
- Does not write to Airtable. Read-only.
- Does not call any LLM. All eval reasoning happens in Claude, then gets serialized into `result.json` for rendering.
- Does not handle Zapier task history, QuickBooks state, or webhook logs. Those evidence sources are file-based, you collect the exports and drop them in `runs/<case>/notes.md` or as JSON Claude can Read.
