---
name: how-it-works-doc-writer-local
version: 1.4.6
description: Write a full PM-quality education document for a bigger automation using the 11-section HOW-IT-WORKS structure (Quick Read for the daily operator, gates, race guard, pipeline diagram, common errors, design decisions, files, open items). Use when Rachael types "/education," when she says "write a full education doc for [feature]," "PM-quality doc," "HOW-IT-WORKS doc for [automation]," "the deep education doc," "write education for [client] on [feature]," "explain [feature] to Janine/Teri/Jessica," or right after a substantial build ships and the client needs a doc that survives handoff to a new operator or engineer. Distinct from /automation-explainer-local (which is the fast bullet version for smaller automations).
---

# education

## Purpose in plain English

This skill helps you write a detailed handoff explaining how an automation works, how to use it, and how to handle common problems.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Write a full education document for the automation Rachael names (or the one that just shipped in this session). This is the deep version, the single source of truth a client can hand to a new operator, an engineer, or an owner. Follow the 11-section structure below exactly.

For a fast bullet version (six sections, one-page-ish), use `/automation-explainer-local` instead.

**Exemplar to match in tone, density, and shape:** `/Users/rachaelquisel/Claude-Work/CLIENTS/AY Media_Jay_Danzy/zapier-qb-webhook/HOW-IT-WORKS-push-to-quickbooks.md` (the AYMG push-to-QuickBooks doc). The Quick Read at the top of that doc is written for Casandra, the daily operator; every other client's doc gets a Quick Read written for that client's daily operator (Janine for Coding Clarified, Jessica for Guardians of Love, Teri for The HOPE for Health, whoever it is). The name in the Quick Read section header changes per doc.

## The Rules

- Plain English first, technical detail after. No jargon that is not defined in plain English the first time it appears.
- No metaphors. No analogies. No "clean," no "heal," no "drift," no "master," no "smoke," no "sync" (as a verb standing in for the real action). Say the literal table, field, value, and verb.
- Tight headings. Scannable tables. Every claim has a concrete example. Numbers where numbers exist.
- Never "needs fixing." Always "needs to be fixed."
- Refer to fields, tables, and records by their human-readable name in the doc body. Field IDs go in parens the first time a field is named in a section, or in the Files-and-Locations engineering tables where a developer would need them.
- The Quick Read section is written for the daily operator by name. Auto-detect who from the client folder name, Coding Clarified → Janine, Guardians of Love → Jessica, The HOPE for Health → Teri, AY Media → Casandra. Only ask Rachael if the client has more than one plausible daily operator (Guardians of Love has Jessica, Leslie G, and Oswaldo, ask which one the doc is for).
- Words that are Rachael's own vocabulary from her exemplar docs and stay: gates, hard guards, bypassable gates, Quick Read, race guard. These are not jargon in this context; she uses them herself.
- Every doc includes all 11 sections. If a section genuinely does not apply to this automation (for example, section 4 Gates for an automation that has no safety checks), write the section header followed by one line: "Not applicable for this automation, [one plain-English sentence naming why, for example: 'this automation is a scheduled read-only report and has no conditions that would block it from running.']" Do not omit the header. The discipline of forcing the question is what makes the doc trustworthy.

## The 11 sections (in this order)

### 1. Quick Read (for [Operator Name])
Page 1. The only thing the daily operator needs to read. Includes:
- **The one thing you do**: the single action (check this checkbox, submit this form, click this button) that starts the automation.
- **What you see**: a numbered list of exactly what appears on screen, in what order, in what fields, in the seconds after the action.
- **What success looks like**: a small table with each indicator (field, value, external system) and the value it takes on when the automation succeeded.
- **What failure looks like**: a small table with each indicator and the value it takes on when the automation failed, plus a one-sentence "here's what to do next" per row.
- **When to use the override** (only if there is one), the override path and the specific scenarios where it applies.

### 2. What this does
One paragraph for the owner and the engineering eyes on the client side. Numbered list of the 3 to 6 things the automation does end-to-end. Ends with the wall-clock duration ("The whole process takes about 10 to 20 seconds end-to-end.").

### 3. The Triggers
Every condition that starts the automation. If there are two automations that must not both fire (like Push versus Force Re-Invoice), spell out each one under its own subheading:
- **Automation A, "[Name]"**: bulleted list of every trigger condition (all of these must be true).
- **Automation B, "[Name]"**: same shape.
- **Why two automations instead of one with a switch**: the design rationale. Explain that the two automations block each other on purpose so both cannot fire at the same time on the same record and create two of whatever the automation creates.

### 4. The Gates (what blocks the automation)
Every safety check the automation runs before it does the thing. A table with columns: `#`, `Gate`, `What it checks`, `Why`. If some gates can be bypassed by an override and some cannot, split them into two subsections:
- **The bypassable gates**: the ones the override skips.
- **The hard guards**: the ones that fire even under the override, because they represent data problems that no amount of "I really need this" can fix.

### 5. The Numbering System (or The Data It Moves)
Two possible shapes for this section, depending on what the automation actually does:

- **The Numbering System**: use this shape if the automation assigns numbers, IDs, keys, or references. Explain how the numbering works, where each piece comes from, how the number is calculated (for example, "we add 29,999 to the autonumber so the numbers start at 30,000"), and why. Include a table of every field involved (field name, field ID, type, what it does). If the numbers cross systems (Airtable → Zapier → QuickBooks Online, for example), show the exact chain, where the number is set in the first system, where it is picked up by the tool in the middle, and where it lands in the destination.
- **The Data It Moves**: use this shape if the automation does not assign numbers. Include a table of every field or value the automation reads from one place and writes to another, showing the source (system, table, field, field ID) and the destination (system, table, field, field ID).

