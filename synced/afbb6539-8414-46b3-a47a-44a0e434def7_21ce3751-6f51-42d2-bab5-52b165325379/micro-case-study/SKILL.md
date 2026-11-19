---
name: micro-case-study
description: Extract micro-case study (MCS) candidates from Zoom call transcripts and supplemental data. Mine client call transcripts for the smallest atomic wins (one automation, one form, one integration, one consulting insight) and produce structured MCS records. Use when asked to create micro-case studies, find client wins, mine transcripts for case studies, identify MCS candidates, or build the MCS library. Triggers on "micro-case study", "MCS", "case study", "mine transcripts", "find wins", "client wins from transcripts".
---

# Micro Case Study

## Overview

A Micro Case Study (MCS) captures the smallest atomic unit of client value delivered: one automation, one form, one integration, one fix, one consulting insight. Not a whole project. The smallest thing that brought the client value.

An MCS answers three questions: What was the challenge? What did you do? How was it successful?

The format is designed to begin a conversation, not end one. If someone's intrigued, they'll ask for more.

## Workflow

1. Pull transcripts from the Debrief Recordings table in Airtable
2. Scan each transcript for completed wins (technical and consulting)
3. Break work into atomic wins, the smallest deliverable that brought value
4. Fill out the raw data capture table for each MCS candidate
5. Calculate ROI for time/cost recovery wins using the Time to Money Cheat Sheet (see `references/time-to-money.md`)
6. Write the headline using the formula; it describes the CLIENT's win, not your work
7. Assign tags, 1 primary + 1 secondary per MCS

## Where the Transcripts Live

Pull transcripts from the Debrief Recordings table in Airtable. Use the `mcp__airtable__list_records` tool with the following parameters:

- **Base:** Projects & Tasks at XRAY (`appQAdxI2hDNJj1g5`)
- **Table:** Debrief Recordings (`tblYLGhD3Ii7EkGZY`)
- **View:** rachaelView (`viwaAHlqwFgrX5vbX`)
- **Transcript fields:** Zoom Transcript 1 (`fldOxrt82yRzwVSmE`), Zoom Transcript 2 (`fldcr5lVB3KILI5hx`)
- **Supplemental fields:** AI Summary (`fldf7qTmupFxeA1BU`), Editable Title for Softr (`fldQDtrKwJ0YfIhLg`), Start Time (`fldR2IUUk260Eduzg`), XRay's Client (`fld9YZme9QfpVSYgm`)

To search for specific meetings, use `mcp__airtable__search_records` with the same base and table IDs. To get a single record by ID, use `mcp__airtable__get_record`.

## XRAY's Two Layers of Value

XRAY delivers value in two layers that often happen together. Both produce standalone MCS candidates.

**Technical:** automations, integrations, forms, dashboards, data migrations

**Consulting:** workflow design, process definition, process refinement, executive coaching, business best practices, data integrity

"Helped client define 6 enrollment statuses that had never been formalized" is its own MCS, separate from the automation that uses those statuses. When you automate a process, you're also refining it; the client gets two wins: the process goes from manual to automatic AND the process itself gets better.

## How to Identify MCS Candidates

Scan transcripts for these signals:

**Technical wins:**
- Completion language: "I built...", "I set up...", "it's live now...", "that's running...", "we deployed..."
- Client confirmation of value: "this is working", "this saves us...", "we love this"
- Before/after states: "used to take X hours", "now it takes Y minutes"
- Specific metrics: hours, dollars, percentages, error counts
- Named tools/deliverables: a specific form, automation, integration, report, dashboard

**Consulting wins:**
- Process definition: "we figured out they didn't have a definition for...", "they hadn't thought about...", "we helped them define..."
- Process refinement: "we realized they could skip...", "we streamlined...", "we eliminated three steps..."
- Workflow design: "we designed a new flow for...", "we mapped out how..."
- Executive coaching: "we helped them see...", "they realized they needed to...", "we showed them the best practice is..."
- Data integrity: "we cleaned up...", "we found duplicates...", "the data was incomplete so we..."
- Data migration: "we moved everything from...", "we migrated..."

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

