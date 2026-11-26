# Micro Case Study (MCS), Product Requirements Document

## Product Overview

The MCS system mines XRAY client call transcripts for the smallest atomic wins (one automation, one form, one integration, one consulting insight) and produces structured, visual case study records. Completed wins feed into automated slide generation and marketing. Queued wins, work that was discussed but not delivered yet, become revenue recovery candidates: when a client has remaining hours and hasn't reached out in 30+ days, the system generates a personalized outreach email showing what they could still get done and the projected value.

Product owner: Rachael Quisel
Content/design lead: Blair Ito
Status: Active, iterating

## Problem Statement

XRAY engineers deliver dozens of small wins on every client engagement (automations, integrations, process fixes, consulting insights), but none of it gets captured in a structured way. Without structured records, XRAY can't:
- Market specific capabilities to prospective clients
- Show existing clients the full value they've received
- Produce visual case study slides at scale

There's a second, revenue-side problem: clients routinely have one or two hours left on their engagement and just don't reach out. After 30 days of inactivity with remaining hours on the books, that work, and the revenue attached to it, quietly expires. Engineers discuss planned automations, integrations, and fixes on calls, but nobody tracks those conversations as actionable candidates. Without a system that captures queued work and flags stale remaining hours, XRAY has no way to say, "Hey, you still have time left; here's what we talked about doing with it, and here's the value it could deliver."

## Vision

Turn every engineer's client call into a library of atomic, visual case studies, and turn stale remaining hours into closed work.

1. Completed MCS records document delivered value for marketing and client retention ("Here's everything we did for you")
2. Queued MCS records capture planned/in-progress work that was discussed but hasn't happened yet; each one is a ready-made outreach candidate with projected ROI
3. Revenue recovery outreach: when a client has remaining hours and a Queued MCS sitting idle for 30+ days, the system generates a personalized email: "You could recover 3 hours a week; here's what we talked about building." Language shifts from past tense ("we recovered") to future tense ("you could recover"), so outreach reads as forward-looking and helpful, not salesy
4. Visual assets (icons, characters, accents) make each record slide-ready
5. AI agents compress content to fit slide layouts automatically
6. Full pipeline runs weekly with minimal human intervention

## Success Metrics

Marketing pipeline (Completed MCS):
- Library size: 50+ records by end of Q2 2026 (34 today)
- Data Confidence distribution: 80%+ of records rated High
- AI compression pass rate: headlines, problem, approach, result all fit slide character limits without manual editing
- Slide generation: Completed MCS records produce usable slides without manual layout work

Revenue recovery (Queued MCS):
- Queued capture rate: at least 1 Queued MCS identified per transcript batch that discusses planned work
- Outreach conversion: % of outreach emails that result in client re-engagement (target: track from day one, optimize after baseline)
- Revenue recovered: total hours re-engaged from Queued outreach ($ value = hours x hourly rate)
- Time to outreach: Queued MCS triggers outreach within 30 days of going idle, not 60 or 90

Operational health:
- Weekly mining runs execute on schedule (Tuesday) with no manual intervention
- Duplicate rate: <5% of new records flagged as duplicates after creation
- Engineer review turnaround: queued candidates reviewed within 1 week of creation

## Feature Prioritization

| Priority | Feature | Status | Depends on | Ship target |
|---|---|---|---|---|
| P0 | F1: Transcript Mining | Completed | none | Shipped |
| P0 | F5: Duplicate Prevention | Completed (in skill) | F1 | Shipped |
| P1 | F2: Queued Work Detection | Skill ready, no records yet | F1 | Next mining run |
| P1 | F3: Visual Asset Assignment | Completed (backfilled) | none | Shipped |
| P1 | F4: AI Content Compression | Live (Blair Ito) | F1 | Shipped |
| P2 | F6: Engineer Review | Not started | F2 | After first Queued batch |
| P2 | F7: Revenue Recovery Outreach | Not started | F2, F6 | After F6 validated |
| P3 | F8: Slide Generation Pipeline | In progress (Blair Ito) | F3, F4 | Tom's timeline |

