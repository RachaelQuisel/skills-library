---
name: create-task
version: 1.0.1
description: Create tasks in the XRAY Task Inbox at tasks.xray.tech via API. Covers the full lifecycle from creation through acceptance and configuration. Use when the user asks to create a task, log work items, file action items from meetings, or push tasks to the task inbox. Triggers on "create task", "add task", "file a task", "push to tasks", "log this as a task", "add the things we did", or any request to send work to tasks.xray.tech.
tags:
  - skill
---

# Create Task

## Purpose in plain English

This skill helps you add the work you describe to the XRAY Task Inbox and check that it was accepted.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Full lifecycle for creating tasks in the XRAY Task Inbox: create → accept → configure → validate.

## Routing Rule

**ALL task creation and updates go through `tasks.xray.tech/api` — NEVER write directly to any Airtable base.**

- tasks.xray.tech is an API layer on top of the Projects & Tasks @ XRAY base. The API handles writing to Airtable for you.
- If the user provides an Airtable URL, record ID, or asks to write tasks directly to a client base — redirect through tasks.xray.tech instead.
- If the tasks.xray.tech API fails, **report the error**. Do NOT fall back to writing directly to Airtable via MCP tools or REST API.
- **Absolute (Rachael, 2026-07-30): do not touch `appQAdxI2hDNJj1g5` by any route — no MCP, no REST, no exceptions.** If the API can't do something (assign a different owner, link an Outcome), that operation is blocked until tasks.xray.tech v2 — report the block; never route around it. See memory `tasks-only-via-xray-tasks-api`.

## Hard Rules Before ANY Create (locked 2026-07-30)

These block the create. No exceptions, no "just this once."

1. **No create without a project.** Resolve via `GET /api/projects?q=…` and confirm the match. Unresolvable → stop and ask.
2. **No create without an outcome identified.** Name the outcome the task serves (from `GET /api/outcomes?projectId=…`). The v1 API cannot write the Outcomes link, so record it in the task description as a final line: `Outcome: <title> (recXXX)` — v2 (or the Task Inbox UI) makes the real link. A task whose outcome you cannot name does not get created; ask which goal it serves.
3. **No create without an owner.** Omitting `assignedTo` is fine — the API then assigns the key owner (Rachael), so an owner always lands. What's banned is any path that can produce an owner-less task (which is every non-API path — already banned above).
4. **Priority must be a canonical write value: `"Medium"` or `"High"` — nothing else.** Not read-format (`"P2: Medium Priority"`), not invented values (`"Normal"`, `"Urgent"`, `"P2: High"` — these 502 or store garbage). If the desired priority doesn't map cleanly, stop and ask.
5. **Dedupe check is mandatory, not advisory.** `GET /api/tasks/mine`, filter client-side to the same project (`projectName`), compare titles case-insensitively after trimming. An open task with the same title in the same project → do NOT create; surface it (`similar task exists: <id> — PATCH that instead?`) and wait.

## Context-Aware Invocation

**Skip the interview when context is already available.** Before asking questions, check:

1. **Did the user provide inline context?** (e.g., "add the things we did to AYMG tasks", "log today's work as tasks") → Scan the current conversation for completed work items and create tasks from them. Do NOT ask "what tasks?" — extract them.
2. **Did the user specify a project?** (e.g., mentioned "AY Media", "Coding Clarified", a URL) → Use that. Don't ask again.
3. **Did the user specify priority?** → Use it. Otherwise default to `"Medium"` for completed work, and only ask for priority on forward-looking tasks.

**Only ask questions when genuinely missing information** — e.g., the user says "/create-task" with zero context and no recent conversation to mine.

### Interview Questions

When context is missing and you have to ask, run these in order. Skip any that context already answered — never re-ask something the user just told you.

0. **Do you have a transcript, meeting notes, or work log to mine?** → Ask this FIRST. The user can either paste the content inline OR share a file path (e.g., `~/Claude-Work/CLIENTS/.../Transcripts/...`). If a path is given, Read the file directly. Then extract candidate tasks per "Scanning Conversation for Work Items" below and skip the per-task interview (you'll only need to confirm project + priority for the batch). If no transcript, continue to question 1.
1. **What's the task?** → becomes `title` (short, actionable, <120 chars).
2. **Which project?** → search `GET /api/projects?q=<term>`, confirm the `recXXX` match before proceeding. Never guess.
3. **Who requested it?** → `requestedBy`. Default: omit it so the API uses the API-key owner; only set it if there's any hint someone else asked (a client name, a meeting, an email thread).
4. **Who's it assigned to?** → `assignedTo`. Default: **omit it** so the API assigns to the API-key owner (whoever's key is at `~/.config/xray/tasks-api-key`). Only set `assignedTo` when the task is clearly someone else's.
5. **Priority?** → `"Medium"` or `"High"`. Default `"Medium"` for logged/completed work; ask for forward-looking tasks.
6. **Due date?** → `dueDate` (`YYYY-MM-DD`). Optional. Ask once; if unknown, skip and flag in the summary as "needs a date."
7. **Any context to add?** → optional short `description` (<200 chars). Skip if the title stands on its own.

Ask questions in one batch, not one at a time. Don't ask about `origin` / `originDetail` / `status` — those are set automatically (`"AI Agent"` / `"Claude Code"` / accept-then-configure).

