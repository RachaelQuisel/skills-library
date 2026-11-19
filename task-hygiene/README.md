# task-hygiene

Enrich and dedupe tasks in the XRAY Airtable base (Projects & Tasks at XRAY), then deliver a post-run analysis. Enrichment fills Hours Estimated, links Outcomes, and sets Parent Tasks on debrief-extracted task batches; the dedupe sweep cancels redundant duplicate tasks using conservative, non-destructive rules. Use this skill whenever the user asks to estimate hours on tasks, add or fill in outcomes, set parent tasks, organize a task batch, clean up or dedupe tasks, run task hygiene, sweep for duplicates, tidy the backlog, or enrich tasks extracted from a debrief — even if they only mention one of those pieces. Also trigger on "fill in the task fields", "add hours to these tasks", "find duplicate tasks", or "run the sweep". Always produces a post-run analysis file.

The working instructions are in `SKILL.md`.
