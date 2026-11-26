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

F_HOURS_EST = "fldExample0000168"
F_OUTCOMES = "fldExample0000164"
F_PARENT = "fldExample0000165"

# Outcomes
OUT_OVERHAUL = "recExample0000185"   # CC: Transcript & Enrollment Document Overhaul
OUT_HOURLY = "recExample0000184"     # Our Hourly Work
OUT_STATUS = "recExample0000188"     # Monitor Student Status Automations -> LOA & Graduated (In Testing)
OUT_PROPOSAL = "recExample0000189"   # CC: Proposal follow-up automation health check (In Progress)
OUT_WRAPUP = "recExample0000186"     # CC: Contract Wrap-up & Transition (new)
OUT_AUDIT = "recExample0000187"      # Audit Tool: Deliverable Positioning & Beta (new)

PARENT_STATUS_CALC = "recExample0000191"  # Deploy and Review Student-Status Calculator
PARENT_REPO_AUDIT = "recExample0000192"   # GitHub Repo Audit Review and Deliverable Positioning

# (record_id, name, hours, outcome, parent, rationale)
PLAN = [
    # --- Aug 13, 15:52 batch (CC client debrief) ---
    ("recExample0000193", "Repoint and Refactor Email Automations to Use Grade Attempts Table", 30,
     OUT_STATUS, None,
     "Debrief's own numbers: 7-13 automations at 3-5h each = 21-65h. 30 is the "
     "conservative-mid estimate; revisit after the first two automations."),
    ("recExample0000191", "Deploy and Review Student-Status Calculator", 4,
     OUT_STATUS, None, "Finish deploy + produce disagreement list for Janine."),
    ("recExample0000194", "Revise Credentials for Proposal Emails", 1,
     OUT_PROPOSAL, None, "Credential swap once Janine shares the account."),
    ("recExample0000195", "Create and Update Brand Assets and Manuals", 3,
     OUT_OVERHAUL, None,
     "Janine drives asset creation; 3h is Rachael's coordination + per-item ticket prep."),
    ("recExample0000196", "Investigate AAPC Reporting Integration", 3,
     OUT_HOURLY, None, "Discovery on AAPC integration points + Drive doc review."),
    ("recExample0000197", "Revisit Status Calculator Frequency/Cost", 1,
     OUT_STATUS, PARENT_STATUS_CALC,
     "Explicitly 'after first beta run' -> child of the deploy task."),
    # --- Aug 13, 23:32 batch (XRAY internal debrief) ---
    ("recExample0000198", "Client AI Usage Analysis", 3,
     OUT_WRAPUP, None, "Usage breakdown by client/feature + client-facing report."),
    ("recExample0000199", "Synthesize Call Transcripts with AI", 2,
     OUT_WRAPUP, None, "Transcript synthesis feeding wrap-up content."),
    ("recExample0000200", "End-of-Contract Chapter Meetings", 2,
     OUT_WRAPUP, None, "Scheduling + prep for CC and EA chapter meetings."),
    ("recExample0000201", "Consult on Meeting Timing and Format", 0.5,
     OUT_WRAPUP, None, "Quick input-gathering from Dylan and Ari."),
    ("recExample0000192", "GitHub Repo Audit Review and Deliverable Positioning", 3,
     OUT_AUDIT, None, "Review audit output with Mark + run on client bases."),
    ("recExample0000202", "Explore Next-Phase Work with Audit Exports", 3,
     OUT_AUDIT, PARENT_REPO_AUDIT,
     "Builds directly on the audit review -> child of it."),
    # --- Aug 6 batch ---
    ("recExample0000203", "Demo the Schema/Relationship Tool", 1,
     OUT_AUDIT, None, "Prep + team demo of a tool that already exists."),
    ("recExample0000204", "Gather Intel on Airtable Pricing", 1,
     OUT_AUDIT, None, "Slack community DMs/posts; async and light."),
    ("recExample0000205", "Reach Out to Airtable Contacts", 0.5,
     OUT_AUDIT, None, "Audie's outreach; 0.5h is the team-side coordination."),
    ("recExample0000206", "Internal Dogfood and Identify Beta Customers", 3,
     OUT_AUDIT, None, "Hands-on pipeline testing + beta shortlist."),
    ("recExample0000207", "Charette-den Design Suggestions", 0.5,
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
    json.dump({"baseId": "appExample0000004", "tableId": "tblExample0000010",
               "records": records}, f, indent=2)

names = {OUT_OVERHAUL: "Overhaul", OUT_HOURLY: "Hourly Work", OUT_STATUS: "Status Calc",
         OUT_PROPOSAL: "Proposal HC", OUT_WRAPUP: "Wrap-up", OUT_AUDIT: "Audit Tool", None: "—"}
print(f"{'Task':<58}{'Hrs':>5}  {'Outcome':<12}{'Parent'}")
for rec_id, name, hours, outcome, parent, _ in PLAN:
    par = "Status Calc deploy" if parent == PARENT_STATUS_CALC else ("Repo Audit Review" if parent == PARENT_REPO_AUDIT else "—")
    print(f"{name[:57]:<58}{hours:>5}  {names[outcome]:<12}{par}")
print(f"\n17 records, {total} hours total -> task_updates_batch2.json")