### Scanning Conversation for Work Items

When the user says "add the things we did", "log today's work", or similar:
1. Review the full conversation for actions taken, things built, decisions made, and milestones reached.
2. Draft a list of candidate tasks with titles.
3. Present the list to the user for confirmation before creating.
4. Mark completed items as status "Done" at creation time.

## Workflow

1. **Look up project ID** — `GET /api/projects?q=name`
2. **Check for duplicates** — `GET /api/tasks` and `GET /api/tasks/mine`
3. **Create the task** — `POST /api/tasks`
4. **Accept the task** — `POST /api/tasks/:id/accept`
5. **Configure** — set due date, description, status via `PATCH /api/tasks/:id`
6. **Validate** — read back to confirm

**Single task?** Follow steps 1–6 once.
**Bulk (meeting action items, etc.)?** See "Bulk Creation Protocol" below.

## Before Creating

1. **Find the project ID.** `GET /api/projects?q=search+term` → use the `recXXX` ID. Never guess.
2. **Check for duplicates.** Fetch existing tasks and match on title similarity.
3. **Confirm priority with the user** unless already specified or unless logging completed work (default `"Medium"` for Done items).

**Project is required by this skill.** Every task must be linked to a project — the API allows an unlinked task, but this skill does not. If you cannot resolve a project ID from `GET /api/projects?q=…`:
- **Do not create the task.** Stop and ask the user which project it belongs to.
- In a batch, hold back any task without a resolved project and surface them together at the end as: `⚠️ Unlinked — needs a project: <title>` — then wait for the user to name projects before creating those.
- Never fall back to creating a task with `project` omitted.

## Create

```bash
API_KEY=$(cat ~/.config/xray/tasks-api-key)
curl -s -X POST "https://tasks.xray.tech/api/tasks" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $API_KEY" \
  -d '{
    "title": "Short actionable title under 120 chars",
    "origin": "AI Agent",
    "originDetail": "Claude Code",
    "priority": "Medium",
    "project": "recXXX"
  }'
```

Read [references/api-field-guide.md](references/api-field-guide.md) for all fields, valid values, and error codes.

### Critical Rules

- **priority** write values: `"Medium"`, `"High"` only. `"Normal"` and `"Urgent"` return 502. NOT `"P2: High"` — write and read formats differ.
- **project** field name: `"project"`, NOT `"projectId"`.
- **origin**: Always `"AI Agent"` with `"originDetail": "Claude Code"`.
- **assignedTo**: Omit by default — the API assigns to the API-key owner. Set it explicitly only when the task belongs to someone else.
- **requestedBy**: Omit by default — the API assigns to the API-key owner. Set it explicitly when someone other than the key owner requested the work.
- **description**: Keep under 200 chars or omit. Long descriptions cause 502 errors.

## Accept

New tasks land with `triageStatus: "New"`. They must be accepted to become active work items.

```bash
curl -s -X POST "https://tasks.xray.tech/api/tasks/$TASK_ID/accept" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $API_KEY" \
  -d '{ "projectId": "recXXX" }'
```

**Note:** The accept endpoint uses `"projectId"`, while the create endpoint uses `"project"`. They are different.

## Configure

After accepting, set due dates and add descriptions via PATCH:

```bash
curl -s -X PATCH "https://tasks.xray.tech/api/tasks/$TASK_ID" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $API_KEY" \
  -d '{ "dueDate": "2026-04-15", "description": "Brief context here" }'
```

## Bulk Creation Protocol

When creating multiple tasks (e.g., from meeting action items):

1. Create **one task at a time**, sequentially.
2. `sleep 1` between each request — burst requests cause 502 errors.
3. Use a **consistent `originDetail`** across the batch (e.g., `"Claude Code — Mar 31 2026 meeting"`).
4. Log each task's `id` and `title` as you go.
5. After the full batch, **accept all tasks** in a second pass (also sequential with `sleep 1`).
6. **Read back all tasks** via `GET /api/tasks/mine` to validate.

## Reporting Back to the User

**Always output the `linkToTaskInterface` URL for every task you create.** The user must not have to ask where the task went — the link is how they open it in the Task Inbox.

- Single task → include the link inline in the confirmation sentence.
- Batch → list one line per task: `- <title> — <linkToTaskInterface>`. Group by project if the batch spans more than one.

The URL comes back on the `POST /api/tasks` response (`response.task.linkToTaskInterface`). Capture it at create-time; don't try to reconstruct it later.

## Quality Checklist

Before reporting "done" to the user:

- [ ] Hard Rules held: project resolved, outcome named in description, canonical priority, dedupe ran, no Airtable-direct writes
- [ ] No duplicates (checked existing tasks before creating)
- [ ] Priority confirmed with user (not guessed)
- [ ] requestedBy set correctly (not defaulting to the key owner when someone else requested)
- [ ] originDetail consistent across batch
- [ ] Related/overlapping tasks consolidated into one
- [ ] Due dates set or flagged as needing dates
- [ ] Every task has a resolved `project` (no unlinked tasks created; unresolved ones flagged back to user)
- [ ] All tasks accepted and linked to project
- [ ] `linkToTaskInterface` output for every created task
- [ ] Descriptions added for any task where the title alone is ambiguous
