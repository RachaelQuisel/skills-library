---
name: micro-case-study
version: 1.0.1
description: Mine client transcripts for atomic wins (one automation, form, integration, or consulting insight) and create structured MCS records — Completed or Queued. Triggers on "micro-case study", "MCS", "mine transcripts", "find wins", "queued work", "pipeline", "outreach", "revenue recovery".
tags:
  - skill
---

# Micro Case Study

## Purpose in plain English

This skill helps you find a specific client improvement and document the work, result, and supporting evidence.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


## Overview

A Micro Case Study (MCS) captures the smallest atomic unit of client value delivered — or planned: one automation, one form, one integration, one fix, one consulting insight. Not a whole project. The smallest thing that brought (or will bring) the client value.

An MCS answers three questions: What was the challenge? What did you do (or will you do)? How was it (or will it be) successful?

MCS records have two statuses:
- **Completed** — the win is done, adopted, and confirmed. Written in past tense. ("We recovered 3 hours a week.")
- **Queued** — the work is planned, in-progress, or agreed upon but not yet finished. Written in future tense. ("You could recover 3 hours a week.") Queued records become revenue recovery candidates: when a client has remaining hours and hasn't reached out in 30+ days, the system surfaces their Queued MCS records in a personalized outreach email showing what they could still get done.

The format is designed to begin a conversation, not end one. If someone's intrigued, they'll ask for more.

## Workflow

1. Pull transcripts from CRM Enriched Debriefs in the LCE/Hourly base (all engineers)
2. Scan for **completed wins AND queued work**
3. Break into atomic wins — the smallest deliverable that brought (or will bring) value
4. **Assign Status: Completed or Queued**
5. Fill out the raw data capture table (tense matches status)
6. Calculate ROI — confirmed for Completed, projected for Queued (see `references/time-to-money.md`)
7. Write the headline using the formula; it describes the CLIENT's pain, not your work
8. Assign tags — 1 primary + 1 secondary per MCS
9. **Assign visual assets** — Result icons, Highlight character, Accent pattern (see Visual Assets section)
10. **Check for duplicates / Queued-to-Completed upgrades** (see Duplicate Prevention section)
11. Write to Airtable

## Where the Transcripts Live

**Single source of truth for all transcripts.** Pull transcripts exclusively from the CRM Enriched Debriefs table. Do not pull transcripts from any other table or base.

Use `mcp__airtable__list_records` with:

- **Base:** XR - LCE / XRAY Hourly (`appMjlaeg7cFYivss`)
- **Table:** CRM Enriched Debriefs (`tblVlruQcm3Z0cBeM`)
- **No view restriction** — pull all records from all engineers' calls
- **Transcript field:** Zoom Transcript 1 (`flduLY0o5WsNiX1eL`)
- **Supplemental fields:**
  - AI Summary (`fldO6Vw6rIQJdkLq7`)
  - XRay's Clients (`fldn8giwRKZA4Lp8B`)
  - Editable Title for Softr (`fldJt5Xt7ddPQUnES`)
  - Start Time (`fldePtWlpNtfggJti`)
  - Duration (`fld2hc6S52zkl0rBv`)
  - View in Debrief (`fldFnxbo7QkGsEEpq`)
  - Editable Summary for Softr (`fldYMr0SxgHYMlWcb`)

To search for specific meetings, use `mcp__airtable__search_records` with the same base and table IDs.

**Anonymization:** Never use client names or identifiable info in the Problem, Approach, Analysis, or Result 1 columns. Use roles instead ("client," "staff," "the CEO," "the team"). This is especially important when mining transcripts from other engineers — anonymize all client-identifying details.

## XRAY's Two Layers of Value

XRAY delivers value in two layers that often happen together. Both produce standalone MCS candidates.

**Technical:** automations, integrations, forms, dashboards, data migrations

**Consulting:** workflow design, process definition, process refinement, executive coaching, business best practices, data integrity