Why this order: you can't do outreach (F7) without engineer review (F6), and you can't review without Queued records (F2). F2 is the gate; the first Tuesday mining run that produces Queued records unblocks everything downstream.

## Architecture

### Data Flow

```
LCE Call Transcripts (Zoom)
    |
    v
CRM Enriched Debriefs table (XR - LCE / XRAY Hourly base)
    |
    v
Claude Code skill: /micro-case-study
    |  - Mines transcripts for completed wins + queued work
    |  - Produces structured MCS records (Completed + Queued)
    |  - Assigns visual assets
    |  - Checks for duplicates / queued-to-completed upgrades
    v
MCS table (XRAY Content base)
    |  - AI agents auto-compress headlines, problem, approach, results
    |  - Character count formulas enforce length limits
    |  - Linked MCS Assets provide visual elements
    |
    +---> Completed MCS path:
    |       Google Sheets (slide template) --> Automated slide generation
    |           |
    |           v
    |       Softr portfolio / marketing
    |
    +---> Queued MCS path (revenue recovery):
            30+ days idle + remaining hours on project?
                |
                v
            Outreach email draft:
              "You could recover ~3 hrs/week; here's what
               we talked about building with your remaining time."
                |
                v
            Client re-engages --> Queued flips to Completed
```

### Airtable Schema

Base: XRAY Content (`appExample0000047`)

MCS Table (`tblExample0000061`)

| Field | Type | Field ID | Notes |
|---|---|---|---|
| MCS ID | singleLineText | `fldExample0000062` | Format: MCS-YYYY-### |
| Headline | singleLineText | `fldExample0000063` | Client pain stated plainly, <80 chars |
| Problem | multilineText | `fldExample0000053` | Skill calls this "Situation" |
| Approach | multilineText | `fldExample0000054` | Past tense (Completed) or future tense (Queued) |
| Analysis | multilineText | `fldExample0000055` | Metric-backed confirmation or "Pending completion." |
| Result 1 | multilineText | `fldExample0000056` | Skill calls this "Value"; quantified outcome |
| Client Name | singleLineText | `fldExample0000064` | Person's name |
| Client Role | singleLineText | `fldExample0000065` | e.g. CEO, CFO |
| Company Name | singleLineText | `fldExample0000066` | |
| Project Name | singleLineText | `fldExample0000052` | |
| Industry | singleLineText | `fldExample0000050` | Comma-separated |
| Tech Stack | singleLineText | `fldExample0000067` | Comma-separated tools |
| Status | singleSelect | `fldExample0000068` | Queued (yellow) / Completed (green) |
| Do Not Contact | checkbox | `fldExample0000069` | Prevents outreach for this project |
| Approved Date | singleLineText | (TBD, needs to be created) | Set when engineer approves Queued record; 30-day outreach clock starts here |
| Last Outreach Date | singleLineText | (TBD, needs to be created) | Set when record is included in an outreach email; used for dedup |
| Primary Tag | singleSelect | `fldExample0000070` | What you built |
| Secondary Tag | singleSelect | `fldExample0000071` | What they got |
| Date Completed | singleLineText | `fldExample0000057` | Blank for Queued. singleLineText (not date) because values are approximate, e.g. "March 2026" or "Q1 2026" |
| Data Confidence | singleSelect | `fldExample0000072` | High / Medium / Estimated |
| Est. Hours Recovered/Week | number | `fldExample0000073` | |
| Hourly Rate Assumption | currency | `fldExample0000074` | |
| Est. Annual Dollar Value | currency | `fldExample0000075` | |
| Result 1 Icon | multipleRecordLinks | `fldExample0000058` | Links to MCS Assets |
| Result 2 Icon | multipleRecordLinks | `fldExample0000059` | Links to MCS Assets |
| Highlight (Human) | multipleRecordLinks | `fldExample0000060` | Links to MCS Assets |
| Accents (Patterns) | multipleRecordLinks | `fldExample0000076` | Links to MCS Assets |
| Industry Tag | singleSelect | `fldExample0000077` | |
| Project Tags | multipleSelects | `fldExample0000078` | |

