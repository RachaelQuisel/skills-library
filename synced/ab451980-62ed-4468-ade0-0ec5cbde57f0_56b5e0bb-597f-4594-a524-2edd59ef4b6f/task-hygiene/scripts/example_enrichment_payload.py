#!/usr/bin/env python3
"""
REFERENCE EXAMPLE — a real, verified enrichment run (2026-08-22, 17 tasks).
Copy this shape for each new batch: one PLAN tuple per task with an explicit
rationale, payload written to JSON for review BEFORE any Airtable write,
sanity assertions, and a printed review table. Swap in the new batch's
record IDs, hours, outcomes, and parents; the structure stays.

Hours -> Hours Estimated (Backlog tasks; Hours Used stays untouched).
"""
import json

F_HOURS_EST = "fld88Zg1liE6QHLNj"
F_OUTCOMES = "fldxDjgnu1i9jp4jl"
F_PARENT = "fldBH3Rfbgsk17Py2"

# Outcomes
OUT_OVERHAUL = "recLn3QUK13yVfor7"   # CC: Transcript & Enrollment Document Overhaul
OUT_HOURLY = "recSy05yToaBpEfbt"     # Our Hourly Work
OUT_STATUS = "rec2RRAKmofRAx1u0"     # Monitor Student Status Automations -> LOA & Graduated (In Testing)
OUT_PROPOSAL = "recLU2u8YnZYKgcZw"   # CC: Proposal follow-up automation health check (In Progress)
OUT_WRAPUP = "rec0ukDR8n2u9j5Zf"     # CC: Contract Wrap-up & Transition (new)
OUT_AUDIT = "recQ8SnMhBjh6zbfX"      # Audit Tool: Deliverable Positioning & Beta (new)

PARENT_STATUS_CALC = "rect1BqVefi34vPE4"  # Deploy and Review Student-Status Calculator
PARENT_REPO_AUDIT = "recE8pdGp075EgMAi"   # GitHub Repo Audit Review and Deliverable Positioning

# (record_id, name, hours, outcome, parent, rationale)
PLAN = [
    # --- Aug 13, 15:52 batch (CC client debrief) ---
    ("rec5UGjRYo0Y590ea", "Repoint and Refactor Email Automations to Use Grade Attempts Table", 30,
     OUT_STATUS, None,
     "Debrief's own numbers: 7-13 automations at 3-5h each = 21-65h. 30 is the "
     "conservative-mid estimate; revisit after the first two automations."),
    ("rect1BqVefi34vPE4", "Deploy and Review Student-Status Calculator", 4,
     OUT_STATUS, None, "Finish deploy + produce disagreement list for Janine."),
    ("recnO5UOp2uH7Dtsp", "Revise Credentials for Proposal Emails", 1,
     OUT_PROPOSAL, None, "Credential swap once Janine shares the account."),
    ("recwqDkezCAq5OTER", "Create and Update Brand Assets and Manuals", 3,
     OUT_OVERHAUL, None,
     "Janine drives asset creation; 3h is Rachael's coordination + per-item ticket prep."),
    ("reccGbV2l5REWwzQ3", "Investigate AAPC Reporting Integration", 3,
     OUT_HOURLY, None, "Discovery on AAPC integration points + Drive doc review."),
    ("recHF78Mh5DK2rYnO", "Revisit Status Calculator Frequency/Cost", 1,
     OUT_STATUS, PARENT_STATUS_CALC,
     "Explicitly 'after first beta run' -> child of the deploy task."),
    # --- Aug 13, 23:32 batch (XRAY internal debrief) ---
    ("recfbFZfm9bMHVBbi", "Client AI Usage Analysis", 3,
     OUT_WRAPUP, None, "Usage breakdown by client/feature + client-facing report."),
    ("recrGBHWGoTFiOF39", "Synthesize Call Transcripts with AI", 2,
     OUT_WRAPUP, None, "Transcript synthesis feeding wrap-up content."),
    ("recnaZ4NeKrhheZFY", "End-of-Contract Chapter Meetings", 2,
     OUT_WRAPUP, None, "Scheduling + prep for CC and GOL chapter meetings."),
    ("recb6LGYVVkyNbYun", "Consult on Meeting Timing and Format", 0.5,
     OUT_WRAPUP, None, "Quick input-gathering from Dylan and Ari."),
    ("recE8pdGp075EgMAi", "GitHub Repo Audit Review and Deliverable Positioning", 3,
     OUT_AUDIT, None, "Review audit output with Mark + run on client bases."),
    ("rec9KLcA4wowyublN", "Explore Next-Phase Work with Audit Exports", 3,
     OUT_AUDIT, PARENT_REPO_AUDIT,
     "Builds directly on the audit review -> child of it."),
    # --- Aug 6 batch ---
    ("recYNcmIgkp71VOM2", "Demo the Schema/Relationship Tool", 1,
     OUT_AUDIT, None, "Prep + team demo of a tool that already exists."),
    ("recsxXC8kRHAGz8fh", "Gather Intel on Airtable Pricing", 1,
     OUT_AUDIT, None, "Slack community DMs/posts; async and light."),
    ("reccpDwuk1crMxlGH", "Reach Out to Airtable Contacts", 0.5,
     OUT_AUDIT, None, "Audie's outreach; 0.5h is the team-side coordination."),
    ("rec2jL6U5V8SjFt7x", "Internal Dogfood and Identify Beta Customers", 3,
     OUT_AUDIT, None, "Hands-on pipeline testing + beta shortlist."),
    ("recUHDG2aTDoGghwm", "Charette-den Design Suggestions", 0.5,
     None, None, "Send Mark a room video. Personal favor - no outcome fits; left unlinked."),
]

records = []
for rec_id, name, hours, outcome, parent, _ in PLAN:
    fields = {F_HOURS_EST: hours}
    if outcome:
        fields[F_OUTCOMES] = [outcome]
    if parent:
        fields[F_PARENT] = [parent]
    records.append({"id": rec_id, "fields": fields})

assert len({r["id"] for r in records}) == len(records) == 17
total = sum(r["fields"][F_HOURS_EST] for r in records)

with open("task_updates_batch2.json", "w") as f:
    json.dump({"baseId": "appQAdxI2hDNJj1g5", "tableId": "tblvlJq7I2GvIQEyP",
               "records": records}, f, indent=2)

names = {OUT_OVERHAUL: "Overhaul", OUT_HOURLY: "Hourly Work", OUT_STATUS: "Status Calc",
         OUT_PROPOSAL: "Proposal HC", OUT_WRAPUP: "Wrap-up", OUT_AUDIT: "Audit Tool", None: "—"}
print(f"{'Task':<58}{'Hrs':>5}  {'Outcome':<12}{'Parent'}")
for rec_id, name, hours, outcome, parent, _ in PLAN:
    par = "Status Calc deploy" if parent == PARENT_STATUS_CALC else ("Repo Audit Review" if parent == PARENT_REPO_AUDIT else "—")
    print(f"{name[:57]:<58}{hours:>5}  {names[outcome]:<12}{par}")
print(f"\n17 records, {total} hours total -> task_updates_batch2.json")
