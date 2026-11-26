# HOW-IT-WORKS Exemplars

Real HOW-IT-WORKS documents Rachael has written. Use these as reference for tone, length, and structure. Match the length of the doc to the complexity of the automation; do not pad a simple writeback into a long doc, and do not compress a multi-trigger system into a short one.

## Short and simple (5–7 sections, ~50 lines)

For an automation with one trigger, a small number of steps, and no operator decision-making.

- `~/Claude-Work/CLIENTS/Example Media_Rowan_Ellis/Automations/QB Downstream/HOW-IT-WORKS-qb-invoice-number-writeback.md` - writeback step inside a Zap, five sections, no Quick Read needed.

## Medium (8–10 sections, ~100–200 lines)

For an automation with a single trigger but multiple decision points, gates, or downstream effects.

- `~/Claude-Work/CLIENTS/Example Media_Rowan_Ellis/Automations/Contract Signing/HOW-IT-WORKS-contract-signing-fetch.md`
- `~/Claude-Work/CLIENTS/Example Media_Rowan_Ellis/Automations/Contract Signing/HOW-IT-WORKS-contract-signing-save-signature.md`
- `~/Claude-Work/CLIENTS/Example Media_Rowan_Ellis/Automations/QB Downstream/HOW-IT-WORKS-link-qb-transactions.md`
- `~/Claude-Work/CLIENTS/Example Media_Rowan_Ellis/Automations/QB Downstream/HOW-IT-WORKS-contract-approved-on-qb-webhook.md`
- `~/Claude-Work/CLIENTS/Example Media_Rowan_Ellis/Automations/Editorial Story/HOW-IT-WORKS-story-timeline-start-from-assignment.md`
- `~/Claude-Work/CLIENTS/Example Media_Rowan_Ellis/Automations/Editorial Story/HOW-IT-WORKS-story-yellow-flag-two-days-out.md`
- `~/Claude-Work/CLIENTS/Example_Nonprofit_Dana_Whitfield/Automations/csv-export-bb-genius-link/HOW-IT-WORKS-csv-bb-link.md`

## Long and complex (11+ sections, 200+ lines)

For an automation that is actually a system, multiple triggers, multiple scenarios, daily operator-facing decisions, several failure modes.

- `~/Claude-Work/CLIENTS/Example_Agency_Pat_Okafor/Automations/acuity-training-sync/HOW-IT-WORKS-acuity-training-sync.md` - the canonical long-form example. Includes Quick Read, four trigger scenarios, what-success-looks-like and what-review-needed-looks-like tables, gates, failure modes, architect rationale, open items.

## What to copy from each

| What you need to figure out | Look at |
|---|---|
| How to write the one-sentence summary | The QB Invoice Number Writeback doc. Five sentences total in that doc; the summary is the second one. |
| How to structure the Quick Read for the operator | The Acuity Training Sync doc, section 1. |
| How to write the "what success looks like" and "what review-needed looks like" tables | The Acuity Training Sync doc, end of section 1. |
| How to handle multiple triggers without confusing the reader | The Acuity Training Sync doc, section 3, four scenarios listed separately rather than mashed together. |
| How to keep a short doc short | The QB Invoice Number Writeback doc, no padding, no optional sections, done in 45 lines. |
| How to write the "what this does not do" section | Both. The point is to disabuse the reader of assumptions they would otherwise carry. |