"Helped client define 6 enrollment statuses that had never been formalized" is its own MCS, separate from the automation that uses those statuses. When you automate a process, you're also refining it; the client gets two wins: the process goes from manual to automatic AND the process itself gets better.

## How to Identify MCS Candidates

Scan transcripts for these signals:

**Technical wins (Completed):**
- Completion language: "I built...", "I set up...", "it's live now...", "that's running...", "we deployed..."
- Client confirmation of value: "this is working", "this saves us...", "we love this"
- Before/after states: "used to take X hours", "now it takes Y minutes"
- Specific metrics: hours, dollars, percentages, error counts
- Named tools/deliverables: a specific form, automation, integration, report, dashboard

**Consulting wins (Completed):**
- Process definition: "we figured out they didn't have a definition for...", "they hadn't thought about...", "we helped them define..."
- Process refinement: "we realized they could skip...", "we streamlined...", "we eliminated three steps..."
- Workflow design: "we designed a new flow for...", "we mapped out how..."
- Executive coaching: "we helped them see...", "they realized they needed to...", "we showed them the best practice is..."
- Data integrity: "we cleaned up...", "we found duplicates...", "the data was incomplete so we..."
- Data migration: "we moved everything from...", "we migrated..."

**Queued work (not yet completed):**
- Future/planned language: "we're going to...", "the plan is to...", "next step is...", "we'll set up..."
- In-progress language: "I'm working on...", "that's in progress...", "we started..."
- Conditional language: "once we get access...", "when the data is ready...", "as soon as they send credentials..."
- Client agreement: "yes, let's do that", "go ahead with that", "sounds good, let's move forward"
- Scoping language: "we need to build...", "this will require...", "the approach would be..."

**Break work into atomic wins.** If a transcript mentions "we built the whole student portal," break it apart: the caseworker lookup, the transcript download, the status tracker. Each is its own MCS. If a consulting conversation produced multiple insights, each insight that changed the client's behavior or decision is its own MCS.

## MCS Triggers: When to Create One

- ROI win: client recovered measurable time or money
- Process improvement: eliminated steps, reduced errors, improved visibility
- Competitive intelligence: uncovered something the client didn't know
- Strategic decision support: informed a pricing, hiring, or go-to-market decision
- Client experience upgrade: onboarding, reporting, or communication got meaningfully better
- Process definition: helped client formalize something they hadn't defined (statuses, roles, rules, edge cases)
- Workflow design: designed how work should flow, not just automated what existed
- Data quality: made sure data was complete, correct, or successfully migrated
- Risk mitigation / compliance: protected revenue, made sure the client was audit-ready, met regulatory requirements
- Vendor replacement / cost elimination: replaced a paid tool with a better solution, eliminating subscription costs
- Single source of truth: consolidated scattered data (emails, PDFs, spreadsheets) into one queryable system
- Self-service enablement: shifted work from staff to end users who can now help themselves
- Scalability unlock: enabled the client to handle more volume without adding headcount
- Training / knowledge transfer: taught the client or team how to think about workflows, use tools, apply best practices
- Error prevention: built systems where certain errors literally cannot happen (validated fields, enforced sequences, automated calculations)
- Discovery / requirements clarity: helped the client figure out what they actually need when they didn't know what to ask for

## Where to Store MCS Records

Write MCS records to the MCS table in Airtable. Use `mcp__airtable__create_record` with:

- **Base:** `app8V74T72TT2SB0h`
- **Table:** MCS (`tbl4fNYChMVv8pyda`)

**Field name mapping:** The skill uses conceptual column names (Situation, Value) but the Airtable fields have different labels. Use this mapping:

