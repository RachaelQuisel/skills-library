---
name: client-doc-build-plan
version: 1.4.7
description: Draft or update the canonical build-plan.md for a client build, structured as Projects, Outcomes, and Tasks. Reads from the tasks.xray.tech API when the project has outcomes and tasks; when it has none yet (a new client), drafts the plan from every meeting debrief and transcript for the client, with each claim verified against the recording. Use when Rachael says "build plan", "draft build-plan.md", "build plan for [client]", "buildplan", "build the plan from the transcripts", "what are the outcomes and tasks for [client]", or when the client-docs flow reaches build-plan.md.
---

# client-doc-build-plan: canonical `build-plan.md` for a client build

## Purpose in plain English

This skill helps you write a practical plan for delivering a client project in clear stages.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Produces the `build-plan.md` file for the client's repo `XRAY-INC/<CLIENT>` at `projects/<build>/`. Writes local Markdown only; the `client-doc-push` skill handles the GitHub push separately.

## Where the output lands

`~/Claude-Work/CLIENTS/<CLIENT_FOLDER>/Documents/build-plan/<build>/build-plan.md`

Find the client repo name using the rule in the `client-docs` skill.

## Reference

Read `references/example-build-plan.md` before drafting. It shows a finished `build-plan.md` for a made-up client. Match its format and level of detail.

## Source 1, always tried first: the tasks system

Projects, Outcomes, and Tasks come from `tasks.xray.tech/api` only. Authenticate with the `X-Api-Key` header; on Rachael's setup the key lives at `~/.config/xray/xray-tasks-api-key`. Never read or write the underlying Airtable base for tasks, and never route through the `update-projects` skill.

1. Resolve the project: `GET /api/projects?q=<client name>`. Try the company name and the people's names; a new client's project is often named after a person (for example "LCE: Quinn Adler King Consulting").
2. Read its outcomes (`GET /api/outcomes?projectId=<recXXX>`) and tasks.
3. If outcomes and tasks exist, write them out as the plan: one section per outcome, one task table per section with Owner, Status, and due date.
4. Test whether an API filter actually filtered. If a projectId query returns tasks from other clients, the filter was ignored; filter client-side or fall back to Source 2 for structure. Never paste another client's tasks into the plan.

## Source 2, the fallback: draft the plan from the meetings

When the project has no outcomes or tasks in the system yet, build the plan from what was actually said in the meetings. This procedure is the point of the skill; do not shortcut it.

1. **Find every meeting for the client, not just the obvious ones.** Search the Debriefs system by the company name AND by every person's name (first names, last names, and name variants such as "King-Iseman" and "Iseman"). New clients' meetings are usually not linked to a client record, and their titles are often just a person's name plus "Zoom event". Match whole words so that a short name does not match inside other words ("King" matches inside "Working"). Exclude same-named strangers by checking who attends and what the meeting is about.
2. **Read each meeting's debrief fields** (summary, progress, decisions, next actions) in date order, so later sessions override earlier ones.
3. **Verify against the recordings.** AI-written debrief summaries contain errors: decisions reversed later, numbers the recording never states, and names mixed up. Check every claim that will appear in the plan against the transcript itself, and drop or TODO-mark any claim the recording does not support. Say in the doc that claims were verified against the recordings.
4. **Write the plan as Outcomes and Tasks.** Group the work into outcomes the client would recognize. Under each, a task table with Owner, Status, and Source: the date of the session each task came from. A task nobody assigned gets the most plausible owner and stays marked as drafted.
5. **State the drafting basis in the doc.** The plan says it was drafted from the meetings, lists the sessions by date, and says the tasks are candidates until Rachael approves them.
6. **Never create tasks in the tasks system from this draft without Rachael's explicit go-ahead.** The document is the deliverable; the system write is a separate, approved step through the `create-task` flow.

## Rules for the draft

- Plain English, client-readable. Spell out every acronym at first use (MVP is the minimum viable product; OPSC is the Office of Public School Construction, and so on). No record IDs in narrative text.
- Every number carries its context. No bare numbers.
- No em dashes; use colons, semicolons, parens, or two sentences.
- Mark every unknown as a `> TODO:` line with the specific question. Never invent an owner, a date, or a package the meetings did not state.
- Update in place: the plan is a living document. Re-read the existing file first and merge.

## Write the file and print the path

1. Create the directory if it does not exist.
2. Write the file.
3. Print the absolute path and a one-line summary ("4 outcomes, 19 tasks, drafted from 5 sessions; 1 TODO left inline.").
4. Do NOT push to GitHub; `client-doc-push` is the one path to the repo.

## When this skill is the wrong answer

- Creating or reconciling the tasks themselves in the system: the `create-task` flow, after Rachael approves the plan
- The PRD's design and tradeoffs: `five-signals-prd`
- What shipped: `client-doc-changelog`