Write completed MCS records to the MCS table in Airtable. Use `mcp__airtable__create_record` with:

- **Base:** `app8V74T72TT2SB0h`
- **Table:** MCS (`tbl4fNYChMVv8pyda`)

Field IDs for record creation:
- MCS ID: `fldF0MOaiyEFLTAxz`
- MCS Headline: `fldoqgQNjGI45I37V`
- Client Name: `fldImm40HGVZ2HGay` (person's name only, e.g. "Janine Mothershed")
- Client Role: `fldHCAkp8xh5kf0bb` (e.g. "CEO", "Publisher", "CFO")
- Company Name: `fld3AZm8ZfdNrh9wS` (client company name, e.g. "Coding Clarified")
- Project Name: `fldfGsRLU1ENqTXAm`
- Industry: `fldoOn2odwxB0PEfG`
- Situation: `fld1RBmjZUzGNifdR`
- Approach: `flddUNLOO62CCy79Y`
- Analysis: `fldKS4hw4scuocsyV`
- Value: `fld0bp8xzpAUrjsG7`
- Date Completed: `fldb3nmqVhKarB0PS`
- Data Confidence: `fldsTTy19IdaF3lgd`
- Primary Tag: `fldVPWOnp1BCmIinL`
- Secondary Tag: `fldL421iu7xfnIFTh`
- Est. Hours Recovered/Week: `fld4qZOrUyIDZRW8u`
- Hourly Rate Assumption: `fldzZ06rEoLrQbMaw`
- Est. Annual Dollar Value: `fldo7oTt8lH4d6ed7`
- Tech Stack: `fldgwsnYXrwbyV66V` (comma-separated list of tools used, e.g. "Airtable, QuickBooks, Fillout")

Always set Client Name, Client Role, and Company Name when creating a record.

## Duplicate Prevention

Before creating any new MCS record, check the existing MCS table for duplicates. Use `mcp__airtable__search_records` or `mcp__airtable__list_records` on base `app8V74T72TT2SB0h`, table `tbl4fNYChMVv8pyda` to pull existing records and compare:

1. **Match on Project Name + Company Name.** If the same project name and company already exist, do not create a new record. Instead, flag it to the user as a potential duplicate.
2. **Match on Headline similarity.** If a headline covers the same pain point as an existing record (even if worded differently), flag it before creating.
3. **Match on MCS ID.** Never reuse an MCS ID. Query the highest existing MCS ID and increment from there.

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
| MCS Headline | A plain, descriptive statement of the client's pain point. No names, no metrics, no action verbs — just what the client was worried about. |
| Situation | 2-3 sentences, the pain before you arrived |
| Approach | 2-3 sentences, what you actually did |
| Analysis | 2-3 sentences, written in past tense as concluded. Include a metric or concrete proof of success. Vary the language — don't always say "95%+ reliability." Use specifics like "without error from day one," "no data loss during migration," "adopted within the first week," "handled every edge case," "processed correctly across all [X] types." |
| Value | Quantified outcome with positive language. Always include est. hours/week and est. annual dollar value. Use "recovered," "redirected," "gained," "freed" — never "eliminate." |
| Date Completed | When deliverable was finished/adopted |
| Data Confidence | High / Medium / Estimated |
| MCS ID | MCS-YYYY-### |
| Primary Tag | What you built/delivered (see Tagging section) |
| Secondary Tag | What they got (see Tagging section) |
| Tech Stack | Comma-separated list of tools used (e.g. "Airtable, QuickBooks, Fillout") |

**Always fill in ROI fields for every MCS record:**
- Est. hours recovered/week
- Hourly rate assumption
- Est. annual dollar value (Hours/Week x 52 x Hourly Rate)

**Data Confidence targets: at least 80% of MCS records should be High.**

Mark Data Confidence as **High** when:
- The transcript cites specific hours, dollars, or percentages
- The transcript describes a clear before/after state where the time savings can be reasonably inferred (e.g., "staff used to do X manually, now it's automated" — even without an exact hour count, if the task is well-understood, mark High)
- The win is directly observable and confirmed by the client (e.g., "this is working," "we're using it every day")
- You can calculate ROI from context clues in the transcript with reasonable confidence (e.g., a manual task that takes a known amount of time is now automated)

Mark Data Confidence as **Medium** when:
- Time savings are mentioned but vague ("saves a lot of time") with no way to anchor an estimate
- The win is in progress or partially adopted

Mark Data Confidence as **Estimated** only when:
- No time or cost data exists in the transcript and the ROI is a rough projection based on general assumptions

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

Bad to Good:
- Office Automation Solution -> Staff is spending the entire week on admin tasks that don't require judgment.
- CRM Integration Project -> The same data has to be typed into two different systems every time.

## Four Columns

Each column: 2-3 sentences max. Never use specific people's names (Janine, Cassandra, Jay, etc.) in Situation, Approach, Analysis, or Value. Use "client" or "staff" instead. Names belong only in the Client Name field.

| Column | What to Write | Example |
|---|---|---|
| Situation | The pain before you arrived. What problem did the client face? | "Client spending 24 hrs/wk on manual admin that didn't require human judgment." |
| Approach | What you actually did. Method, tool, or strategy. | "Built custom automation to handle admin workflow without intervention." |
| Analysis | What you confirmed, written in past tense as though it's concluded. Always include a metric — if the solution is working, state >= 95% reliability. This column is used for marketing to potential clients. | "Automation handled tasks at 95%+ reliability. Adopted within the first week with no training required." |
| Value | The quantified outcome. Always include est. hours/week recovered and est. annual dollar value. Use positive language — show value gained, not just problems removed. Frame with success and forward momentum (e.g. "freed capacity for," "gained the ability to," "redirected time toward"). Never use "eliminate" — use "recovered," "redirected," "gained," "freed," "accelerated." | "~5 hrs/week recovered (~$9,100/yr at $35/hr). Consistent follow-up now happens automatically, improving retention outreach." |

## Tagging System

1 primary + 1 secondary per MCS.

**Primary, What You Built/Delivered:**
Process Automation, Data Entry Automation, Reporting Automation, Integration, Workflow Orchestration, Client Experience, Workflow Design, Process Definition, Data Migration, Data Integrity, Executive Coaching, Vendor Replacement, Self-Service Enablement, Error Prevention, Training / Knowledge Transfer, Discovery / Requirements Clarity

**Secondary, What They Got:**
Time Recovery, Error Reduction, Visibility, Scalability, Cost Avoidance, Speed, Strategic Clarity, Compliance / Risk Mitigation, Cost Elimination, Data Consolidation, Self-Service, Capacity Without Headcount, Knowledge / Capability, Error Prevention

## Input/Output Example

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
| Situation | Staff manually checked Blackboard login data to identify inactive students, then individually composed and sent follow-up emails. This process consumed approximately 5 hours per week and was inconsistently executed. |
| Approach | Built a 6-tier automated inactivity email sequence (7, 14, 21, 30, 45, and 60 days) triggered by Blackboard login activity, removing staff from the follow-up workflow entirely. |
| Analysis | All six inactivity tiers operated at 95%+ reliability from day one. Staff were fully removed from the follow-up workflow with no training required. Built-in logic prevented duplicate emails across milestone tiers. |
| Value | ~5 hrs/week recovered (~$9,100/yr at $35/hr). Consistent, timely student follow-up now happens automatically, improving retention outreach that previously fell through the cracks. |
| Date Completed | March 2026 |
| Data Confidence | High |
| MCS ID | MCS-2026-005 |
| Primary Tag | Process Automation |
| Secondary Tag | Time Recovery |
| Tech Stack | Airtable, Blackboard |
| Est. hours recovered/week | 5 |
| Hourly rate assumption | $35/hr |
| Est. annual dollar value | ~$9,100 |
