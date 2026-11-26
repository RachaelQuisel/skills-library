# Build a client mock-up of a planned system, with its workflow, in the client's brand colors

This skill builds one web page a client can react to before anything is built. It shows the workflow first, then the planned screens in the order the process moves. A short Next Steps page goes with it.

## What to share

- The client and the build name.
- The workflow, if you have one: a Lucid chart exported as JSON, a screenshot, or written steps. Without one, the skill drafts the workflow and labels it as a draft for you to confirm.
- Which screens to show this round, and the meeting notes or requests behind each change, with their dates.
- The link to the existing mock-up, if you are updating one.

## How to start

Select this skill and describe your request, for example "add this Lucid workflow to the ScholarPoint mock-up" or "make a mock-up of the intake screens for EA". The assistant asks what it needs, agrees a definition of done with you, and posts what it is working on at each step.

## What you get

- The mock-up page, published at a link, with "new on [date]" tags for each round of changes and "proposed" tags for open questions.
- A Next Steps page with a short timeline.
- A changelog line marked "Drafted, not built."
- A report: the links, who can open them, what changed, and anything in the sources that looks wrong.

## Detailed guidance

The [working instructions](SKILL.md) describe each step, the rules the pages follow, and the reasons behind them. The [pre-publish checklist](references/review-checklist.md) lists every check. The [chart script](scripts/lucid_outline.py) reads a Lucid export.
