---
name: task-hygiene
version: 1.0.0
description: Enrich and dedupe tasks in the XRAY Airtable base (Projects & Tasks at XRAY), then deliver a post-run analysis. Enrichment fills Hours Estimated, links Outcomes, and sets Parent Tasks on debrief-extracted task batches; the dedupe sweep cancels redundant duplicate tasks using conservative, non-destructive rules. Use this skill whenever the user asks to estimate hours on tasks, add or fill in outcomes, set parent tasks, organize a task batch, clean up or dedupe tasks, run task hygiene, sweep for duplicates, tidy the backlog, or enrich tasks extracted from a debrief — even if they only mention one of those pieces. Also trigger on "fill in the task fields", "add hours to these tasks", "find duplicate tasks", or "run the sweep". Always produces a post-run analysis file.
---

# Task Hygiene: Enrich, Dedupe, Analyze

Debrief-extraction runs create tasks in the XRAY Airtable base that arrive bare: no hours, no outcome links, no parent tasks — and, because the extraction automation double-fires, frequently in duplicate. This skill turns a bare batch into an organized one and leaves an audit trail good enough that Rachael can verify every decision after the fact.

The workflow has three phases. Run all three unless the user scopes the request to one. **Build every write as a Python-generated payload first, apply it second, verify it by re-reading third.** The script-then-apply pattern is not ceremony: it makes every value reviewable before it lands, makes the run repeatable, and makes the post-run analysis honest.

Base and field IDs live in `references/field-ids.md` — read it before the first Airtable call. Do not trust it blindly: if a field write fails or a name looks wrong, re-fetch the schema, use what the base actually says, and note the drift in the post-run analysis so the reference can be corrected.

## Ground rules (these override speed)

1. **Never delete records.** The API connection historically returns 403 on deletes anyway. When a record should go away, set Status to `Cancelled` and write a Triage Note explaining why, naming the keeper record, and noting that Rachael can delete from the UI. Deletion is hers alone.
2. **Never modify Done, Cancelled, or Archived records.** Completed work is history. An archived Done record still *counts as evidence* that work happened — it just cannot be written to.
3. **Write hours to `Hours Estimated`, never `Hours Used`,** unless Rachael explicitly says the tasks were already worked. Backlog tasks with fabricated Hours Used corrupt the Progress formula and billable rollups. If the user says "hours I've spent," confirm which field once — or, if running unattended, use Hours Estimated and say so prominently.
4. **Show the plan before writing** — a per-task table of hours, outcome, parent, and one-line rationale. If Rachael has said to run without questions, print the table anyway and proceed; the table then becomes part of the post-run analysis.
5. **Verify every write** by re-reading the touched records and comparing to the payload. A write that was not re-read did not happen.
6. **No silent truncation.** The Tasks table paginates. Check `totalRecordCount` against what was actually fetched before analyzing anything, and page (or refetch with a larger pageSize) until they match.

## Phase 1 — Enrich the batch

Identify the target tasks. Default scope: tasks in the relevant project whose Hours Estimated, Outcomes, AND Parent Task are all empty — usually the most recent debrief-extraction batches (they share a creation timestamp within a minute or two and their descriptions start with "Extracted from Debrief Transcription").

For each task, decide three things:

**Hours Estimated.** Infer from the task description and the nature of the work. Anchors that matched reality in past runs: quick coordination or outreach 0.5–1h; form/field edits 1h; interface permission changes 2h; document updates or new field logic 2–3h; bulk data operations 3–4h; discovery/investigation 3h. When the description contains the client's own numbers (e.g., "7–13 automations at 3–5h each"), use the conservative midpoint and say in the rationale that the estimate should be revised after the first units of work. State an overall confidence level; description-based estimates are ~70%.

**Outcome link.** Fetch the project's existing outcomes first. Map each task to an open outcome (Backlog / Ready to Start / In Progress) whose theme matches. Do not link work to a Done outcome. When a coherent cluster of 3+ tasks has no matching open outcome, create one: name it in the base's style (client-prefixed, e.g. "CC: ..."), give it a description tracing back to the source debrief and date, set Status to Ready to Start, link the project, set Owner to Rachael, and link the client record for client work. A task that fits no outcome (personal favors, one-offs) stays unlinked — say so rather than forcing it into "Our Hourly Work."

**Parent Task.** Link only when the relationship is stated or strongly implied by the descriptions themselves ("after first beta run" → child of the deploy task; a task another task explicitly says to create → child of that task). Two or three parent links per batch is normal; ten is a sign of inventing structure.

Write the plan script, print the table, apply in one `update_records_for_table` call (≤50 records per call), verify.

## Phase 2 — Dedupe sweep

Run `scripts/dedupe_analysis.py` against a complete fetch of the project's tasks (it expects `all_tasks.json` in the working directory; adjust the field-ID constants only if the schema has drifted). The rules it encodes, and why:

- Group by normalized name (case, whitespace, apostrophe/dash variants). Name match alone never condemns a record — **descriptions must match too** (or one be empty). Same name with different descriptions means different asks.
- A group containing a Done copy (archived or not) means the work happened; live open copies with matching descriptions are redundant → cancel. This archived-Done-as-evidence rule matters: the base's pattern is that Done copies get archived while their Backlog ghosts stay live, silently inflating open-work counts.
- A group of only open copies keeps the earliest; later matching copies → cancel.
- Anything with Hours Used logged, or otherwise ambiguous, is **flagged, never auto-cancelled**.
- Pairs of Done records are reported as informational only.

The script emits `dedupe_report.txt` and `cancel_payload.json`. Sanity-check the report (do the keepers make sense?), apply the payload, verify. Each cancellation's Triage Note names the keeper and the sweep date.

Duplicates are a symptom: if the sweep finds duplicates created seconds apart across multiple dates, the debrief-extraction automation is double-firing. Say so in the analysis and recommend fixing the trigger — otherwise the sweep becomes a subscription.

## Phase 3 — Post-run analysis

Always produce `post_run_analysis.md` and send it to the user along with the scripts and payloads. Structure:

```
# Post-Run Analysis — <what ran>
**Session date / base / project**
## What ran            (each pass, one short paragraph, with created outcomes named)
## The numbers         (hours written, tasks touched, links created, duplicates cancelled,
                        and the zero-lines: 0 deleted, 0 Done/Archived modified, 0 Hours Used touched)
## What the run revealed  (patterns in the data — root causes, not just symptoms)
## Mistake-avoidance checklist  (each known risk and how it was handled or why it could not be)
## Open items, in priority order
## Confidence          (percentage per category, with the reasoning)
```

The analysis is where honesty lives: name what was skipped, what was guessed, what needs Rachael's decision, and what the data revealed beyond the task at hand (e.g., a Quarters table with no current-year records, a portal exposing all clients' projects). Findings like those are often worth more than the sweep itself.

## Known environment facts (verify if a call behaves unexpectedly)

The API token can read, create, and update but **not delete** (403). Select-option writes take plain option-name strings; linked-record writes take arrays of record IDs; collaborator writes take `{"id": "usr..."}`. The response to an update echoes the union of written fields across all records in the call — a value appearing for a record you did not write that field on is its current value, not your write. Full ID map: `references/field-ids.md`.
