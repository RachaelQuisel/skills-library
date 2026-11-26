---
name: workflow-eval
version: 1.4.7
description: >
  Evidence-based evaluation of multi-step automation workflow chains. Reads workflow
  scripts + before/after evidence + live Airtable state, produces per-case
  PASS / FAIL / UNVERIFIED with diffs and an unexpected-writes section. Use this skill
  whenever the user wants to verify a multi-step automation actually worked, phrases
  like "workflow eval", "automation eval", "verify this workflow", "verify my
  automation", "did this workflow work", "regression test this chain", "post-run
  analysis", "test my multi-step automation", "did the workflow succeed", "validate
  end to end", OR any time the user is checking whether an Airtable + Zapier +
  QuickBooks chain they just edited produced the expected effects. User runs the
  workflow; this skill does not execute it. Companion Python helper at
  scripts/eval_helper.py.
compatibility: "Needs the Airtable PAT MCP tools: mcp__airtable-pat__list_tables, mcp__airtable-pat__describe_table, mcp__airtable-pat__list_records, mcp__airtable-pat__get_record, mcp__airtable-pat__search_records"

---

# Workflow Eval

## Purpose in plain English

This skill helps you check whether an automation produces its intended result using its instructions, records, and observed behavior.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Evidence-based eval. The **user runs the workflow**; this skill reads scripts +
evidence + live state, then produces a per-case verdict report.

This skill does NOT execute the workflow. Claude can't reliably observe a multi-step
automation chain firing end-to-end across Airtable + Zapier + downstream systems
(timing, partial observability, multi-MCP coordination). That's a deliberate scope
boundary, not a limitation to work around.

## When to use vs when not

USE when:
- A workflow / automation chain just ran (or is about to run) and you want a structured verdict
- You're regression-testing after editing a script in an automation chain
- You want a written record of what worked and what didn't before declaring something shipped
- A client reports "the automation didn't work" and you need a structured diagnosis

DON'T use when:
- Bug-hunting in one isolated script (use `systematic-debugging`)
- Auditing what automations exist in a base (use `audit-airtable-automations`)
- Reviewing code statically without runtime evidence (use `/review` or `peer-review`)
- The user wants you to actually trigger the workflow, say so and pivot to the user-runs pattern

## Working directory

Per workflow, create `workflow_eval/<workflow-name>/` in the current working directory.
Standard layout:

```
workflow_eval/<workflow-name>/
├── workflow-spec.json
├── cases/
│   ├── 01-happy-path.json
│   └── ...
├── runs/
│   ├── <case-name>/
│   │   ├── before.json
│   │   ├── after.json
│   │   ├── diff.json
│   │   └── notes.md         # optional: user-supplied evidence
│   └── result.json           # the eval verdicts you write
└── POST_RUN_ANALYSIS_YYYY-MM-DD.md
```

---

## Phase 1: Inventory + success criteria

Read or run the inventory of automations in the workflow chain:
- Prefer existing `audit-airtable-automations` output for the base if present
- Read the actual script files (Airtable script-action scripts, Zapier Code steps, Apps Script, custom Python)
- Identify: trigger table+field, every action in the chain, every downstream write target, every external system touched

Write `workflow-spec.json`. Schema and worked example in `references/workflow-spec-schema.md`. Key fields:

- `workflow_name` - slug used for the folder
- `production` - boolean. If true, additional confirmation gate before later phases
- `trigger` - `{base_id, table_id, field_id, type}`
- `chain` - ordered list of `{step_id, kind: airtable_automation|zapier_zap|apps_script|http|other, name, ref}` (ref = automation ID, Zap ID, script path)
- `downstream_observers` - list of `{type: airtable|zapier_task|quickbooks|http_log, ...config}` - where to look for evidence
- `sandbox_base_id` (optional), if non-prod
- `production_base_id` (optional), must be distinct from sandbox_base_id if both present
- `notes` - free text

Define what success looks like for the chain AS A WHOLE. Per-step success goes in case files.

---

## Phase 2: Case build

Propose 5-10 cases covering:
- **Happy path**: typical input, all writes succeed
- **Missing required input**: input that should trigger a guarded error path
- **Multi-link edges**: input with 2+ linked records where the workflow expects exactly one
- **Stale or empty lookup**: input where lookup fields haven't propagated yet
- **Idempotency**: same input run twice; second run should be a no-op or controlled re-run
- **Production-only edge**: real-world record class that synthetic data won't surface (named historical record)

Write each case to `cases/<NN>-<slug>.json`. Schema in `references/case-schema.md`. **Propose one case at a time, conversational, let the user confirm or edit before saving the next.** No batching.

Each case has:
- `name`, `description`
- `input` - what the user will use as the trigger (record fields to PATCH, payload to POST, etc.)
- `expected_outcomes[]` - list of `{observer_id, what_to_check, match_rule}` where `match_rule` is `equals` / `contains` / `regex` / `present` / `absent`
- `expected_error?` - for error-path cases (substring or regex matched against captured errors)
- `notes`

If a case has empty `expected_outcomes` AND no `expected_error`, refuse to save, eval can't verify "nothing should happen" without explicit absent markers.

---

## Phase 3: Evidence gather (user-driven, Python helper available)

User runs the workflow for each case (or runs it naturally in production). User provides evidence:

