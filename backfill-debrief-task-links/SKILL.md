---
name: backfill-debrief-task-links
version: 1.0.1
description: Populate empty "Debrief Tasks" link fields on Tasks records for one explicitly named XRAY client so meeting-created tasks appear on Workzone meeting pages. Use when someone asks to "backfill debrief tasks for [client]," says tasks are not connected to a meeting, or reports that a meeting page shows no tasks even though tasks exist. Perform a client-scoped Airtable repair with read-only preflight and per-record verification; never write base-wide or without a named client.
---

# Backfill Debrief Task Links

## Purpose in plain English

This skill helps you reconnect a named client's meeting tasks so they appear with the meeting where they belong.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Repair the missing reverse-facing meeting link by copying each eligible task's
verified `Debrief Recordings` links into its empty `Debrief Tasks` field.

## Safety contract

- Require exactly one explicitly named client. Reject an unscoped, multi-client,
  or "all clients" write request.
- Treat an explicit request to backfill, fix, or reconnect a named client's tasks
  as write approval. If the user only reports symptoms, diagnose read-only and
  request approval before updating records.
- Read [references/airtable-schema.md](references/airtable-schema.md) before any
  Airtable call. Treat its IDs as expected values that must pass live preflight.
- Require the `tasks-xray-tech` profile for upstream reads and approved updates.
  Use the `project-management` profile only for the optional client-interface
  check. A missing client-interface profile does not block upstream repair.
- Check profiles without displaying `whoami` output. Redirect stdout and stderr,
  then report only `configured` or `unavailable`. Never display, log, or store PAT
  values. Never ask the user to paste a PAT into the conversation.
- Write only the `Debrief Tasks` field on manifest-listed Tasks records. Never
  create or delete records, clear links, change another field, or update a task
  whose target field is already populated.
- Treat a linked-record update as replacement of that field's complete value.
  Re-read one task immediately before its one-record write and again afterward.
  Do not claim compare-and-swap protection unless the discovered tool provides it.
- Determine scope from linked client record IDs. Do not infer ownership from a
  meeting title. Skip unstamped, multiply stamped, mixed-client, missing, or
  otherwise ambiguous meetings.

## Workflow

1. **Confirm scope and authorization.** Record the exact client name. Ask for it
   if absent. Resolve it to exactly one record in `XRay's Clients`; stop on zero
   or multiple matches and request a record ID.

2. **Discover tools, profiles, bases, and schema.** Discover current Airtable
   tools and their access classes. Confirm `tasks-xray-tech` without printing its
   authentication output:

   ```sh
   airtable-mcp whoami --profile tasks-xray-tech >/dev/null 2>&1
   ```

   Confirm `project-management` the same way when an interface check is possible.
   Every later Airtable CLI call must include its explicit profile.

   - With `tasks-xray-tech`, resolve the upstream `Projects & Tasks at XRAY` base
     and compare every required table, field, reciprocal link, field type, and
     linked-table target with the schema contract.
   - With `project-management`, try to find one client project-management base
     whose name contains XRAY and the client's canonical name or approved
     abbreviation. Record the exact live name and ID. If none or more than one
     matches, mark the interface check unavailable and continue upstream.

   Stop before task reads when the upstream profile, base, or schema fails.

3. **Build an immutable before-manifest.** Page through every Tasks record whose
   `Debrief Recordings` field is non-empty and whose `Debrief Tasks` field is
   empty. Request both fields and follow every cursor. Record the global before
   count, task IDs, complete source meeting ID sets, and empty target ID sets.

4. **Prove client scope.** Fetch every distinct source meeting and its `XRay's
   Client` link with `tasks-xray-tech`. Compare linked record IDs with the target
   client record ID. Include a task only when every source meeting has exactly one
   client link and every link matches the approved client.

5. **Generate the write plan.** Pass the scoped manifest to
   `scripts/prepare_backfill.py` through stdin. Include one object per task:

   ```json
   {
     "clientRecordId": "rec...",
     "tasks": [{
       "taskRecordId": "rec...",
       "sourceMeetingIds": ["rec..."],
       "targetMeetingIds": [],
       "meetings": [{
         "recordId": "rec...",
         "clientRecordIds": ["rec..."]
       }]
     }]
   }
   ```

   The script must exit successfully before any write. Review its exclusions and
   use only its one-record update payloads. It does not call Airtable or use
   credentials.

6. **Revalidate and update one task at a time.** Immediately before each write,
   re-read that task with `tasks-xray-tech`. Proceed only when its source set is
   unchanged and its target remains empty. Send the exact script-generated
   payload, then read the task back. Treat matching source and target sets as
   success.

   If a response is missing or ambiguous, read before retrying. Do not retry a
   task whose target is populated or whose source changed. Retry one confirmed
   transient no-write failure once. Stop further writes on authentication,
   permission, or schema errors. Re-read every attempted task and classify it as
   verified success, verified unchanged, or unknown. Do not report completion
   while any result is unknown.

7. **Verify upstream.** Re-read every successful task and compare both link sets
   with the script's verification expectations. Rerun the complete mismatch query,
   resolve remaining meetings' client links, and confirm zero eligible in-scope
   tasks remain. Record the global after count. Treat unrelated concurrent changes
   as a count discrepancy to explain, not as proof that task writes failed.

8. **Check the client interface when available.** With `project-management`,
   spot-check one affected meeting page in the resolved client base. Allow for
   sync delay and refresh if needed. If the profile, base, page, or interface data
   is unavailable, report that the interface check was not completed. Do not
   infer interface success from upstream table data.

9. **Report evidence.** Report verified upstream base name and ID, client name
   and record ID, profile roles used, schema result, before and after mismatch
   counts, tasks updated, meetings affected, per-record verification, interface
   result, and every skipped or failed record with its reason. Note that updates
   change Tasks' last-modified timestamps.

End with the standing limitation: this repairs existing links only. New tasks can
recreate the gap until the task-creation system writes both meeting-link fields or
the meeting page reads the source field.