AI Agent Fields (auto-generated, do not write):
| Field | Type | Field ID | Purpose |
|---|---|---|---|
| Headline - AI Revised | aiText | `fldExample0000079` | Compressed headline, ~50 chars |
| Problem - AI Revised | aiText | `fldExample0000080` | Compressed situation blurb |
| Approach - AI Revised | aiText | `fldExample0000081` | Compressed approach |
| Result 1 - AI Revised | aiText | `fldExample0000082` | Compressed result |
| Result 2 | multilineText | `fldExample0000051` | Auto-mirrors Result 1; exists for the slide template which has two result columns. The skill does not write to this field. |
| Character count fields | formula | (multiple) | Track length per column |

MCS Assets Table (`tblExample0000083`)

| Field | Type | Field ID |
|---|---|---|
| Name | formula | `fldExample0000084` |
| Target Location | singleSelect | `fldExample0000085` |
| Asset | multipleAttachments | `fldExample0000086` |
| Accent Location (Pattern) | singleSelect | `fldExample0000087` |

Current assets:
| Record ID | Name | Type | Description |
|---|---|---|---|
| `recExample0000088` | Target | Results | Target/bullseye doodle |
| `recExample0000089` | Money | Results | Money/dollar doodle |
| `recExample0000090` | Woman Pointing | Highlight | Woman character |
| `recExample0000091` | Man Pointing | Highlight | Man character |
| `recExample0000092` | Red Circle | Accent | Position 1 |
| `recExample0000093` | Blue Circle | Accent | Position 2 |
| `recExample0000094` | Blue Triangle | Accent | Position 3 |

Transcript Source:
- Base: XR - LCE / XRAY Hourly (`appExample0000049`)
- Table: CRM Enriched Debriefs (`tblExample0000095`)
- Transcript field: Zoom Transcript 1 (`fldExample0000048`)

## Features

### F1: Transcript Mining (Completed)
- Pull all LCE transcripts from CRM Enriched Debriefs
- Scan for completed wins (technical and consulting)
- Break into atomic wins
- Produce structured MCS records with ROI calculations
- Write to Airtable MCS table

Acceptance criteria: Shipped. 34 records created. Validated by Rachael.

### F2: Queued Work Detection (New)
- Detect future/planned/in-progress language in transcripts
- Create Queued MCS records with future-tense columns
- Projected ROI with "Estimated" confidence; language shifts from "recovered" to "could recover"
- Queued records become outreach candidates when clients have remaining hours and 30+ days of inactivity
- Each Queued MCS is a ready-made outreach candidate: specific work the client already agreed to, with projected value

Acceptance criteria:
- [ ] Skill identifies at least one Queued candidate from a transcript that discusses planned work
- [ ] Queued record uses future tense in Approach and Result 1
- [ ] Analysis field reads "Pending completion."
- [ ] Data Confidence set to "Estimated"
- [ ] Date Completed is blank
- [ ] ROI fields filled with projected estimates
- [ ] Status field set to "Queued"

### F3: Visual Asset Assignment (New)
- Each MCS record gets 4 visual assets: Result 1 Icon, Result 2 Icon, Highlight (Human), Accents (Patterns)
- Assets assigned based on secondary tag (Money for cost/time recovery, Target for everything else)
- Highlight characters alternate; accents rotate
- All 34 existing records backfilled as of 2026-04-06

### F4: AI Content Compression (Blair Ito)
- Airtable AI agents auto-compress headlines, problem, approach, results
- Character count formulas enforce length limits
- Conditional AI fields fire when content exceeds thresholds (e.g., headline > 50 chars)
- Skill writes concise content that compresses well

### F5: Duplicate Prevention + Queued-to-Completed Upgrades
- Match on Project Name + Company Name
- Headline similarity is a secondary human check: when a Project Name + Company Name match is found, the skill presents both headlines to the user and asks whether to skip, merge, or create as new
- MCS IDs are never reused
- Queued-to-Completed: update existing record, don't create a duplicate

Acceptance criteria:
- [ ] Skill queries existing records before creating new ones
- [ ] Duplicate flagged to user when Project Name + Company Name match
- [ ] Queued record updated in place (not duplicated) when same work is confirmed as Completed
- [ ] Upgraded record has past-tense Approach, confirmed Analysis, filled Date Completed
- [ ] MCS ID increments from highest existing ID