### 6. The Pipeline
An ASCII diagram showing the flow from the trigger through every step to the writeback. Use the AYMG exemplar's diagram shape, boxes for each system, arrows between them, one line per step inside each box. Name the actual systems in the section title:
- If the flow is Airtable → Zapier → QuickBooks Online → writeback, the section title is "The Pipeline: Airtable → Zapier → QuickBooks Online."
- If the flow is a form to Airtable to an email, the section title is "The Pipeline: Fillout → Airtable → Gmail."
- Never write a generic title like "Source → Middleware → Destination." Always name the real systems.

Below the diagram, a table titled **Where each piece of data on the [destination system] comes from, with field IDs and step references**, showing every mapped field: destination field → the exact step in the tool in the middle that carries it → source field name and ID.

### 7. The Race Guard (what stops the automation from running twice on the same record)
What the automation does to prevent running twice on the same record when the trigger fires two times in quick succession. Name the field that tracks whether the automation is idle, running, done, or failed. Name what the operator will see if a record gets stuck in the running state, and what an engineer can do to reset it.

If the automation is one-shot and there is no risk of two runs overlapping, replace this section with **What happens if the trigger fires twice**: a paragraph explaining, in plain English, exactly what the second run does (nothing, because the first run already wrote the flag field; or re-runs harmlessly; or would create a duplicate, which is why the trigger config prevents it).

### 8. Common Errors and What They Mean
The translation guide. Split into subsections:
- **Gate halts**: the "you can fix this" errors. Table with `Message`, `What's wrong`, `How to fix`.
- **Hard errors**: the "call an engineer" errors. Table with `Message`, `What's wrong`.
- **Deep-dive on the top failure mode**: for whichever error has bitten the client most (in the AYMG exemplar, this was the "Invalid Reference Id" QB Item ID bug). Include the heuristic that finds the bad record fast, a table showing valid versus invalid patterns, remediation steps, and a real example from a real incident with dates and record IDs.

### 9. For Owners and Architects
The design-decisions section. Cover:
- **Design decisions and the rationale**: one paragraph per decision. Why checkboxes instead of a button. Why two automations instead of one. Why an autonumber instead of letting the downstream system generate the number. Why the legacy field is kept untouched. Why the check that stops double-runs lives in the script AND in the trigger config (the check runs in two places on purpose, so if one fails the other catches it). Each decision named by its short form and answered in three to six sentences.
- **How the system fails safely**: the halt path and the hard-error path, step by step, showing what gets written where and what stays unchanged.
- **Audit trail**: every place a run leaves a trace (the client-visible narrative field on the record, the Airtable Automation history, the Zapier Task History, the destination system's log).
- **Versioning and rollback**: how to tell which version is live, how to roll back.
- **Release notes**: a short "what's new / what changed / known issues" block, drafted verbatim so Rachael can cut-paste it straight into a client email without further editing. Fill in the actual content from this session, do not use bracketed placeholders.

### 10. Files and Locations (for engineers)
Table of every file involved: filename, what it is, where it lives. Include the runner script, the code in the tool in the middle (Zapier Python step, Make module code, Google Apps Script, whatever it is), the schema dump, the README, the runbook, the field-mapping reference.

### 11. Open Items (to-do for follow-up)
Bulleted list of the 4 to 6 things still on the to-do list, what's built and live, what's built and needs to be deployed, what's blocked on the client, what is known-broken and waiting on a fix. Below it, a `### Shipped (no longer open)` subheading with items that have moved out of Open, checkmarked.

## Optional Appendix

**Appendix: How to provision a clean test [record type] for verification**: if the automation has a fixture setup that is not obvious (like the AYMG "provision a Test Contract via MCP with a real signed PDF" pattern), document the steps and the known-good fixture record IDs so the next session can re-run the same verification without re-figuring out the setup.

## Header block for every doc

Every education doc opens with:

```
# How the [Automation Name] Works

**Audience:** the [Client Name] team - [Operator Name] (daily operator), [Owner Name] (owner), [Engineer Name] (engineering eyes).
**Last updated:** YYYY-MM-DD.
**Current versions:** [runner script filename with version stamp] · [middle-tool code filename with version stamp] · [external system version if relevant]. Filename suffix always matches the SCRIPT_VERSION constant inside - on every version bump the file is renamed.

**What v[N] fixed** (only if the latest version was a bug fix): one paragraph on the incident, the root cause, and what the new version does about it.

This document is the single source of truth for what happens when [the trigger condition]. Read the **Quick Read** section to use it day-to-day. Read **For Owners and Architects** if you need to understand or change the system.
```

## Where to save the doc

Save co-located with the automation's code:

`~/Claude-Work/CLIENTS/<client>/Automations/<automation-name>/HOW-IT-WORKS-<automation-name>.md`

If the automation lives in a top-level folder like the AYMG `zapier-qb-webhook/` folder, save it there. If there is no clear automation folder, save it under `Project Documentation/` using the same filename pattern.

## After saving

- Print the full path to the education doc.
- Reveal it in Finder with `open -R <path>`.
- One-line summary: which client, which automation, which sections landed with the most substance and which ones are placeholder (so Rachael knows where to spend her review time).
- If any of the 11 sections has genuinely no content for this automation (for example, the automation has no numbering system and no data-mapping either), say so explicitly in the summary. Do not fabricate content to fill it.