| Skill concept | Airtable field name | Field ID |
|---|---|---|
| MCS ID | MCS ID | `fldF0MOaiyEFLTAxz` |
| MCS Headline | Headline | `fldoqgQNjGI45I37V` |
| Client Name | Client Name | `fldImm40HGVZ2HGay` |
| Client Role | Client Role | `fldHCAkp8xh5kf0bb` |
| Company Name | Company Name | `fld3AZm8ZfdNrh9wS` |
| Project Name | Project Name | `fldfGsRLU1ENqTXAm` |
| Industry | Industry (single-select) | `fldPENDING_Industry_(single-select)` (new; legacy free-text `fldoOn2odwxB0PEfG` kept intact) |
| Situation | **Problem** | `fld1RBmjZUzGNifdR` |
| Approach | Approach | `flddUNLOO62CCy79Y` |
| Analysis | Analysis | `fldKS4hw4scuocsyV` |
| Value | **Result 1** | `fld0bp8xzpAUrjsG7` |
| Result 2 | Result 2 (independent) | `fldPENDING_Result_2_(independent)` (new; legacy auto-mirror `fldHpvofpyDNf8sb4` kept intact) |
| Date Completed | Date Completed | `fldb3nmqVhKarB0PS` |
| Data Confidence | Data Confidence | `fldsTTy19IdaF3lgd` |
| Primary Tag | Primary Tag | `fldVPWOnp1BCmIinL` |
| Secondary Tag | Secondary Tag | `fldL421iu7xfnIFTh` |
| Est. Hours Recovered/Week | Est. Hours Recovered/Week | `fld4qZOrUyIDZRW8u` |
| Hourly Rate Assumption | Hourly Rate Assumption | `fldzZ06rEoLrQbMaw` |
| Est. Annual Dollar Value | Est. Annual Dollar Value | `fldo7oTt8lH4d6ed7` |
| Tech Stack | Tech Stack | `fldgwsnYXrwbyV66V` |
| Status | Status | `fldH66dHGIK2kmfPp` |
| Do Not Contact | Do Not Contact | `fldyoQYs9ZNFiZUM0` |
| Approved Date | Approved Date | (TBD, needs to be created) |
| Last Outreach Date | Last Outreach Date | (TBD, needs to be created) |
| Result 1 Icon | Result 1 Icon | `fldFccMBzWxY1u0C7` |
| Result 2 Icon | Result 2 Icon | `flddeJvoeH4XcSfez` |
| Engineer | Engineer | `fldPENDING_Engineer` |
| Build Time | Build Time | `fldPENDING_Build_Time` |
| Highlight (Human) | Highlight (Human) | `fldijTkoO3K2bSHpk` |
| Accents (Patterns) | Accents (Patterns) | `fldcDwADWdlL63AXv` |

Always set Client Name, Client Role, Company Name, Status, and visual assets when creating a record.

**Status values:**
- `"Completed"` — work is done and confirmed
- `"Queued"` — work is planned/in-progress, not yet finished

**Do Not Contact** (`fldyoQYs9ZNFiZUM0`): checkbox. Set to true to prevent a project's queued MCS from being used in outreach. Default: false (unchecked).

**AI agent fields — do NOT write to these.** The MCS table has Airtable AI agents that auto-generate compressed versions of content after record creation:
- Headline - AI Revised (`fldNlrtUT6OE3vChX`)
- Problem - AI Revised (`fldqt82z6ZPNiRHxG`)
- Approach - AI Revised (`fld8CPcEa5JTErREW`)
- Result 1 - AI Revised (`fldLKAR8KPH9tVH4E`)
- Result 2 (`fldHpvofpyDNf8sb4`) — auto-mirrors Result 1
- Character count formula fields (multiple)

These agents compress content to fit slide layouts. Write concise headlines and blurbs that work well when further shortened.

## Visual Assets

Each MCS record links to visual assets from the **MCS Assets** table (`tblF3r40XrSfirC38`, same base `app8V74T72TT2SB0h`). These assets display on Softr cards and are used for automated slide generation.

**Four asset slots per MCS record:**