### F6: Engineer Review (New)

Engineers review queued MCS candidates before anything goes to outreach. This is the human-in-the-loop gate; no Queued record reaches a client without an engineer signing off.

Workflow:
1. After a mining run produces Queued records, the assigned engineer gets a reviewable list (Airtable view filtered to Status = Queued, grouped by Company)
2. For each Queued MCS, the engineer picks one of three actions:
   - Approve as Queued: record stays Queued and becomes eligible for outreach after 30 days idle
   - Mark Completed: engineer confirms the work is done; triggers Queued-to-Completed upgrade (tense rewrite, Date Completed filled, Data Confidence updated)
   - Flag Do Not Contact: checks the DNC box; this project's Queued records are excluded from outreach going forward (e.g., client relationship is sensitive, work was descoped, client already knows)
3. Unreviewed records do not trigger outreach. The 30-day idle clock starts from Approved Date (set on engineer approval), not from record creation.
4. Rachael assigns the reviewing engineer and sends a Slack message linking to the Engineer Review Airtable view. For now, Rachael is the sole reviewer; as more engineers' transcripts are mined, the engineer whose call produced the Queued record reviews it.

Acceptance criteria:
- [ ] Airtable view exists: "Engineer Review" filtered to Status = Queued, sorted by Company Name
- [ ] Engineer can update Status field (Queued -> Completed) in Airtable
- [ ] Engineer can check Do Not Contact box in Airtable
- [ ] Queued-to-Completed upgrade rewrites Approach, Analysis, and Result 1 in past tense (skill handles this on next run, or manually)
- [ ] Unreviewed Queued records (created <7 days ago with no engineer action) are excluded from outreach queries
- [ ] Approved Date is set when engineer approves a Queued record
- [ ] After engineer marks Completed, the record shows up in the Completed MCS pipeline (slides, marketing)

### F7: Automated Outreach / Revenue Recovery (New)

The outreach system turns Queued MCS records into personalized client emails. Every email references a specific conversation the client already had with their engineer; this is not a cold pitch.

Trigger conditions (all must be true):
1. Queued MCS record exists and was approved by engineer (F6)
2. Record's Approved Date is 30+ days ago
3. Do Not Contact is false
4. Client has remaining hours on their engagement (cross-referenced from Projects & Tasks base)

Workflow:
1. Monthly scan (or on-demand): query MCS table for records matching all trigger conditions
2. Group qualifying records by client/company; one email per client, even if they have multiple Queued MCS records
3. Pull remaining hours from Projects & Tasks base (`appExample0000004`)
4. Generate email draft from `references/outreach-template.md` with:
   - Client name and company
   - Remaining hours available
   - List of Queued MCS records: headline + projected value for each
   - Combined projected value across all Queued items
5. Language uses future tense throughout: "you could recover," "expected to save," "here's what we discussed building with your remaining time"
6. Tone: helpful, not salesy; a reminder, not a pitch
7. Sender: generic XRAY address (person15@example.com or similar)
8. Email is generated as a draft for Rachael to review before sending (no auto-send in v1)

After outreach:
- Client re-engages -> engineer completes the work -> Queued flips to Completed (tense rewrites automatically)
- Client doesn't respond -> no follow-up in v1 (reconsider cadence after baseline data)
- Client declines -> engineer flags Do Not Contact

Acceptance criteria:
- [ ] Query filters correctly: Queued + approved + 30+ days idle + DNC false + remaining hours > 0
- [ ] Records grouped by client; one email per client, not per MCS
- [ ] Email draft includes all Queued MCS for that client with individual and combined projected value
- [ ] Email draft uses future tense throughout (no past-tense language)
- [ ] Email is generated as a reviewable draft, not auto-sent
- [ ] Remaining hours pulled from Projects & Tasks base accurately
- [ ] Last Outreach Date set on each record included in an outreach email; outreach query skips records emailed in the current month

### F8: Slide Generation Pipeline (Blair Ito)
- MCS records feed into Google Sheets template
- AI-compressed fields + visual assets = slide-ready data
- Automated slide generation (in progress)

