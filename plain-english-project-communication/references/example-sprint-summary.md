# Example: sprint summary (target voice for scannable status posts)

This is the exact format Rachael posts to a client Slack huddle every Friday. Match this shape when writing a sprint summary, weekly status post, or any scannable multi-item update. It shows how brevity and plain English coexist: every number stands on its own, every bullet is understandable to a non-technical reader, and no jargon or invented internal terms appear.

## Example 1: Example Nonprofit (2026-07-30 to 2026-07-31)

```
Sprint Summary: 2026-07-30 – 2026-07-31 | Example Nonprofit

:white_check_mark: Completed (5):
• Plan reorganized into four goal-named projects; scope locked to eight goals, new application form (Zite) first · Build plan
• Five duplicate or accidental project entries retired; 376 finished tasks archived · Build plan
• 49 orphaned tasks re-homed (30) or closed (19); four standing gap checks added · Build plan
• WIOA region ground-truth audit, Stage 1 (read-only): 12,720 zip-region pairs checked; 75.7% consistent · WIOA data quality
• 15 new tasks filed to the task inbox (application form end-to-end, five state proposals, exit form, dashboard, and more) · Build plan

:arrows_counterclockwise: In Progress (2):
• WIOA Stage 2 benchmark: cleared to proceed (1,087 source-cited rows across 38 regions); sample spot-verification pending · WIOA data quality
• 1,016 county mismatches and 70 multi-region zips flagged, awaiting fix decisions · WIOA data quality

:clipboard: Carried (3):
• Wed–Fri rolled-up email to Dana (Fillout preview, HQ blockers, WIOA questions, transcript Qs)
• Blackboard exam-file ask for the 139 graduation dates (urgent)
• 19 zip disagreements and duplicate-region picks awaiting Dana

:bar_chart: Velocity: 5 tasks | Completion rate: 71%
```

## Example 2: Example Agency (same week)

```
Sprint Summary: 2026-07-30 – 2026-07-31 | Example Agency

:white_check_mark: Completed (6):
• Status vocabulary migration applied: 12 controlled fields, 57 definitions, 1,055 record values updated · Status architecture
• Two-table compliance MVP live: 1,170 training requirements and 2,013 deadline obligations, internal vs contract clocks · Compliance tracking
• QPI 5 upload clock corrected to 24 hours internal / 72 hours contract · Compliance tracking
• Booking sync deep review: 10 defects fixed and deployed; cancellation path fixed (caught a real Aug 5 cancellation) · Acuity sync
• 12 missed July sign-ups imported and linked; 2 held on Pat's answer · Acuity sync
...and 1 more (20 booking rows renamed; timezones verified end to end, all Los Angeles)

:arrows_counterclockwise: In Progress (2):
• Junction table (one row per applicant per module): Rachael adding it; downstream builds wait on it · Compliance tracking
• Deadline-window fields: next build after the junction table · Compliance tracking

:clipboard: Carried (3):
• Email to Pat: hosting choice and the July 15/16 1:00 PM classes question
• Training SMS review email to Casey (confirm routing through Pat first)
• Shay Benton's 2 held sign-ups: re-run the import after Pat answers

:bar_chart: Velocity: 6 tasks | Completion rate: 75%
```

Note: the originally posted versions used em dashes in several bullets. These reference versions replace them with colons, semicolons, or "and" per Rachael's standing no-em-dash rule (`feedback_no_em_dashes`). Match the reference versions, not the historical posts, unless Rachael updates the em-dash rule.

## Note on acronyms: spell them out once even in insider posts (updated 2026-08-04)

Both exemplars above use `WIOA` without ever spelling out Workforce Innovation and Opportunity Act. That reflects the posts as-published, when the immediate audience (Dana, Pat, their teams) already knew the acronym. Rachael's updated preference is to spell any acronym (WIOA, PROGRAM, QPI, CAP, MVP, etc.) out once at first use in the piece — because students and other downstream readers benefit. Follow the updated rule when writing new posts; treat the exemplars as authoritative on shape but not on the acronym choice.

## Extra pattern: `...and N more` overflow

When the `Completed` section runs longer than 5 bullets, cap visible bullets at 5 and summarize the remainder in a single `...and N more (<one-line description>)` line, as shown in Example 2 above. Keeps the section scannable. `In Progress` and `Carried` sections do not use this overflow — they list every item.

## What this exemplar teaches (rules for scannable status posts)

1. **Section headers use Slack emoji shortcodes with a count:** `:white_check_mark: Completed (5):`, `:arrows_counterclockwise: In Progress (2):`, `:clipboard: Carried (3):`, `:bar_chart: Velocity: ... | Completion rate: ...`. Use the shortcode form (`:white_check_mark:`) not the Unicode glyph — Slack renders both, but the shortcode survives copy-paste unambiguously.

2. **One bullet = one fact + its context.** Not one bullet = one paragraph. If a bullet has two related facts, join them with a semicolon: `Five duplicate or accidental project entries retired; 376 finished tasks archived`.

3. **Every number carries its unit as part of the noun phrase.** `12,720 zip-region pairs`, `376 finished tasks`, `49 orphaned tasks`, `1,016 county mismatches`, `70 multi-region zips`, `139 graduation dates`, `19 zip disagreements`. Never bare `12,720` or `376`.

4. **Percentages carry what they mean as the next word.** `75.7% consistent`. Not `75.7% (consistency rate)`, not a separate `What this means:` sentence.

5. **Status is expressed through verb choice, not through a separate meaning sentence.** `checked`, `retired`, `archived`, `re-homed`, `closed`, `added`, `cleared to proceed`, `flagged`, `awaiting fix decisions`, `pending`. The verb tells the reader what happened AND its state.

6. **Project tag on the right, separated by " · ".** `· Build plan`, `· WIOA data quality`. This gives project context without forcing a section-per-project structure. Omit when every bullet in the section belongs to the same project.

7. **"Awaiting X" language is descriptive, not prescriptive.** `awaiting fix decisions`, `awaiting Dana`: states what's blocked and on whom, without prescribing what the team should do. That's the plain-English standard's "no unrequested recommendations" rule expressed in one word.

8. **Parens are for sub-lists that don't warrant their own bullet.** `(application form end-to-end, five state proposals, exit form, dashboard, and more)`, `(30)`, `(19)`, `(urgent)`. Short, no verbs, no sentences.

9. **No arrows.** Use `Wed–Fri`, `Stage 1`, or `Stage 2 benchmark: cleared to proceed`, never `Stage 1 → Stage 2` or `Wed → Fri`.

10. **Noun-phrase-plus-verb bullets are fine; full grammatical sentences are NOT required in this format.** `376 finished tasks archived` is a valid bullet. `376 tasks were archived from the project` is worse: same information, more words, no clarity gain.

## When to use this format vs. a full paragraph

Use the sprint-summary shape when:
- Writing a Friday sprint summary for a client Slack huddle
- Posting a weekly status update
- Compiling a scannable multi-item list (completed items, open items, blockers)
- The reader is skimming to catch counts and status, not reading for depth

Use a full-sentence paragraph when:
- Answering "what does this number mean" in a DM
- Explaining a single measurement in a dashboard tile caption
- Writing the "What this means" sentence at the end of a comparison block
- Delivering one thought, not a list of many

Do NOT inflate a sprint summary bullet into a paragraph, and do NOT compress a dashboard tile caption into a fragment. Brevity matches the format.
