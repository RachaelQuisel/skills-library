---
name: plain-english-project-communication
version: 1.0.1
description: Use when Rachael asks Claude to explain project information (dashboard copy, status updates, KPI reports, base overviews, sprint summary bullets, running-updates entries, "what does this mean") or to write an Airtable Canvas prompt. Enforces plain English matched to the format (paragraphs for DMs and captions, tight bullets for sprint summaries and status posts), preserved terminology, fully labeled numbers with context, no jargon, no invented internal names ("engine", "status engine"), no exposed field/table/automation names or IDs, no arrows, no em dashes, no unrequested tasks or recommendations. Applies to any Canvas prompt build, KPI report or section, base overview, running-updates entry, or explanation destined for a client or a non-technical reader. Triggers on "write a Canvas prompt", "Airtable Canvas prompt", "explain this project", "explain the numbers", "dashboard copy", "make this readable", "no jargon", "plain English for the client", "KPI report", "base overview", "sprint summary bullets".
---

# Plain-English Project Communication

## Purpose in plain English

This skill helps you explain project work so the reader understands the purpose, numbers, and practical meaning without technical background.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Use this standard whenever explaining project information or writing an Airtable Canvas prompt for Rachael. The goal: the reader understands the content without opening Airtable and without having read the project documentation.

The previous approach failed because it removed too much context: jargon, abbreviations, vague labels, truncated sentences that force the reader to interpret. Do not repeat that.

## Format first, then apply the rules

Brevity matches the format. Before writing, name which format the output belongs to and apply the appropriate density:

- **Sprint summary / weekly status post / scannable multi-item update:** tight bullets. One bullet = one fact + its context. Noun-phrase-plus-verb is enough; full grammatical sentences are NOT required. Match the shape and voice of `references/example-sprint-summary.md` (bullets, `· Project` right-tags, verb-driven status, per-number units, Slack emoji shortcode section headers). Where the exemplar and the acronym or em-dash rules in this SKILL.md disagree, the rules here win; the reference file's own preamble notes that its as-posted content violates both.
- **KPI section (embedded in a sprint summary or a standalone Slack post):** same tight-bullet format as sprint summary. Each headline number is a bullet whose noun phrase names what the number counts and its state (`414 proposals connected to a WIOA region for the first time`). No paragraph subsections per number.
- **Slack DM answering "what does this number mean" / a single question:** short paragraph, 2 to 5 complete sentences.
- **Airtable Canvas prompt / dashboard tile caption / standalone number block:** complete descriptive labels and the five-part comparison structure (see below). Canvas prompts are specs Canvas uses to build; the USER-FACING copy inside the spec follows the plain-English rules, but the spec itself can be structured with numbered sections.
- **Base overview / longer explainer document:** structured sections with plain-English headings and complete-sentence paragraphs. Use bullets nested under a paragraph when listing or comparing a set of numbers. Longest of the formats; used to onboard someone new to a base or client build.
- **Running-updates entry / decision log entry:** short paragraph or tight bullets, depending on how much needs to be said. Follow the running-updates plain-English rule at memory file `feedback_running_updates_plain_english.md` (frontmatter name `feedback-running-updates-plain-english`).

Do NOT inflate a sprint summary into paragraphs. Do NOT compress a dashboard tile caption into a fragment. Wrong density is a failure of the standard.

## Communication requirements (apply to every format)

- Preserve Rachael's terminology. Do not translate her request into project-management, software-development, or database jargon.
- Give every number enough context to be understood on its own. In tight bullets, the unit is part of the noun phrase (`376 finished tasks archived`, `12,720 zip-region pairs checked`). In paragraphs, the surrounding sentence carries the same context (`543 of the 679 WIOA regions are linked to at least one candidate`). Never leave a bare number.
- Percentages carry what they mean as the next word (`75.7% consistent`) or in the same sentence (`candidates are currently represented in about 80 percent of the WIOA regions`).
- Use complete descriptive labels for dashboard tiles, table columns, and standalone headings. Write "Candidates linked to a WIOA region," not "Candidate linkage" or "Region coverage."
- Do not invent names for parts of the project. Do not use words such as "engine," "status engine," or similar internal-sounding terminology unless Rachael supplied that exact name.
- Do not include tasks, project boards, work queues, blockers, or prescriptive recommendations about what the team should do unless Rachael explicitly requests them. `Awaiting X` phrasing IS allowed; it describes what's blocked and on whom without prescribing action.
- Do not expose Airtable field names, table IDs, automation names, formulas, technical implementation details, or version numbers in the presentation.
- Do not use unexplained abbreviations. Spell out any acronym (WIOA, RHAS, QPI, CAP, MVP, etc.) at least once at first use in the piece, even when the immediate audience knows it, because students, external partners, and other downstream readers benefit. WIOA = Workforce Innovation and Opportunity Act. Skip the definition only when the piece is a strictly internal technical exchange between people who share the vocabulary (e.g., a code comment, a note to an engineer).
- No arrows (`→` or `->`). Use colons, semicolons, parens, "and", or a second line instead. This applies in every format, including compact bullets.
- No em dashes per `[[no-em-dashes]]`. Use colons, semicolons, parens, or two sentences.
- Do not assume the reader knows what a record, relationship, percentage, or comparison refers to.
- Do not sacrifice clarity to make the output look compact. Compact is fine; opaque is not.

## How to present a comparison

Use the same structure for every measurement. `[baseline period]` is a placeholder; substitute the actual baseline the comparison is being made against (e.g., "January 2026", "Q1 2026", "start of this fiscal year"). Do not leave `[baseline period]` literal in the output.

- **[baseline period]:** State the starting number and explain exactly what it counts.
- **Today:** State the current number using the same definition.
- **Change since [baseline period]:** State how many were added or lost.
- **Current coverage:** Show the percentage currently linked when that percentage is meaningful.
- **What this means:** Add one complete sentence explaining the practical meaning of the change.

If the baseline value is zero, do not calculate a percentage increase. State the absolute number added since the baseline period.

If the baseline value is small but exact (e.g., "a handful", "roughly 5"), state the absolute change and avoid calculating a percentage against an imprecise denominator; "grew from a handful to 543" is better than a bogus percentage.

If the available data cannot prove what was true on the historical date, do not substitute current relationships onto old records. State clearly that the historical value is unavailable and explain what evidence would be required to calculate it.

## Example

Do not write:

> Region coverage: 543 / 679

Write:

> **WIOA regions connected to candidates**
> Today, 543 of the 679 WIOA regions are linked to at least one candidate. That means candidates are currently represented in 80 percent of the WIOA regions in the table.

## Final review before delivery

Before giving Rachael the finished prompt or explanation, review every heading, label, and number and ask:

"Could someone understand exactly what this refers to without opening Airtable or reading the project documentation?"

If the answer is no, rewrite it with the missing context. Do not shorten it.

Also confirm: is the density right for the format? A sprint summary written as paragraphs is wrong. A dashboard tile caption written as a fragment is wrong. Match the density to the format.

## Related

- `references/example-sprint-summary.md` — Rachael's canonical Friday-huddle Sprint Summary post + ten rules for scannable status posts (bullets, ` · Project` tags, verb-driven status, per-number units, section-header emoji shortcodes).
- `references/example-client-update-starting-work.md` — client email to a non-technical reader when work is just starting (CCRES, 2026-10-26). Before and after: the first draft sounded finished and gave no why or benefit; the approved version separates done from next and has its own bullets for why it takes time and the benefit.
