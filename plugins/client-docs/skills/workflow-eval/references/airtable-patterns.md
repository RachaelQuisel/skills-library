# Airtable-side eval patterns

Practitioner-derived patterns for testing Airtable automation chains. Use these when designing cases and reading evidence, they're not enforced by tooling, they're disciplines.

## Pattern 1: Trigger/action split with a manual checkbox gate

The most-upvoted pattern on the canonical Airtable Community thread on testing automations without hitting clients. The load-bearing trick is the **manual checkbox gate**.

How it works:
1. Add a checkbox field to the trigger table called something like `Eval Test Mode`. Default unchecked.
2. The production automation's trigger conditions check `Eval Test Mode = false` (or omit the field check entirely if you don't want to modify the production trigger).
3. Create a SECOND automation, identical in script logic, whose trigger conditions check `Eval Test Mode = true`. This is the eval-only twin.
4. Cases set `Eval Test Mode = true` on the input record. The eval twin fires; the production automation stays quiet.
5. After the eval, flip `Eval Test Mode` back to false (or delete the test record per the case's `cleanup` field).

Why this matters for eval design:
- Lets you run cases against real production data without triggering real client-facing side effects (e.g., emails, invoice pushes)
- The eval twin can be configured to point at the QBO Sandbox while production points at the live QBO company
- The checkbox makes test records self-identifying, easy to find later for cleanup

Caveats:
- This doubles maintenance: any script change has to happen in both twins. Mitigate by extracting shared logic into a `library_<name>` Airtable record (Scripting Extension snippet) referenced by both automations.
- Doesn't work for triggers that don't have field-level conditions (e.g., "Record created" without further filtering).

## Pattern 2: Downstream sandbox

Universal best practice for chains that end in external SaaS (QuickBooks, Stripe, Shopify, etc.).

How it works:
- Point the eval twin's Zapier Zap at the downstream system's sandbox credentials instead of production
- Verify shape, side effects, error handling against the sandbox
- Swap credentials to production only after the sandbox runs clean

Why this matters for eval design:
- The eval framework's `downstream_observers` can point at sandbox URLs / sandbox APIs in non-prod cases
- A case can have `production: false` in the workflow spec but still verify real side effects (just in sandbox)

Caveats:
- Sandbox state can drift from production state. A case that passes in sandbox can fail in production due to data shape differences (e.g., production has a customer with multiple Ship Addresses; sandbox doesn't). Mitigate by occasionally rotating real-but-sanitized production data into sandbox.
- Some integrations have no sandbox mode. Note these as `sandbox_unavailable: true` in the observer and design cases that can be safely run against the live system.

## Pattern 3: Schema snapshot before every eval

Before running any case (Phase 3), capture the current schema of every observed table:

```bash
# Conceptual - not yet a helper subcommand
mcp__airtable-pat__describe_table baseId=appXXX tableId=tblYYY detailLevel=full
```

Save it to `runs/schema-snapshot-<timestamp>.json`. Use it to:
- Validate cases (Phase 3 schema staleness check)
- Detect field renames after the eval (a field referenced by a case may have been renamed since the case was authored)
- Provide diff context in the post-run analysis when a previously-existing field disappears

## Pattern 4: Trigger-by-timestamp, not by snapshot diff

When verifying downstream effects, don't try to diff full record snapshots, at scale it's expensive and misses updates where field value coincidentally matches.

Instead:
1. Capture `trigger_timestamp` (UTC ISO) before PATCHing the input record
2. Snapshot AFTER state filtered to `IS_AFTER(LAST_MODIFIED_TIME(), trigger_timestamp)` (`eval_helper.py snapshot --since <ts>`)
3. The result is the change set since trigger, small, focused, includes updates to pre-existing records

This is what the `--since` flag on `snapshot` is for.

## Pattern 5: Recursive observer for cascading chains

When automation A's output is automation B's input is automation C's input, observers should be defined for each step's output, not just the chain's final output. Otherwise a silent mid-chain failure looks like a timing problem.

Example: EMG Contract push triggers Airtable Automation → Zapier Zap → QBO. Observers:
- `airtable` observer on Contract (Airtable Automation should stamp `fldLastQbPush` after webhook POST)
- `zapier_task` observer on the Zap (manual export, did the Zap fire and succeed?)
- `quickbooks` observer on Invoice (was the invoice created?)

A FAIL on observer 2 with PASS on observer 1 tells you the webhook fired but the Zap broke, different diagnosis from "automation didn't fire at all."

## Pattern 6: Reverse cases (what should NOT happen)

For every case where a field SHOULD be written, consider whether there's a related case where the field should NOT be written (input that should fail validation, or input that should hit a guard). Add it. Most eval gaps come from missing reverse cases.

Example: "happy path stamps fldLastQbPush=SUCCESS" should always be paired with "missing-Advertiser case leaves fldLastQbPush empty AND fldQbTransactionId absent." The absence assertion is what catches a silent-success bug where v17's guards stop throwing but also stop fully clearing failure state.
