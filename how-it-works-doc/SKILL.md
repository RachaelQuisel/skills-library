---
name: how-it-works-doc
version: 1.4.8
description: Writes a plain-English education document that explains an automation, what triggers it, what inputs it reads, what steps it takes, what outputs it produces, and what it does not do. Use when Rachael says "write a how-it-works doc," "explain this automation in plain English," "education doc for [automation]," "what does this automation do" (in a teaching context, not a debugging one), "write up this automation for the client," or asks for a doc that lets a non-technical reader understand a workflow. Produces a HOW-IT-WORKS-name.md file co-located with the automation's code or under Project Documentation/. Do not use for code-level explanations of a single function (that is the `explain-code` skill) or for inventorying every automation in a base (that is `audit-airtable-automations`).
---

# How-It-Works Doc

## Purpose in plain English

This skill helps you explain an automation's starting point, information, steps, results, and practical limits in plain English.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


## What this skill produces

A single markdown file named `HOW-IT-WORKS-<automation-slug>.md`, written so a non-technical reader can pick it up cold and understand the automation in under five minutes. The same file should also be the engineer's reference for what the system is supposed to do.

Save the file next to the automation's code (under `Automations/<automation-name>/`) when one exists. If the automation lives only in Airtable, Make, or Zapier and has no local code folder, save it under that client's `Project Documentation/` folder.

## When to use it

Trigger phrases, Rachael's words:

- "write a how-it-works doc for [automation]"
- "explain this automation in plain English"
- "write a little education document for me on [automation]"
- "what does this automation do, in plain English"
- "write up [automation] so the client can understand it"
- "do a HOW-IT-WORKS for [automation]"

Do not trigger this skill when:

- The user wants a code-level walk-through of a single function, use `explain-code`.
- The user wants an inventory of every automation in a base, use `audit-airtable-automations`.
- The user wants a Loom script or a verbal walk-through, that is a different deliverable.

## Inputs the skill needs

Before writing, gather:

1. **Which automation.** A path, a name, or a clear pointer. If ambiguous, ask one focused question.
2. **Who the reader is.** Common readers are the daily operator, the client owner, the engineer, or all three. The audience drives section depth.
3. **Where the code or configuration lives.** A path on disk, an Airtable automation name, a Make scenario, a Zapier zap. Read it before writing.
4. **What other docs already exist.** A README, a post-run analysis, a design spec, the client's `running-updates-and-questions.md`. Cross-link to them; do not duplicate them.

If any of these are missing and not obvious from the working directory, ask once. Do not guess.

## The plain-English rule (non-negotiable)

This skill exists because Rachael's clients need to read these documents and understand them. Every sentence must clear the bar below.

- **Complete sentences only.** No truncated phrases. "Fires the certificate flow" is a fragment; "When the participant completes the module, the system sends them their certificate" is a sentence.
- **No jargon stacks.** "PATCH the FK on the linked record via the upstream PAT" reads as noise. Say "the system updates the link between the two records, using the credentials stored at the project level."
- **No abbreviations the reader has to decode.** Spell out Contract Line Item, do not write CLI. Spell out Caseworker, do not write CW. The only acceptable abbreviations are ones the client already uses in their own meetings.
- **No record IDs in the body.** A reader does not care that the table is `tblExample0000046`. Use the human-readable name and put any IDs in a footnote or appendix if they are needed at all.
- **No "needs fixing." Use "needs to be fixed."** Same rule for every other gerund. See `~/Claude-Work/ABOUT-ME/my-voice.md`.
- **"Main" not "master." "Complete" not "clean."**
- **No throat-clearing.** Skip "this document explains," "the purpose of this is," "in summary." Lead with the answer.
- **No counts of demos or videos.** ("9 walk-throughs, 4 diagrams" reads as filler in a client doc.) Counts of records, fields, automations, and interfaces are fine.

If the reader is the engineer alone, technical terms are fine, but the Quick Read section at the top is always plain-English regardless.

## The spine

