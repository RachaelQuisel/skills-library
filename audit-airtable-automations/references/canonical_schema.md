# Canonical Automation Inventory schema

Default schema for the `Automation Inventory` + `Automation Logs` pattern. Used when the
audit skill creates these tables in a fresh base. When the base already has tables that
look like an inventory, the skill adopts the existing schema instead of imposing this
one.

This schema is designed for any Airtable base — pair an inventory catalog (one row per
automation) with a runtime logs table (one row per run), linked, so each automation's
last-run / total-runs / failure-count are visible at a glance.

## `Automation Inventory` table

One row per automation in the base.

| Field | Type | Notes |
|---|---|---|
| Automation Name | single line text (primary) | e.g., "Applicant created → Create training tracker" |
| Trigger Type | single select | Choices: Record matches conditions, Record updated, Record created, Scheduled, View entry, Form submission, Webhook, External |
| What It Does | long text | Plain-language description of the behavior |
| Source Table | single line text | The table whose records trigger this automation |
| Group | single select | Choices: A - Has script action, B - No script action, Sweep, External, Webhook |
| Fields Written | long text | Fields this automation writes to (or records it creates) |
| Status | single select | Choices: Live, Built not deployed, Disabled, Off |
| Source File | single line text | Path to script file, or "(Airtable UI only)" / "(Zapier zap)" / "(Apps Script)" |
| Deployed | checkbox | |
| Logger Added | checkbox | Whether this automation writes a row to Automation Logs on each run |
| Automation Logs | multipleRecordLinks → Automation Logs | Inverse link for runtime data |
| Last Run | single line text (placeholder) | Description: "Convert to ROLLUP of Automation Logs > Logged At with MAX aggregation" |
| Total Runs | single line text (placeholder) | Description: "Convert to COUNT of linked Automation Logs (no filter)" |
| Last Outcome | single line text | Logger-stamped (not a rollup — rollups can't return latest value) |
| Failed Runs | single line text (placeholder) | Description: "Convert to COUNT of Automation Logs where Outcome = Failed" |
| Skipped Runs | single line text (placeholder) | Description: "Convert to COUNT of Automation Logs where Outcome = Skipped" |
| Last Note | single line text | Logger-stamped — most recent run's notes |
| Trigger Condition | long text | Watched fields / filter formula that fires this automation |
| Owner | single line text | Who owns / maintains this automation |
| Last Updated | date (US format M/D/YYYY) | When the automation definition was last changed |
| Dependencies | long text | Other automations, fields, or systems this one depends on |
| Pain Points Addressed | single line text | The documented pain point this automation resolves |
| Deliverable | single line text | The client-facing deliverable this automation is part of |
| Notes | rich text | Free-form notes |

**Why some fields are placeholders:** Airtable's public API can't create rollup/count
fields directly (see `feedback_airtable_api_no_lookup_rollup_create.md`), so Last Run,
Total Runs, Failed Runs, and Skipped Runs are created as `singleLineText` with
conversion instructions in their descriptions. The Omni prompt sequence's Prompt 1c
asks Omni to do the conversion in a follow-up step.

## `Automation Logs` table

Runtime activity that Inventory links into. Each `Logger Added` automation writes one
row here per run.

| Field | Type | Notes |
|---|---|---|
| Log ID | single line text (primary) | e.g., "{Automation Name} {timestamp}" |
| Automation | multipleRecordLinks → Automation Inventory | The catalog entry that ran |
| Logged At | dateTime | When the run completed |
| Outcome | single select | Choices: Success, Failed, Skipped, Partial |
| Notes | long text | First-person message from the run (what happened) |
| Affected Record IDs | long text | Comma-separated rec IDs the run touched (if any) |
| Duration ms | number | Run duration in milliseconds (if measured) |
| Error | long text | Stack trace or error message if Outcome = Failed |
