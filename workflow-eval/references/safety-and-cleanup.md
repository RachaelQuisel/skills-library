# Safety + cleanup rules

These are the guards Claude enforces when running the `workflow-eval` skill. They're not Python checks, they're skill discipline.

## Production gate

If `workflow-spec.json` has `production: true`:

1. Before generating cases, ask the user explicitly: "This spec is marked `production: true` and `production_base_id: <id>`. Confirm you want to proceed against the live production base."
2. Before interpreting any evidence against the production base, restate the case and ask: "About to read evidence from production base `<id>` for case `<name>`. Confirm."
3. Never assume prior confirmation carries forward across multiple cases, confirm per case.

The point isn't to slow the user down. The point is to interrupt autopilot when production reads might inform a destructive recommendation.

## Sandbox/prod distinction

If both `sandbox_base_id` and `production_base_id` are set and they're equal: refuse to proceed and surface the contradiction. Most often this means a copy-paste mistake in the spec.

## Schema staleness check (before Phase 3)

Before reading any evidence for a case, validate that every field ID referenced by the case's `expected_outcomes` and `expected_error.where` exists in the live schema:

1. For each unique `base_id` + `table_id` pair referenced in cases, call `mcp__airtable-pat__describe_table` with `detailLevel=full`
2. Build a set of valid `fld...` IDs per table
3. Walk every case; collect every `fldXXX` mentioned in `what_to_check` strings or observer `field_ids`
4. If any case references a field ID not in the live set: refuse to proceed. List the stale references. Cases must be updated before eval.

This catches the failure mode where a field got renamed/deleted weeks ago and the case file silently references a dead ID, the eval would PASS (no observable write to a nonexistent field) and the wrong conclusion would ship.

## Identifying eval test records

When the user runs cases against a real base, the test records need to be findable for cleanup. Three conventions, in order of preference:

1. **Dedicated `Eval Test Mode` checkbox** (recommended; pairs with the trigger/action-split pattern). Every test record has this checked. Cleanup = filter view + bulk delete or bulk uncheck.
2. **`Eval Run ID` text field** with a UUID per eval session. Lets you correlate test records to a specific eval run, including across multiple cases. Cleanup = filter by run ID.
3. **Naming convention** (fallback when adding a field isn't possible). Test record names get an `[EVAL <date>]` prefix. Cleanup = filter view by name.

The skill doesn't auto-create or auto-delete records. The Python helper doesn't stamp Eval Run IDs or set Eval Test Mode either, those go on the trigger record the user PATCHes before the workflow fires. The user runs the workflow; the user does the cleanup. The skill's job is to make cleanup tractable by ensuring test records are findable.

## UNVERIFIED is not success

A summary line of "5 PASS / 0 FAIL / 2 UNVERIFIED" is NOT a green light. UNVERIFIED means evidence is insufficient, could be a timing issue (poll longer), could be a silent failure (the workflow ran but produced nothing observable).

In the post-run analysis:
- Surface UNVERIFIED in its own section
- For each UNVERIFIED case, list the specific expected outcomes that weren't observed
- Recommend: longer wait + re-run, OR human-eyeballed verification, OR adding an observer that would catch the missing signal next time

Never recommend "ship it" while any case is UNVERIFIED.

## Empty-expectations refusal

Refuse to save a case where `expected_outcomes` is empty AND `expected_error` is missing. Eval can't verify "nothing should happen" without explicit absent markers. The user can express absence:

```json
"expected_outcomes": [
  {
    "observer_id": "contract-last-push",
    "what_to_check": "any field on the triggered Contract",
    "match_rule": "absent"
  }
]
```

Or set `expected_error` for error-path cases. One of the two is required.

## Stating limits in the report

Always note in the post-run analysis's "Inventory notes" section:
- Whether `audit-airtable-automations` ran (if no, what's potentially missing)
- Which observer types are in v1 coverage (Airtable + Zapier task with manual export) and which require manual evidence (QBO, HTTP logs)
- Any case that ran with partial evidence (e.g., user provided Airtable snapshots but not Zapier task export)

The goal is that a third party reading the post-run analysis a month later can tell what was tested, what wasn't, and why.
