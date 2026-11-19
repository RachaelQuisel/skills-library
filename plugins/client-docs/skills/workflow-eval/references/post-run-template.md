# Post-run analysis: report structure + result.json schema

The post-run analysis is the deliverable. Two equivalent ways to produce it:

1. Write `runs/result.json` (schema below), then run `eval_helper.py render` to produce the Markdown.
2. Write the Markdown directly. Fine for 1-2 cases; the renderer keeps formatting consistent across many cases.

## `result.json` schema

```json
{
  "workflow": "aymg-qb-push-v17",
  "run_date": "2026-06-06",
  "inventory_notes": "audit-airtable-automations ran on 2026-06-05; v17 script read from local; Zapier task history exported manually for case 01 only.",
  "cases": [
    {
      "name": "01-uams-happy-path",
      "description": "UAMS contract; v17 walks Advertiser link, finds customer, pushes invoice.",
      "verdict": "PASS",
      "expected_outcomes": [
        "fldLastQbPush contains SUCCESS on recQWdfjq9ILIY5XO",
        "fldQbTransactionId present on recQWdfjq9ILIY5XO",
        "New Invoice in QBO sandbox matching contract amount"
      ],
      "actual_outcomes": [
        "fldLastQbPush = 'SUCCESS - pushed at 2026-06-06T14:32Z' on recQWdfjq9ILIY5XO",
        "fldQbTransactionId = '1042' on recQWdfjq9ILIY5XO",
        "Invoice 1042 created in QBO sandbox, total $4,500.00"
      ],
      "diff": { "<paste the relevant diff.json content here, or omit>" },
      "notes": "Ran twice for idempotency cross-check; second run was a no-op."
    },
    {
      "name": "02-no-advertiser-link",
      "description": "Contract with empty Advertiser; v17 should throw guard.",
      "verdict": "PASS",
      "expected_outcomes": [
        "fldQbTransactionId absent",
        "Error message contains 'Advertiser is not linked'"
      ],
      "actual_outcomes": [
        "fldQbTransactionId absent",
        "Automation run errored with 'Advertiser is not linked on this Contract'"
      ],
      "notes": "Friendly error rendered to fldLastQbPush as expected."
    },
    {
      "name": "03-item-ref-202",
      "description": "Contract whose Product points at QB Item ID 202 (does not exist in QBO Items catalog).",
      "verdict": "UNVERIFIED",
      "expected_outcomes": [
        "Zap Step 5 (Create Invoice) errors with 'Item Ref 202 not found'"
      ],
      "actual_outcomes": [
        "Airtable Automation completed; webhook fired; Zap task history not exported"
      ],
      "unverified_reasons": [
        "Zapier task history wasn't exported for this case - can't confirm whether Step 5 errored as expected or failed silently"
      ],
      "notes": "Recommend re-run with Zap task export captured."
    }
  ],
  "unexpected_writes": [
    "fldNotes on recXXX got 'last sync' update - not predicted by any case. Trace to: scheduled automation 'Sync Notes Hourly' coincidentally ran during eval window. Not workflow-related."
  ],
  "followups": [
    "Add observer for Zapier task export to cover UNVERIFIED case 03",
    "Add a case for Product with valid Item ID but wrong tax category (next likely failure mode)",
    "Consider migrating the eval twin's Zap to point at QBO Sandbox to remove the production-data risk on case 01"
  ]
}
```

## Field rules

- `verdict` must be exactly `"PASS"` | `"FAIL"` | `"UNVERIFIED"` (the renderer's summary line counts these).
- `expected_outcomes` and `actual_outcomes` are arrays of strings, human-readable, not raw JSON. The renderer prints them as bullets.
- `diff` is optional; include it inline when the diff is small or surprising. Otherwise leave it out, the diff.json file in `runs/<case>/` is the canonical record.
- `unverified_reasons` (for UNVERIFIED cases) and `failure_reasons` (for FAIL cases) are required if the verdict is non-PASS. The renderer emits a dedicated section. **A FAIL without `failure_reasons` is uninterpretable, refuse to ship the report.**
- `unexpected_writes` catches writes the eval saw that weren't predicted by any case. If empty, omit the section entirely.
- `followups` is open-ended, every eval should produce at least one ("add a case for X", "wire up observer Y") unless coverage is genuinely complete.

## Markdown report shape (what the renderer emits)

```
# Post-Run Analysis - <workflow>

**Run date:** YYYY-MM-DD
**Summary:** N PASS / M FAIL / K UNVERIFIED

## Inventory notes
<inventory_notes>

## Cases

### <case name> - <verdict>

<description>

**Expected:**
- ...

**Actual:**
- ...

**Observed state changes:**
<diff rendered as bullets per table>

**Why FAIL:** / **Why UNVERIFIED:**
- ...

**Notes:** ...

## Unexpected writes (not predicted by any case)
- ...

## Follow-ups
- ...
```

## What the renderer does NOT do

- Doesn't decide verdicts. You write the verdict; the renderer formats it.
- Doesn't read scripts or evidence. That's Claude's job in Phase 4, serialized into `result.json`.
- Doesn't enforce field requirements (e.g., `failure_reasons` for FAIL). Claude enforces that rule before writing `result.json`.