A HOW-IT-WORKS document follows this spine. Use the section names verbatim. Drop sections that genuinely do not apply (a one-line writeback step does not need a "Failure modes" section). Add sections only when the automation is complex enough to need them.

The two canonical examples are short-and-simple (`HOW-IT-WORKS-qb-invoice-number-writeback.md` - five sections) and long-and-complex (`HOW-IT-WORKS-acuity-training-sync.md` - eleven sections). Match the length to the automation's complexity.

### Minimum spine (every doc)

1. **Title**.`# How the <Automation Name> Works`
2. **One-sentence summary**: what the automation does, in one sentence, in plain English
3. **What sets it off (the trigger)**: what event, schedule, or human action makes it run
4. **What it needs to do its job (the inputs)**: the data, records, or credentials the automation reads
5. **What it produces (the outputs)**: what changes when the automation finishes
6. **Step by step, when the trigger fires**: numbered list, plain English, one step per sentence
7. **What this automation does not do**: the boundary; calls out what someone might reasonably assume it does that it does not

### Optional sections (add when the automation is non-trivial)

8. **Audience**: who reads this doc and which sections matter to them
9. **Quick read**: a paragraph-or-table summary for the daily operator who is not going to read the whole thing
10. **Gates and guards**: the conditions that stop the automation from running
11. **Failure modes**: what breaks, what the symptom looks like, who notices first
12. **Files and locations**: where the code, the README, the post-run analysis live
13. **Architect rationale**: why the automation was built this way; what was rejected and why
14. **Open items**: things still to be decided, blocked on the client, or pending a future build

### What success looks like / what review-needed looks like

When the automation produces records the operator scans every day (an RSVP, an order, a case), include two tables: one showing the field values that mean "this worked," one showing the field values that mean "someone needs to look at this."

## How to write each section

### Title

`# How the <Automation Name> Works`. Not "Automation X documentation." Not "<Name> Spec." The phrase "How the X Works" tells the reader the genre at a glance.

### One-sentence summary

State the actual effect, in one sentence, in the active voice. Lead with the system's name only if it matters (most of the time it does not).

Good: "When QuickBooks Online creates the invoice, the system writes the Transaction Id and Invoice Number back to the Contract record in Airtable, closing the loop on the push."

Bad: "This automation is responsible for handling the writeback process for invoices."

### Triggers

Name the trigger in plain English. If the trigger is a webhook, say "Acuity sends a New Appointment webhook." If the trigger is a schedule, say "Daily at 8 AM Pacific Time." If the trigger is a field change, say "When the Status field on a Contract changes to Approved." If there are multiple triggers, list them; do not bury them in a paragraph.

### Inputs

Bulleted list. Each line is a noun phrase that names the data the automation reads. Use the field's human-readable name. Note the source table or system in parentheses.

### Steps

Numbered list. One step per sentence. Each step starts with what the system does, not what the user does (unless the user is part of the loop). Bold the actor at the start of each step when several systems are involved (Airtable, Zapier, QuickBooks, Make, Zoom).

### Outputs

Bulleted list. Each line is a field-or-record-or-message that changes. Note the table or system the change lands in.

### What this automation does not do

Three to five bullets. The point is to disabuse the reader of assumptions they would otherwise carry. "It does not create the QuickBooks invoice, that is the Zap's Create Invoice step." "It does not retry if QuickBooks rejects the push, see [other doc] for the retry logic."

## Output format

```
~/Claude-Work/CLIENTS/<client>/Automations/<automation-name>/HOW-IT-WORKS-<automation-slug>.md
```

or, if no local Automations folder:

```
~/Claude-Work/CLIENTS/<client>/Project Documentation/HOW-IT-WORKS-<automation-slug>.md
```

After writing, report the path to Rachael and stop. Do not summarize the doc back to her; she can read it.

## Reference files

- `references/template.md` - the fillable template
- `references/exemplars.md` - paths to ten-plus real HOW-IT-WORKS docs Rachael has already written, organized by complexity
