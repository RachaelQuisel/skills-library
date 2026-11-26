# workflow-spec.json schema

The workflow spec is the eval contract for a chain. One per workflow. Lives at `workflow_eval/<workflow-name>/workflow-spec.json`.

## Required fields

| Field | Type | Notes |
|---|---|---|
| `workflow_name` | string | slug, matches the folder name |
| `production` | boolean | if `true`, Claude requires verbal confirmation before generating cases or interpreting evidence |
| `trigger` | object | what fires the chain |
| `chain` | array | ordered steps in the chain |
| `downstream_observers` | array | where to look for evidence of effects |

## Optional fields

| Field | Type | Notes |
|---|---|---|
| `sandbox_base_id` | string | if non-prod |
| `production_base_id` | string | if applicable; must be distinct from `sandbox_base_id` |
| `inventory_source` | string | path to the audit-airtable-automations output if available, or freeform note |
| `notes` | string | freeform |

## `trigger` shape

```json
{
  "base_id": "appXXX",
  "table_id": "tblYYY",
  "field_id": "fldZZZ",
  "type": "airtable_record_updated"
}
```

Trigger `type` values:
- `airtable_record_created`
- `airtable_record_updated` (specify `field_id` - the field that fires it)
- `airtable_record_matches_conditions`
- `airtable_view_entry` (specify `view_id`)
- `airtable_scheduled`
- `webhook_inbound`
- `manual` (user-clicked button or manual run)

## `chain` shape

Ordered list. Each step:

```json
{
  "step_id": "1-script-action",
  "kind": "airtable_automation",
  "name": "Push Invoice to QuickBooks via Zapier",
  "ref": "wfl123abc",
  "script_path": "~/Claude-Work/CLIENTS/AY Media_Jay_Danzy/zapier-qb-webhook/push_invoice_to_qb_via_zapier.js",
  "notes": "Reads Advertiser link, builds payload, POSTs to Zapier webhook"
}
```

`kind` values: `airtable_automation` | `zapier_zap` | `apps_script` | `http` | `webhook` | `other`

## `downstream_observers` shape

Each observer tells Phase 3 where to look for evidence.

### Airtable observer

```json
{
  "observer_id": "qb-id-write",
  "type": "airtable",
  "base_id": "appXXX",
  "table_id": "tblContracts",
  "field_ids": ["fldQbTransactionId", "fldLastQbPush"]
}
```

Snapshots pull these tables. Diffs show changes to these fields. Optional `field_ids` narrows the relevant fields if you want a focused diff.

### Zapier task observer

```json
{
  "observer_id": "zap-uefknpv",
  "type": "zapier_task",
  "zap_id": "uefknpv",
  "evidence_format": "manual_export",
  "notes": "Export the task history for this Zap from the Zapier UI; drop in runs/<case>/zap-tasks.json"
}
```

Zapier doesn't have a stable read API for task history at the consultant tier; v1 expects manual export.

### QuickBooks observer

```json
{
  "observer_id": "qbo-invoice",
  "type": "quickbooks",
  "entity": "Invoice",
  "match_on": "DocNumber",
  "since_field": "MetaData.CreateTime",
  "notes": "Read via QBO API or eyeball in the sandbox UI; capture invoice JSON in runs/<case>/qbo-invoice.json"
}
```

### HTTP log observer

```json
{
  "observer_id": "webhook-receiver",
  "type": "http_log",
  "endpoint": "https://hooks.zapier.com/...",
  "notes": "Capture the inbound webhook payload from the receiver's log; drop in runs/<case>/webhook.json"
}
```

## Worked example: AYMG Contract → QuickBooks push v17

```json
{
  "workflow_name": "aymg-qb-push-v17",
  "production": true,
  "production_base_id": "appExample0000153",
  "sandbox_base_id": "appExample0000154",
  "inventory_source": "~/Claude-Work/CLIENTS/AY Media_Jay_Danzy/Project Documentation/schema-dependencies.md",
  "trigger": {
    "base_id": "appExample0000153",
    "table_id": "tblContracts",
    "field_id": "fldPushTrigger",
    "type": "airtable_record_updated"
  },
  "chain": [
    {
      "step_id": "1-airtable-script",
      "kind": "airtable_automation",
      "name": "Push Invoice to QuickBooks via Zapier",
      "ref": "wfl<id>",
      "script_path": "~/Claude-Work/CLIENTS/AY Media_Jay_Danzy/zapier-qb-webhook/push_invoice_to_qb_via_zapier.js",
      "notes": "v17 - reads Advertiser via Contract.Advertiser link, throws 5 friendly errors on missing data"
    },
    {
      "step_id": "2-zapier-zap",
      "kind": "zapier_zap",
      "name": "AYMG Push → QBO",
      "ref": "uefknpv",
      "notes": "Catches webhook, Find Customer, Create Invoice, Attach Tear Sheets"
    }
  ],
  "downstream_observers": [
    {
      "observer_id": "contract-last-push",
      "type": "airtable",
      "base_id": "appExample0000153",
      "table_id": "tblContracts",
      "field_ids": ["fldLastQbPush", "fldQbTransactionId"]
    },
    {
      "observer_id": "zap-task",
      "type": "zapier_task",
      "zap_id": "uefknpv",
      "evidence_format": "manual_export"
    },
    {
      "observer_id": "qbo-invoice",
      "type": "quickbooks",
      "entity": "Invoice",
      "match_on": "DocNumber"
    }
  ],
  "notes": "v17 adds 5 data-integrity guards after Advertiser link walk. Test UAMS recExample0000152 (populated) + a Contract with no Advertiser link (red path)."
}
```