- **Before-state snapshot**: pre-trigger Airtable state for the observed tables
- **After-state snapshot**: post-trigger state of the same tables
- **Run history** (optional but valuable), Airtable automation logs page export, Zapier task history JSON, QBO audit log
- **Error messages / screenshots / freeform notes**: drop in `runs/<case>/notes.md`

The Python helper handles Airtable snapshots:

```bash
export AIRTABLE_PAT=<pat>

python ~/.claude/skills/workflow-eval/scripts/eval_helper.py snapshot \
  --base appXXX --tables tblA,tblB,tblC \
  --out workflow_eval/<workflow-name>/runs/<case>/before.json

# User runs the workflow here

python ~/.claude/skills/workflow-eval/scripts/eval_helper.py snapshot \
  --base appXXX --tables tblA,tblB,tblC \
  --out workflow_eval/<workflow-name>/runs/<case>/after.json
```

To narrow noise on large tables, snapshot only records modified since the trigger:

```bash
python eval_helper.py snapshot --base appXXX --tables tblA \
  --since 2026-06-06T14:00:00Z --out .../after.json
```

Diff the two snapshots:

```bash
python eval_helper.py diff \
  --before .../before.json --after .../after.json \
  --out .../diff.json
```

The diff JSON contains per-table added / updated / deleted records with field-level
changes. You read this file via Read tool when synthesizing the verdict.

---

## Phase 4: Eval + report

For each case:
- Read `diff.json` (or query Airtable MCP directly for live state if no snapshot)
- Read scripts in the chain to understand intended behavior
- Read any `notes.md` evidence the user provided
- Compare actual outcomes against the case's `expected_outcomes`
- Write a verdict: **PASS** / **FAIL** / **UNVERIFIED**
  - PASS = every expected outcome observed AND no unexpected writes
  - FAIL = an expected outcome is missing OR an unexpected write occurred OR `expected_error` didn't match the captured error
  - UNVERIFIED = no expected outcomes observed AND no error captured (could be timing OR silent failure, flagged for human review)

Aggregate verdicts into `runs/result.json` (schema in `references/post-run-template.md`).
Then render the report:

```bash
python ~/.claude/skills/workflow-eval/scripts/eval_helper.py render \
  --result workflow_eval/<workflow-name>/runs/result.json \
  --out workflow_eval/<workflow-name>/POST_RUN_ANALYSIS_$(date +%Y-%m-%d).md
```

You may also write the Markdown directly without the renderer if there are only 1-2
cases. The renderer keeps formatting consistent across many cases.

The report's summary line is the headline: `N PASS / M FAIL / K UNVERIFIED`. **Never
claim a workflow passed if any case is FAIL or UNVERIFIED** without explicitly naming
those cases in the summary. UNVERIFIED means evidence was insufficient, could be
timing, could be silent failure, could be a missing observer. Reading "no FAIL" as
"green light" is exactly the failure mode this skill exists to prevent; the user
ships a broken workflow because no one looked at the cases that produced no signal.

---

## Safety rules (Claude-side)

These are not Python guards, they're rules Claude follows when running this skill.

1. **Production gate.** If `workflow-spec.json` has `production: true`, ask the user to verbally confirm before generating cases or interpreting evidence against a production base. Never auto-proceed.
2. **Schema staleness check.** Before Phase 3, call `describe_table` for every table referenced by any case. If any case references a field ID not in the live schema, refuse to proceed and list the stale references. Cases must be updated before eval.
3. **Empty-expectations check.** Refuse to save a case with empty `expected_outcomes` AND no `expected_error` - eval cannot verify "nothing should happen" without explicit absent markers.
4. **Sandbox/prod distinction.** If both `sandbox_base_id` and `production_base_id` are set in the spec, refuse to proceed if they're equal.
5. **UNVERIFIED is not success.** A summary line of "5 PASS / 0 FAIL / 2 UNVERIFIED" is NOT a green light. Name the unverified cases explicitly and recommend either longer-wait re-runs or human-eyeballed verification before shipping.
6. **No silent claims of completeness.** If Phase 1 inventory was incomplete (e.g., audit skill didn't run, user gave partial scripts), say so in the report's Notes section.

---

## Companion: `audit-airtable-automations`

Phase 1's inventory is usually faster if you run `audit-airtable-automations` first
and read its `raw_automations.json` output. If the workflow involves only one
Airtable Automation and the user has the script handy, skipping audit is fine.

## References

- `references/workflow-spec-schema.md` - spec format + worked example
- `references/case-schema.md` - case format + examples for happy / edge / error cases
- `references/airtable-patterns.md` - six practitioner-derived patterns: trigger/action split with checkbox gate, downstream sandbox, schema snapshot, timestamp-based change detection, recursive observers, reverse cases
- `references/safety-and-cleanup.md` - production gate enforcement, identifying eval test records, schema staleness handling
- `references/post-run-template.md` - report shape; required structure of `result.json`
- `scripts/eval_helper.py` - snapshot / diff / render
- `scripts/README.md` - helper usage with examples

## See also

- `audit-airtable-automations` - run first to get the workflow inventory this skill's Phase 1 consumes
- `verification-before-completion` - the evidence-before-claims discipline this skill operationalizes for workflow chains
