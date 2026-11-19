# Case JSON schema

Each case file lives at `workflow_eval/<workflow-name>/cases/NN-<slug>.json`. Each case is one scenario you'll run against the workflow.

## Required fields

| Field | Type | Notes |
|---|---|---|
| `name` | string | matches the file slug |
| `description` | string | what this case tests + why it matters |
| `input` | object | freeform, whatever the user will use as the trigger |
| `expected_outcomes` | array | what should be true after the workflow runs |

## Optional fields

| Field | Type | Notes |
|---|---|---|
| `expected_error` | object | for error-path cases (see below) |
| `max_wait_seconds` | number | how long to wait after triggering before snapshotting after-state; default 60 |
| `notes` | string | freeform |
| `cleanup` | string | `delete` \| `flag` \| `none` - guidance for the user, not auto-executed |

## `expected_outcomes`: each entry

```json
{
  "observer_id": "contract-last-push",
  "what_to_check": "field fldLastQbPush on the triggered Contract",
  "match_rule": "contains",
  "match_value": "SUCCESS",
  "notes": "fldLastQbPush gets a SUCCESS marker after the QB push completes"
}
```

`match_rule` values:
- `equals` - exact match
- `contains` - substring match (for text fields, error messages)
- `regex` - Python regex match
- `present` - field exists and is non-null/non-empty
- `absent` - field doesn't exist OR is null/empty
- `count_equals` - number of matching records equals `match_value` (use when expecting N writes)
- `count_gte` - at least N matching records

> Claude interprets `match_rule` values in Phase 4 when comparing evidence against expected outcomes. The Python helper does not parse or enforce them, it only formats results Claude has already verdicted.

## `expected_error`: for error-path cases

```json
{
  "expected_error": {
    "where": "airtable_automation_run",
    "match_rule": "contains",
    "match_value": "Advertiser is not linked",
    "notes": "v17 throws this when Contract.Advertiser is empty"
  }
}
```

`where` values:
- `airtable_automation_run` - error from Airtable's automation run history
- `zapier_task` - error from Zapier task history
- `downstream_api` - error from QBO / external API
- `script_exception` - uncaught exception in script output

## Refuse-to-save rule

If `expected_outcomes` is empty AND `expected_error` is missing, refuse to save the case. Eval can't verify "nothing should happen" without explicit absent markers, express that explicitly:

```json
{
  "expected_outcomes": [
    {
      "observer_id": "contract-last-push",
      "what_to_check": "any field on the triggered Contract",
      "match_rule": "absent"
    }
  ]
}
```

## Worked examples

### Happy path

```json
{
  "name": "01-uams-happy-path",
  "description": "UAMS contract has a linked Advertiser with QB Customer ID populated. v17 should walk the Advertiser link, find the customer, push the invoice, and stamp fldLastQbPush with SUCCESS.",
  "input": {
    "record_id": "recQWdfjq9ILIY5XO",
    "trigger_action": "check fldPushTrigger checkbox",
    "notes": "User PATCHes fldPushTrigger=true via Airtable UI or API"
  },
  "expected_outcomes": [
    {
      "observer_id": "contract-last-push",
      "what_to_check": "field fldLastQbPush on recQWdfjq9ILIY5XO",
      "match_rule": "contains",
      "match_value": "SUCCESS"
    },
    {
      "observer_id": "contract-last-push",
      "what_to_check": "field fldQbTransactionId on recQWdfjq9ILIY5XO",
      "match_rule": "present"
    },
    {
      "observer_id": "qbo-invoice",
      "what_to_check": "new Invoice in QBO sandbox matching the Contract amount",
      "match_rule": "present"
    }
  ],
  "max_wait_seconds": 90,
  "notes": "Test in QBO sandbox first if possible."
}
```

### Missing-required-input edge

```json
{
  "name": "02-no-advertiser-link",
  "description": "Contract has no linked Advertiser. v17 should throw 'Advertiser is not linked' before reaching Step 5 (Find Customer).",
  "input": {
    "record_id": "<choose a Contract with empty Advertiser link>",
    "trigger_action": "check fldPushTrigger checkbox"
  },
  "expected_outcomes": [
    {
      "observer_id": "contract-last-push",
      "what_to_check": "field fldQbTransactionId on the triggered Contract",
      "match_rule": "absent"
    }
  ],
  "expected_error": {
    "where": "airtable_automation_run",
    "match_rule": "contains",
    "match_value": "Advertiser is not linked"
  },
  "notes": "Red-path validation. v17's first guard."
}
```

### Idempotency

```json
{
  "name": "03-idempotency",
  "description": "Run the same happy-path trigger twice. Second run should be a no-op (fldLastQbPush already SUCCESS, fldQbTransactionId already populated).",
  "input": {
    "record_id": "recQWdfjq9ILIY5XO",
    "trigger_action": "check fldPushTrigger checkbox; uncheck; check again"
  },
  "expected_outcomes": [
    {
      "observer_id": "qbo-invoice",
      "what_to_check": "count of new Invoices in QBO sandbox for this Contract since trigger_timestamp",
      "match_rule": "count_equals",
      "match_value": 1,
      "notes": "Second run must not create a duplicate invoice"
    }
  ],
  "notes": "This is the case that catches double-write bugs. Critical."
}
```