## Tense Rules

| Column | Completed | Queued |
|---|---|---|
| Problem | Pain before you arrived (past/present) | Same; the pain still exists |
| Approach | Past tense: "Built..." | Future: "Will build..." |
| Analysis | Past tense with metric | "Pending completion." |
| Result 1 | "~5 hrs/week recovered..." | "Expected to recover ~5 hrs/week..." |

The tense shift is the outreach engine. A Completed MCS says "we recovered 3 hours a week." A Queued MCS says "you could recover 3 hours a week." When the outreach email fires, it pulls Queued language directly; the future tense makes it a natural, forward-looking suggestion rather than a sales pitch.

## Content Guidelines

- Anonymization: no client names in Problem, Approach, Analysis, Result 1. Use roles.
- Headline: client's pain stated plainly. No names, metrics, or action verbs. <80 chars.
- ROI: hours/week, hourly rate, and annual value are filled in on every record. Use Time to Money Cheat Sheet.
- Data Confidence: 80%+ of records should be High. Queued = Estimated.
- Tags: 1 primary (what you built) + 1 secondary (what they got) per MCS.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Engineers don't review Queued records in time | Outreach delayed or stale | Weekly Slack reminder; keep review simple (3 actions in Airtable, no separate tool) |
| Outreach emails feel salesy or generic | Client trust eroded | Every email references a specific conversation; human review before send (v1 is drafts only); future tense keeps it forward-looking |
| Remaining hours data is stale or inaccurate | Outreach sent to clients with no hours left | Cross-reference at email generation time, not at record creation; skip clients with 0 remaining hours |
| Queued MCS content too vague to be useful in outreach | Low conversion | Skill enforces specific projected ROI and concrete approach description; engineer review catches vague records |
| Duplicate MCS records erode trust in the library | Marketing uses wrong data; slides have repeats | Duplicate prevention in skill (F5); engineer review catches near-misses |
| AI compression changes meaning | Slide says something inaccurate | Character count thresholds trigger AI redrafting only when needed; original fields are preserved as source of truth |

## Current State (2026-04-06)

- 34 MCS records in Airtable (all Completed, no Queued yet)
- All 34 records have visual assets assigned (backfilled today)
- AI agent fields active for headline, problem, approach, result compression
- Character count + conditional AI logic live (Blair Ito)
- Skill updated with queued detection, asset assignment, engineer review, outreach sections
- Outreach template created
- Slide generation pipeline in progress (Blair Ito + Google Sheets)

## Open Items

Blocking next milestone (first Queued batch):
- [ ] Run first mining batch with Queued detection enabled, Rachael, next Tuesday run
- [ ] Create "Engineer Review" Airtable view (Status = Queued, grouped by Company), Rachael
- [ ] First Queued MCS: Maas Verde n8n automation transfer, Rachael (test case)

Blocking outreach (F7):
- [ ] Define outreach sender address and response routing, Rachael
- [ ] Test outreach email generation with queued records, Rachael (after first Queued batch)
- [ ] Create Approved Date field in Airtable (blocks F6/F7), Rachael
- [ ] Create Last Outreach Date field in Airtable (blocks F7), Rachael

Content/design (Blair Ito):
- [ ] More accent placeholder images needed for positions 4-6
- [ ] Google Sheets slide template tweaks
- [ ] Run AI rephrasing on all existing records

Operational:
- [ ] Schedule weekly Tuesday MCS mining run (existing `run-mcs-skill` scheduled task), Rachael
- [ ] Validate Industry Tag and Project Tags values across all 34 records, Rachael

## Related Files

- Skill: `~/.claude/skills/micro-case-study/SKILL.md`
- References:
  - `~/.claude/skills/micro-case-study/references/mcs-examples.md`
  - `~/.claude/skills/micro-case-study/references/headline-guide.md`
  - `~/.claude/skills/micro-case-study/references/time-to-money.md`
  - `~/.claude/skills/micro-case-study/references/outreach-template.md`
- Scheduled task: `/Users/rachaelquisel/Claude-Work/PROJECTS/Scheduled/run-mcs-skill/SKILL.md`
