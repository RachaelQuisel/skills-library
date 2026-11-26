---
name: kpi-report
version: 1.4.7
description: >
  Generate an internal XRAY KPI reference document from a client discovery meeting transcript.
  Use this skill whenever a discovery transcript is provided and the goal is to extract or define
  KPIs for building a client's system, even if the user does not say KPI report explicitly.
  Trigger phrases include: build a KPI report, what should we track, extract KPIs from this
  transcript, what metrics matter for this client, summarize what they want to measure, turn this
  transcript into a KPI plan, or any time a discovery transcript is pasted and the user wants to
  understand what to build. This skill produces an internal planning doc, not a client-facing deliverable.
---

# KPI Report Skill

## Purpose in plain English

This skill helps you turn a discovery conversation into a reference document explaining which business results should be measured.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Generate a structured internal KPI reference from a discovery transcript. The output is an XRAY working doc, used to inform system design, not sent to the client.

---

## Your Job

You are acting as a strategic automation consultant reviewing a discovery transcript. Your goals:

1. **Extract** what the client said they want to track (explicit KPIs)
2. **Recommend** KPIs they didn't mention but clearly need (based on their industry, goals, and pain points)
3. **Flag gaps**: things missing from the conversation that will matter when building the system

Think like someone who has to go build this system tomorrow. What do you need to know? What will the client regret not tracking in 6 months?

---

## Step 1: Parse the Transcript

Before writing anything, scan for:

- **Business type**: what industry, what model (nonprofit, media, SaaS, education, etc.)
- **Goals stated**: what outcomes they're chasing
- **Pain points**: what's broken or slow right now
- **Tools mentioned**: what they're already using
- **People/roles**: who uses the data and for what purpose
- **Metrics mentioned**: any numbers, rates, or tracking already in place

If the transcript is ambiguous on any of these, note it as a gap (don't invent context).

---

## Step 2: Write the Report

Use this exact structure:

---

### CLIENT KPI REFERENCE
**Client:** [Name or "Unknown, not stated"]
**Industry:** [Type]
**Discovery Date:** [If mentioned, otherwise omit]
**Prepared by:** XRAY

---

#### Business Context
2–4 sentences. What does this client do, who do they serve, and what are they trying to accomplish with automation? Pull directly from transcript language where possible.

---

#### Stated Goals
Bullet list of what the client explicitly said they want to achieve. Use their words, not sanitized consultant-speak. If they said "I need to stop losing track of leads," write that.

---

#### Extracted KPIs
These are metrics the client mentioned directly or strongly implied. For each KPI:

**[KPI Name]**
- What it measures: [one sentence]
- Why it matters to this client: [one sentence, tied to their stated goals]
- Data source: [where this data lives or should live, Airtable, form, CRM, etc.]
- Tracking cadence: [daily / weekly / monthly / ad hoc]
- Current baseline: [if mentioned in transcript; otherwise "not established"]

Repeat for each KPI.

---

#### Recommended KPIs (Not Yet Mentioned)
These are KPIs Claude is recommending based on the client's industry, goals, and gaps in the conversation. Each one should feel like a "you'll wish you'd tracked this" addition, not padding.

For each:

**[KPI Name]**
- What it measures: [one sentence]
- Why this client needs it: [specific rationale tied to what they said]
- Data source: [where this would come from]
- Tracking cadence: [suggested]
- Confidence: [High / Medium / Low, how sure are you this is relevant?]
- Rationale: [1–2 sentences on why you're recommending it]

---

#### Gaps & Open Questions
Things missing from the transcript that need answers before building. Use a numbered list. Be specific.

Examples of the right level of detail:
- "Client mentioned 'lead tracking' but didn't specify what qualifies as a lead, web form fill, phone call, referral?"
- "No baseline metrics exist yet; will need to define what 'good' looks like before setting targets"
- "Multiple roles mentioned (Jay, Jessica, Mike), unclear who owns KPI review and reporting"

---

#### Suggested Reporting Structure
Based on what you learned, recommend:
- **Who reviews KPIs:** [role(s)]
- **How often:** [cadence]
- **Format:** [dashboard / weekly email digest / Airtable view / other]
- **Owner:** [who at the client is responsible for keeping data clean]

---

#### Notes for System Build
Bullet list of things to keep in mind when designing the Airtable schema, forms, or automations. This is the "remember this when you're building" section.

Examples:
- "Client tracks revenue by publication, not by advertiser, design tables accordingly"
- "No existing baseline data; build in a 'target' field on every KPI record so they can set goals later"
- "Manager wants mobile-friendly views, keep field counts low on primary views"

---

## Step 3: Self-Check Before Outputting

Ask yourself:

- [ ] Did I distinguish between what they said vs. what I'm recommending?
- [ ] Are all recommended KPIs tied to something specific in the transcript, not generic filler?
- [ ] Did I note every place the transcript was vague or incomplete?
- [ ] Is the "Notes for System Build" section actually useful for an Airtable builder?
- [ ] Does any of this use forbidden words (ensure, leverage, utilize, streamline)?

If a section can't be filled because the transcript didn't provide enough info, write: "Not enough information, add to open questions."

---

## Step 4: Write to disk

Save the KPI report to the canonical MONTHLY-CLIENTS location for the client:

`~/Claude-Work/CLIENTS/<CLIENT_FOLDER>/Documents/kpi-report/<build>/kpi-report.md`

Where:
- `<CLIENT_FOLDER>` is the existing client folder name (e.g., `Coding_Clarified_Janine_Whitfield`, `Guardians_of_Love_Jessica_Peoples`, `The_HOPE_for_Health_Teri_Hall`)
- `<build>` is the kebab-case build identifier (e.g., `2026-07-build`, `enrollment-agreement-flow`)

One KPI report per build. Fixed filename `kpi-report.md` so it matches the canonical MONTHLY-CLIENTS name for the GitHub push.

If the client or build isn't clear from context, ask ONE question that pins both. If the KPI report is NOT tied to a client build (rare, e.g., internal exploratory work), save to `~/Claude-Work/PROJECTS/kpi-reports/kpi-report-<topic>-<YYYY-MM-DD>.md` instead.

Create the directory if it doesn't exist. Print the absolute path after writing.

---

## Tone & Style

This is an internal XRAY working doc. Write like you're briefing a colleague, not presenting to a client.

- Direct, specific, no filler
- Use arrows for flows: "form submission → Airtable record → Zapier trigger"
- No bold headers inside bullet items
- Numbers are your friend, if a metric was mentioned, include it
- Flag uncertainty explicitly ("client implied this, but didn't confirm")

Do not use: ensure, utilize, leverage, streamline, robust, scalable solution, or any word ending in -ly as emphasis.

---

## Reference Files

(None yet. An industry-KPI library was planned for `references/industry-kpi-library.md` but hasn't been populated. When you recognize a common industry pattern, draw from your own KPI knowledge and flag the assumption in the recommendation so Rachael can correct it.)