| Slot | Field ID | Purpose |
|---|---|---|
| Result 1 Icon | `fldFccMBzWxY1u0C7` | Doodle icon for the primary outcome |
| Result 2 Icon | `flddeJvoeH4XcSfez` | Doodle icon for the secondary outcome |
| Highlight (Human) | `fldijTkoO3K2bSHpk` | Character illustration |
| Accents (Patterns) | `fldcDwADWdlL63AXv` | Decorative geometric shape |

**Available assets:**

| Record ID | Name | Type | Use for |
|---|---|---|---|
| `recYWlwjZmUqhvj47` | Target | Results | Process/visibility/strategic wins |
| `recluDuWe0Cco8T8D` | Money | Results | Cost/time recovery wins |
| `rec9EAml1NvaXzQPO` | Woman Pointing | Highlight | Alternate with Man Pointing |
| `recXYJVpGuM9yxiZh` | Man Pointing | Highlight | Alternate with Woman Pointing |
| `recI4Zwklqr37aNHH` | Red Circle | Accent | Position 1 |
| `recidnRUBWLU5C5w0` | Blue Circle | Accent | Position 2 |
| `rec2gSbYGKoYvKdiX` | Blue Triangle | Accent | Position 3 |

**Assignment rules:**
- **Result 1 Icon:** If the secondary tag is Time Recovery, Cost Avoidance, or Cost Elimination, use Money (`recluDuWe0Cco8T8D`). Otherwise use Target (`recYWlwjZmUqhvj47`).
- **Result 2 Icon:** Use whichever Results asset was NOT used for Result 1.
- **Highlight (Human):** Alternate between Woman Pointing and Man Pointing across records.
- **Accents (Patterns):** Rotate through the 3 accent assets.
- **Link format:** Pass as a record ID array, e.g. `"fldFccMBzWxY1u0C7": ["recYWlwjZmUqhvj47"]`

**Do NOT write to** lookup fields (`fldNOHFEYlLbwxQqB`, `fldzW9jiec6j2D3se`, `fldzlWDs97yH59PIW`, `fldyJ66wlvEHLn0ul`, `fldpUITTi9QS95Cml`) — these auto-populate from the linked records.

## Duplicate Prevention

Before creating any new MCS record, check the existing MCS table for duplicates. Use `mcp__airtable__search_records` or `mcp__airtable__list_records` on base `app8V74T72TT2SB0h`, table `tbl4fNYChMVv8pyda` to pull existing records and compare:

1. **Match on Project Name + Company Name.** If the same project name and company already exist, do not create a new record. Instead, flag it to the user as a potential duplicate.
2. **Headline similarity is a secondary human check.** When a Project Name + Company Name match is found, present both headlines to the user and ask whether to skip, merge, or create as new. Do not auto-match on headline text alone.
3. **Match on MCS ID.** Never reuse an MCS ID. Query the highest existing MCS ID and increment from there.

**Queued-to-Completed upgrades:** If an existing Queued record matches a new Completed candidate (same project, same pain point), **update** the existing record instead of creating a new one:
- Flip Status from "Queued" to "Completed"
- Rewrite Approach in past tense
- Fill in Analysis with confirmed metric
- Rewrite Result 1 (Value) with confirmed outcome
- Set Date Completed
- Update Data Confidence (usually from Estimated to High)
- Use `mcp__airtable__update_records` for upgrades, not create

Never create a Completed duplicate of a Queued record.

When in doubt, present the potential duplicate to the user and ask whether to skip, merge, or create as new.

## Output: Raw Data Capture Table

For each MCS candidate identified, fill out every field:

