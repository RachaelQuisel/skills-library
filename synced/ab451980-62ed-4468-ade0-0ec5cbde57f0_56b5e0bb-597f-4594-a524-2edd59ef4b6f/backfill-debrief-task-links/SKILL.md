---
name: backfill-debrief-task-links
description: Reconnect meeting-created tasks to the Workzone meeting pages for a specific XRAY client by backfilling the "Debrief Tasks" link field in Airtable. Use when tasks created from a meeting (by the tasks.xray.tech service) don't show up in a meeting page's task tabs, when someone says "tasks aren't connected to the meeting," "backfill debrief tasks for [client]," or "the meeting page shows no tasks." Scoped to one or more named clients — never run base-wide without explicit approval.
---

# Backfill Debrief Task Links

## The problem this fixes

The Workzone base's Tasks table has TWO link fields to Debrief Recordings (meetings):

- "Debrief Recordings" (fldmzmZy2D1yh5B7p) — the field the external tasks.xray.tech
  service writes when it creates tasks from a meeting. Always populated.
- "Debrief Tasks" (fldXbCPMQBosF9Vre) — the field the meeting page's task tabs
  ("AI-Proposed Tasks / Trash / Created! / All tasks") actually read. The service
  never writes it, so meeting pages show "No tasks found that match current filters."

The fix is additive: copy each task's "Debrief Recordings" links into its empty
"Debrief Tasks" field. Nothing is ever removed or overwritten.

## Key IDs

- Base: appQAdxI2hDNJj1g5 (Projects & Tasks at XRAY)
- Tasks table: tblvlJq7I2GvIQEyP
- Debrief Recordings table: tblYLGhD3Ii7EkGZY
- Tasks."Debrief Recordings": fldmzmZy2D1yh5B7p
- Tasks."Debrief Tasks": fldXbCPMQBosF9Vre
- Debriefs."XRay's Client": fld9YZme9QfpVSYgm

## Steps

1. **Confirm scope first.** Ask which client(s) unless the request names them.
   Never touch tasks for clients outside the approved scope, and never delete
   or replace existing links.

2. **Pull the mismatch list.** Page through Tasks (pageSize 100, follow cursor)
   with fieldIds [fldmzmZy2D1yh5B7p] and this filter:

   ```json
   {"operator": "and", "operands": [
     {"operator": "isNotEmpty", "operands": ["fldmzmZy2D1yh5B7p"]},
     {"operator": "isEmpty", "operands": ["fldXbCPMQBosF9Vre"]}
   ]}
   ```

   Record the totalRecordCount — it is the before number for verification.

3. **Resolve which meetings belong to the client — by client stamp, not name.**
   Collect the distinct debrief record IDs from the mismatch list and fetch them
   from tblYLGhD3Ii7EkGZY with fieldIds [fld9YZme9QfpVSYgm]. A meeting is in
   scope when "XRay's Client" matches the target client. Two lessons learned:
   - Meeting names lie by omission: CCRES meetings have shown up as "Zoom Meeting"
     and "Matt Przywara: Zoom event"; Coding Clarified as "GitHub Repo" and
     "Janine Mothershed" events. Sweep every distinct meeting's client stamp.
   - Older meetings may have no client stamped (they predate CRM Client Stamping).
     For those, include only exact matches to the client's known recurring meeting
     name (e.g. "XRAY <> Guardians of Love"), and say so in the report.

4. **Backfill in batches.** For each in-scope task, set "Debrief Tasks" to the
   exact record IDs already in its "Debrief Recordings" field (all of them, if
   more than one). Use update_records_for_table with batches of about 10.
   If a batch is denied by a permission classifier, retry once, then split it
   smaller — do not skip records silently.

5. **Verify.** Re-run the step-2 filter with pageSize 1. The totalRecordCount
   must have dropped by exactly the number of tasks updated, and the first
   remaining record should belong to an out-of-scope client. Spot-check one
   meeting page: the backfilled tasks appear in its "All tasks" tab immediately,
   no refresh needed.

6. **Report.** Before-and-after counts, tasks updated per meeting, any meetings
   included by name-match rather than client stamp, and the standing reminder:
   this is symptom repair. New tasks from tasks.xray.tech will recreate the gap
   until either that service also writes "Debrief Tasks" or the meeting page's
   task element is repointed to "Debrief Recordings" in the interface builder.

## Guardrails

- Additive only. Never clear, replace, or delete link values; a task that already
  has "Debrief Tasks" set is skipped by the step-2 filter automatically.
- Scope is per client and per explicit approval. Quantify anything out of scope
  ("N tasks for other clients still have the gap") but leave it untouched.
- Updates touch last-modified timestamps on the affected tasks; mention this if
  anyone relies on modified-time sorting or reports.
