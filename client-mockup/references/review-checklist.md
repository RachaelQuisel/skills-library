# Pre-publish checklist for a client mock-up

Go through every item before each publish. Report any item you could not check.

## Work in progress, never done
- [ ] The banner says "Work in progress" and that nothing is final or clickable.
- [ ] The intro says these are some of the screens and they will change.
- [ ] None of these words describe the mock-up or the build: done, finished, complete, shipped, ready, launched, live, every, all, final. (A goal date is "Goal: [date]".) On an update, scan the whole mock-up and Next Steps page, including text carried over from the last version.
- [ ] Screen numbers count the screens on this page ("Screen 2 of 6"). They do not claim to be the whole system.
- [ ] Changelog lines for this round say **Drafted** and "Not built."
- [ ] The Next Steps page shows the mock-up as "First draft" with a dashed outline, not as done.

## Workflow diagram
- [ ] With a Lucid export: every box, word, arrow, arrow direction, label and sticky note matches the script outline.
- [ ] Only plain typos were fixed, and each one is listed for Rachael.
- [ ] Every item in the script's "Report to Rachael" list is in your report.
- [ ] With no chart: the page labels the diagram "Our draft of the workflow, for you to confirm", and Rachael saw it before publishing. The diagram shows every outcome the screens show.
- [ ] A box the client's decision changed keeps the chart's words, has the highlight outline and a "Changed [Mon D]" label on the diagram itself.
- [ ] The diagram is SVG, not diagram code.

## Content
- [ ] Every statement traces to a source (a transcript, a document, the live schema). Anything unsourced is an open question instead.
- [ ] This round's changes carry "new on [Mon D]", and the key names each date's source.
- [ ] Every undecided item carries a proposed or "still deciding" tag, and appears in the Still open list.
- [ ] A "Decided on [date]" list holds only what the client decided, in their words. Message text keeps "wording to confirm" until the client approves it.
- [ ] Nothing undecided, and no weak practice, is shown as the plan, even if an internal document says it was agreed.
- [ ] The tag key says "from our [date] meeting" only if that meeting's transcript or notes were read.
- [ ] Key terms have hover definitions, and they show on hover and on tap.
- [ ] Example people are made up. Each first and last name was searched in the client's Airtable base and transcripts, and none matches a real staff member, applicant or contact. The footer says names and figures are examples.
- [ ] Transcripts came from the client folder or the Debrief Recordings table, and each change notes the meeting date (and the time in the call when available).

## Bias
- [ ] Status labels are neutral ("On hold", "Waiting on student") and use the one grey status style, never orange or blue. No person is colored red or labeled as failing.
- [ ] Score bands use neutral words ("Not enough evidence yet"), not deficit words ("does not demonstrate").
- [ ] No unsourced disability, ability, health or family labels on fields that feed a score.
- [ ] Example people vary, and the hardship or "problem" examples do not fall on one group.
- [ ] Where a design reduces bias (for example, reviewers score without seeing the AI score), the page says so in one plain sentence.

## Nothing that makes XRAY look bad
- [ ] No typos (read every line once more, including diagram boxes and tooltips).
- [ ] No weak practices shown as the plan (shared logins, admin passwords, manual workarounds).
- [ ] No XRAY internals: no table or field IDs, internal decisions, tool names, process notes, or "the chart says".
- [ ] No guessed causes or promises you cannot keep.

## Plain English (voice-align)
- [ ] Short sentences, one idea each. Common words. No jargon ("mobile-first", "pre-populated", "workflow automation").
- [ ] No metaphors. No em dashes.
- [ ] Each fact appears once. No sentence repeats the banner.
- [ ] Friendly and welcoming. Fewer words, diagrams first.

## Colors and layout
- [ ] White page with the client's brand colors. No tan, beige or cream panels.
- [ ] Main color used for structure, highlight color only for the newest tag, decisions and the next step.
- [ ] Text contrast is at least 4.5:1 in both light and dark mode.
- [ ] Screenshots taken: light, dark, desktop, phone width (DevTools emulation at 420 by 900 pixels with mobile turned off; Chrome windows will not shrink below 500).
- [ ] At phone width, the page does not scroll sideways (`scrollWidth === clientWidth`). Only the diagram and tables scroll, inside their own boxes.

## Publish and report
- [ ] Republished to the same link when the page already exists.
- [ ] Rachael has been told who can open each page, as the publish result states it.
- [ ] Nothing was posted to Slack, email or anywhere else unless Rachael asked.
- [ ] The report lists: links, what changed, definition-of-done status, source problems, anything skipped.

## Slack post pattern (only when Rachael asks to post)

```
Here is an early mock-up of [Build]: [link]

This is a work in progress. We're just getting started, and nothing on it is built or final. It shows some of the screens, not all of them. Your feedback will change what's there.

It starts with [the workflow]. Today I drafted [N] screens:
• [What one screen shows, in plain words]
• [...]

The plan is to go through it together on [Weekday, Month D].
```

Post it to the client's channel from the `post-to-huddle` skill table. You cannot edit or delete Slack posts. If a post needs fixing, post the corrected one and tell Rachael to delete the first.