| Field | Description |
|---|---|
| Client Name | Contact person's name (e.g. "Janine Mothershed") |
| Client Role | Contact person's role (e.g. "CEO") |
| Company Name | Client company name (e.g. "Coding Clarified") |
| Project Name | Internal name for the deliverable |
| Industry | Comma-separated list of industries the MCS could apply to. Be generous — include the client's primary industry plus any adjacent industries where the same win would resonate (e.g. "Education, Workforce Development, Nonprofit") |
| MCS Headline | A plain, descriptive statement of the client's pain point. No names, no metrics, no action verbs — just what the client was worried about. Keep under 80 characters when possible — the AI agent will compress further. |
| Situation (Problem) | 2-3 sentences, the pain before you arrived. Same tense for both Completed and Queued — the pain exists/existed. |
| Approach | 2-3 sentences. **Completed:** past tense ("Built...", "Replaced..."). **Queued:** future tense ("Will build...", "Plan to replace..."). |
| Analysis | 2-3 sentences. **Completed:** past tense with metric. Vary language — don't always say "95%+ reliability." Use "without error from day one," "no data loss during migration," "adopted within the first week." **Queued:** "Pending completion." |
| Value (Result 1) | **Completed:** Quantified outcome with positive language. Always include est. hours/week and est. annual dollar value. Use "recovered," "redirected," "gained," "freed" — never "eliminate." **Queued:** "Expected to recover ~X hrs/week (~$Y/yr at $Z/hr)." |
| Status | "Completed" or "Queued" |
| Date Completed | When deliverable was finished/adopted. **Blank for Queued.** |
| Data Confidence | High / Medium / Estimated. **Queued records are generally "Estimated."** |
| MCS ID | MCS-YYYY-### |
| Primary Tag | What you built/delivered (see Tagging section) |
| Secondary Tag | What they got (see Tagging section) |
| Tech Stack | Comma-separated list of tools used (e.g. "Airtable, QuickBooks, Fillout") |
| Visual Assets | Assign all 4 slots (see Visual Assets section) |

**Always fill in ROI fields for every MCS record:**
- Est. hours recovered/week
- Hourly rate assumption
- Est. annual dollar value (Hours/Week x 52 x Hourly Rate)

For Queued records, use projected estimates and mark Data Confidence as "Estimated."

**Data Confidence targets: at least 80% of MCS records should be High.**

Mark Data Confidence as **High** when:
- The transcript cites specific hours, dollars, or percentages
- The transcript describes a clear before/after state where the time savings can be reasonably inferred (e.g., "staff used to do X manually, now it's automated" — even without an exact hour count, if the task is well-understood, mark High)
- The win is directly observable and confirmed by the client (e.g., "this is working," "we're using it every day")
- You can calculate ROI from context clues in the transcript with reasonable confidence

Mark Data Confidence as **Medium** when:
- Time savings are mentioned but vague ("saves a lot of time") with no way to anchor an estimate
- The win is in progress or partially adopted

Mark Data Confidence as **Estimated** only when:
- No time or cost data exists in the transcript and the ROI is a rough projection based on general assumptions
- The record is Queued (work not yet completed)

Use the Time to Money Cheat Sheet (see `references/time-to-money.md`) to calculate dollar values whenever hours are known or reasonably inferred.

In the rare case (less than 1% of records) where no reasonable estimate is possible, leave the ROI fields blank and write a memo in the Value column explaining why an estimate could not be made.

## Headline Rules

The headline is the client's pain point stated plainly and descriptively. Not what you built, not the outcome, not a marketing tagline. See `references/headline-guide.md` for full examples.

**How to write a headline:**
1. Ask: what was the client's concern before you showed up?
2. Write a clear, descriptive sentence stating that concern
3. No specific names — use roles (CEO, staff, team) instead
4. Be descriptive, not snarky or vague — the reader should understand the problem immediately
5. No metrics in headlines — those belong in the Value column
6. Keep under 80 characters when possible — the AI agent compresses to ~50 chars

Bad to Good:
- Office Automation Solution -> Staff is spending the entire week on admin tasks that don't require judgment.
- CRM Integration Project -> The same data has to be typed into two different systems every time.

## Four Columns

Each column: 2-3 sentences max. Never use specific people's names (Janine, Cassandra, Jay, etc.) in Situation, Approach, Analysis, or Value. Use "client" or "staff" instead. Names belong only in the Client Name field.

### Completed MCS (past tense)

