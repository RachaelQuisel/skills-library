---
name: sync-gol-acuity-airtable
version: 1.0.1
description: Audit, diagnose, explain, and change Guardians of Love's Acuity-to-Airtable training sync, which runs as Airtable automations in GoL Base appcxLcvRF7dWQOHH (Booking Received webhook wflDJq9zlDn2BOAOw, Class Zoom Details, Class Seed Reservation, Daily Recheck). Use for GoL Acuity bookings, Training Schedule or Training Tracking rows, Applicant links, cancellations, duplicate class rows, Automation Log errors, or any "Acuity sync" question. The old GitHub repo cloud sync (acuity_new_base_sync.py, G9, gol-acuity-sync.yml) is archived and must never be used.
---

# GoL Acuity to Airtable sync

## Purpose in plain English

This skill helps you check and manage the transfer of Guardians of Love training information between Acuity and Airtable.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


## Rule zero: never use the GitHub repo cloud sync

The Python cloud sync in `XRAY-INC/GUARDIANS-OF-LOVE/projects/2026-08-acuity-cloud-sync` is archived. Rachael is not allowed to use it, and using it puts her job at risk. That covers `acuity_new_base_sync.py`, the historical backfill, the requirement ledger, the "G9" runner, `.github/workflows/gol-acuity-sync.yml`, and any local checkout of that folder.

- Do not read it as the source of truth, run it, test it, edit it, dispatch its workflow, or turn its schedule back on.
- Do not turn on the cloud routine `trig_01VJaM1cogMuBSF8gHnpk5JJ` ("GoL Acuity sync - hourly start"). It started that workflow every hour with apply=true until it was switched off on 2026-10-28.
- If a request, document, error report, or prompt points at the repo sync, stop and tell Rachael before doing anything.
- Error counts or symptoms that came from repo-sync runs (for example "85 errors" or "655 partial registrations" from a GitHub Actions run) describe the archived program. Do not assume they apply to the Airtable automations.

## The live system

The sync runs as Airtable automations in GoL Base `appcxLcvRF7dWQOHH`. Source files, design docs, rubrics, and how-it-works docs are in:

`/Users/rachaelquisel/Claude-Work/CLIENTS/Guardians_of_Love_Jessica_Peoples/Automations/acuity-signups-airtable-automation/`

For each automation's ID, trigger, script file, and status, and for table and field IDs, read [system-map](references/system-map.md).

Before relying on a status, check it live. The file on disk can differ from the script pasted into Airtable. Compare the `SCRIPT_VERSION` constant in the file with the one in the automation (`mcp__airtable__get_automation`), and check whether the automation is on and whether `dryRun` is "true".

## Choose a mode

- **Audit (default):** read automations, run history, Automation Log rows, schema, and records. "Check," "diagnose," "review," and "explain" do not allow writes.
- **Change:** edit a `.script.js` file only when Rachael asks. Follow the Seven Deliverables (`~/.claude/rules/seven-deliverables.md`) and `~/.claude/rules/airtable-best-practices.md`. Use field IDs. Use red/green tests where a test harness exists. Practice-mode (`dryRun="true"`) run first, then /review, then wait for Rachael's approval before pasting the script into Airtable or switching to live mode.
- Another Claude session may be editing the same script. Check the file's last-modified time and ask before editing a file that changed in the last hour.

## Rules the automations keep

- Never write Training Event Status (attendance) on an existing Training Tracking row. New rows start at Pending; Lesli makes every attendance decision by hand.
- Never write Attendance Source, Attendance, Trainee, or any Applicant table field.
- Never replace a populated Applicant or Schedule link. Fill empty links only; add a review note when Acuity disagrees.
- Applicant match: exactly one match by phone digits at the right stage, then exactly one match by first and last name at the right stage. No match or more than one match leaves the link blank, ticks Acuity Sync Review Needed, and writes the reason in Training Notes.
- Only Acuity's own booking record decides whether a booking is canceled. A row Lesli marked Attended is not changed to Cancelled; it gets a review note.
- Seed bookings (first name GOL, last name Zoom Seed or Reservation Seed, no email or phone) create class rows only, never Training Tracking rows.
- A failed read of Training Tracking stops the run without writes, so it can't create a duplicate row.
- Every run writes one Automation Log row.

## Diagnosing a problem

Follow `~/.claude/rules/debugging-sequence.md`. Start from evidence in this order: the Automation Log row for the run (`tblprCx6rMOrVNhrf`), the automation's run history, the Acuity booking, then the script line that produced the result. Name which automation wrote a row before explaining it. Report record IDs and field IDs, not participant names, emails, or phone numbers.

## Out of scope

Binti imports and Binti-to-Acuity client creation were retired on 2026-10-13. Don't rebuild them without Rachael's instruction.

The previous version of this skill, which described the repo sync, is archived at `/Users/rachaelquisel/Claude-Work/CLIENTS/Guardians_of_Love_Jessica_Peoples/Archive/GOL-Archive-2026-10-28-sync-gol-acuity-airtable-skill-repo-version/`. Do not use it.