| Column | What to Write | Example |
|---|---|---|
| Situation (Problem) | The pain before you arrived. What problem did the client face? | "Client spending 24 hrs/wk on manual admin that didn't require human judgment." |
| Approach | What you actually did. Method, tool, or strategy. | "Built custom automation to handle admin workflow without intervention." |
| Analysis | What you confirmed, written in past tense as though it's concluded. Always include a metric. | "Automation handled tasks at 95%+ reliability. Adopted within the first week with no training required." |
| Value (Result 1) | The quantified outcome. Always include est. hours/week recovered and est. annual dollar value. Use positive language. | "~5 hrs/week recovered (~$9,100/yr at $35/hr). Consistent follow-up now happens automatically." |

### Queued MCS (future tense)

| Column | What to Write | Example |
|---|---|---|
| Situation (Problem) | The pain exists now — same as Completed. | "Each estimate requires hours of manual re-entry from PDF to project management system." |
| Approach | What you will do. Future tense. | "Will transfer automation ownership and integrate Google Drive folder monitoring for automatic estimate parsing." |
| Analysis | Pending. | "Pending completion." |
| Value (Result 1) | Projected outcome. Use "Expected to recover..." | "Expected to recover ~3 hrs/week (~$6,240/yr at $40/hr). Will enable hands-off estimate processing." |

## Tagging System

1 primary + 1 secondary per MCS.

**Primary, What You Built/Delivered:**
Process Automation, Data Entry Automation, Reporting Automation, Integration, Workflow Orchestration, Client Experience, Workflow Design, Process Definition, Data Migration, Data Integrity, Executive Coaching, Vendor Replacement, Self-Service Enablement, Error Prevention, Training / Knowledge Transfer, Discovery / Requirements Clarity

**Secondary, What They Got:**
Time Recovery, Error Reduction, Visibility, Scalability, Cost Avoidance, Speed, Strategic Clarity, Compliance / Risk Mitigation, Cost Elimination, Data Consolidation, Self-Service, Capacity Without Headcount, Knowledge / Capability, Error Prevention

## Engineer Review

After MCS candidates are created, engineers review their queued records:

1. Engineer reviews queued MCS candidates for their projects
2. Engineer marks each as: **Completed** (done — trigger Queued-to-Completed upgrade) or keeps as **Queued**. Approving as Queued sets the Approved Date field; the 30-day outreach clock starts from this date, not record creation.
3. Engineer can flag a project as **Do Not Contact** — this prevents that project's queued MCS from being used in outreach
4. Present candidates to the engineer in a reviewable table format showing: MCS ID, Headline, Status, Company, Projected Value

## Automated Outreach (Revenue Recovery)

**Trigger:** Queued MCS record idle 30+ days AND client has remaining hours on their engagement. Monthly scan or on-demand.

1. Query MCS table for **Queued** records where Do Not Contact is false
2. Filter for records created 30+ days ago that are still Queued
3. Cross-reference remaining hours on the project (from Projects & Tasks base, `appQAdxI2hDNJj1g5`)
4. Skip clients with zero remaining hours
5. Group qualifying records by client/company
6. Generate personalized outreach email — short (~3-5 sentences), references the specific conversation by name, future-tense throughout, no sales pitch. Pattern: opener referencing the past conversation → the queued win in plain language → "you could recover ~N hrs/week" with the actual number → soft close ("want me to set this up?")
7. Language pulls directly from the Queued MCS fields — future tense throughout: "You could recover ~3 hrs/week," "expected to save," "here's what we discussed building with your remaining time"
8. Sender: generic XRAY address (projects@xray.tech or similar)
9. Route responses: TBD (downstream automation)

The outreach is not a cold pitch. Every Queued MCS references a specific conversation the client already had with their engineer — work they already agreed to. The email just reminds them it's still available.

## Input/Output Examples

### Completed Example

**Input (transcript excerpt):**
> Rachael: So the inactivity emails are all live now, 7 day, 14, 21, 30, 45, and 60 days. When a student hasn't logged into Blackboard for that period, they automatically get an email. Before this, Janine's team was manually checking who hadn't logged in and sending individual emails, which was taking about 5 hours a week.

**Output (MCS record):**

| Field | Value |
|---|---|
| Client Name | Janine Mothershed |
| Client Role | CEO |
| Company Name | Coding Clarified |
| Project Name | Student Inactivity Email Automation |
| Industry | Education, Workforce Development, Nonprofit |
| MCS Headline | Students are going inactive and nobody is following up consistently. |
| Situation (Problem) | Staff manually checked Blackboard login data to identify inactive students, then individually composed and sent follow-up emails. This process consumed approximately 5 hours per week and was inconsistently executed. |
| Approach | Built a 6-tier automated inactivity email sequence (7, 14, 21, 30, 45, and 60 days) triggered by Blackboard login activity, removing staff from the follow-up workflow entirely. |
| Analysis | All six inactivity tiers operated at 95%+ reliability from day one. Staff were fully removed from the follow-up workflow with no training required. Built-in logic prevented duplicate emails across milestone tiers. |
| Value (Result 1) | ~5 hrs/week recovered (~$9,100/yr at $35/hr). Consistent, timely student follow-up now happens automatically, improving retention outreach that previously fell through the cracks. |
| Status | Completed |
| Date Completed | March 2026 |
| Data Confidence | High |
| MCS ID | MCS-2026-005 |
| Primary Tag | Process Automation |
| Secondary Tag | Time Recovery |
| Tech Stack | Airtable, Blackboard |
| Est. hours recovered/week | 5 |
| Hourly rate assumption | $35/hr |
| Est. annual dollar value | ~$9,100 |
| Result 1 Icon | Money (`recluDuWe0Cco8T8D`) |
| Result 2 Icon | Target (`recYWlwjZmUqhvj47`) |
| Highlight (Human) | Woman Pointing (`rec9EAml1NvaXzQPO`) |
| Accents (Patterns) | Red Circle (`recI4Zwklqr37aNHH`) |

### Queued Example

**Input (email excerpt):**
> Rachael to Kris: I'd like to transfer the n8n automation ownership to your team and set up a Google Drive folder integration so the PDF estimate parser can run automatically when new estimates land in a shared folder.

**Output (MCS record):**

| Field | Value |
|---|---|
| Client Name | Kris Wade |
| Client Role | CFO |
| Company Name | Maas Verde |
| Project Name | n8n Automation Ownership Transfer + Google Drive Integration |
| Industry | Landscape, Construction, Restoration |
| MCS Headline | Estimate parsing still requires manual file handoff to trigger. |
| Situation (Problem) | The PDF estimate parser runs on PythonAnywhere but requires manual file placement. No automated trigger exists for when new estimates arrive, and the automation credentials are tied to a single engineer rather than the client's team. |
| Approach | Will transfer n8n automation ownership to the client's team and integrate Google Drive folder monitoring so new estimates automatically trigger the parsing pipeline. |
| Analysis | Pending completion. |
| Value (Result 1) | Expected to recover ~3 hrs/week (~$6,240/yr at $40/hr). Will enable hands-off estimate processing from PDF drop to structured data output. |
| Status | Queued |
| Date Completed | |
| Data Confidence | Estimated |
| MCS ID | MCS-2026-040 |
| Primary Tag | Integration |
| Secondary Tag | Time Recovery |
| Tech Stack | n8n, Google Drive, PythonAnywhere |
| Est. hours recovered/week | 3 |
| Hourly rate assumption | $40/hr |
| Est. annual dollar value | ~$6,240 |
| Result 1 Icon | Money (`recluDuWe0Cco8T8D`) |
| Result 2 Icon | Target (`recYWlwjZmUqhvj47`) |
| Highlight (Human) | Man Pointing (`recXYJVpGuM9yxiZh`) |
| Accents (Patterns) | Blue Circle (`recidnRUBWLU5C5w0`) |
