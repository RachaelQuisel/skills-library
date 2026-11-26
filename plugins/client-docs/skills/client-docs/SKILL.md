---
name: client-docs
version: 1.4.7
description: Decide which canonical client docs a session's work belongs in, and which skill writes each one, for the 8 canonical files per build (prd, vision-and-scope, build-plan, kpi-report, interface-prompts, user-stories, decisions, changelog) in each client's XRAY-INC GitHub repo. Use when the user says "update client docs", "document this build", "which docs need updating", "backfill the client docs", when a client build ships something worth documenting across several docs, or when the /deliver checklist reaches its docs step. For a single doc, the matching client-doc-* skill is the better fit.
---

# Client Docs: canonical education documentation per build

## Purpose in plain English

This skill helps you create and maintain the documents that explain a client project and its decisions, plans, changes, and use.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Every client build gets 8 canonical Markdown files. They live in GitHub, not locally. This skill keeps them created and current so nothing Rachael builds for a client is forgotten.

## Where docs live

Repo: `XRAY-INC/<CLIENT>`, one repo per client
Path: `projects/<build-name>/`
Local drafts: `~/Claude-Work/CLIENTS/<CLIENT_FOLDER>/Documents/<doc-type>/<build-name>/<doc-type>.md` (for example `Documents/changelog/2026-05-build/changelog.md`)

`XRAY-INC/MONTHLY-CLIENTS` is only an index. It lists each monthly client repo in its `.gitmodules` file and holds no client folders. Never write client docs to it.

The consultant names the client when invoking this skill. If the client isn't
named and can't be read from the current context, ask which client before doing
anything else. Never assume.

Client repo names are uppercase, hyphen-joined organization names with no
contact person in them (`Acme_Widgets_Dana_Lee` → `ACME-WIDGETS`). Derive the name
that way, then confirm the repo exists: list the repos in
`XRAY-INC/MONTHLY-CLIENTS/.gitmodules`, or run `gh api repos/XRAY-INC/<CLIENT>`.
If no repo matches, stop and tell the consultant. Mark (person1@example.com) creates
client repos; never create one yourself.

Build-name convention: lowercase words joined by hyphens, dated when it's a monthly build (e.g., `2026-05-build`) or named for the system (e.g., `exec-dashboard`).

## The 8 canonical files

| File | Contains | Skill that produces it |
|---|---|---|
| `prd.md` | The PRD, **ALWAYS in five-signals format** (never the generic template) | `five-signals-prd` |
| `vision-and-scope.md` | Problem, vision, scope, non-goals (client-readable) | `client-doc-vision-and-scope` (heavier Wiegers version: `business-requirements`) |
| `build-plan.md` | Projects → Outcomes → Tasks | `client-doc-build-plan` (API first; drafts from meeting transcripts when the project has no outcomes or tasks yet) |
| `kpi-report.md` | What the client measures and why | `kpi-report` |
| `interface-prompts.md` | One section per bespoke interface element: the **Airtable Labs Canvas** prompt used to build it | `client-doc-interface-prompts` |
| `user-stories.md` | Who does what and why, per persona | `client-doc-user-stories` |
| `decisions.md` | Append-only ADR log: "We decided X because Y" with date | `client-doc-decisions` |
| `changelog.md` | What shipped, when, what changed (newest first) | `client-doc-changelog` |

Diagrams: Mermaid fenced blocks inline in the .md files, GitHub renders them. Prefer a diagram over a paragraph for flows.

For one overview of the whole build (every client product and deliverable, how each gets made, who receives it), use `client-doc-workflow-diagram`. It reads discovery and these 8 docs and publishes a shareable web page.

## Reference examples

Each writing skill has a finished example for a made-up client in its `references/` folder. Read the matching one before drafting:
- `client-doc-vision-and-scope/references/example-vision-and-scope.md`
- `client-doc-user-stories/references/example-user-stories.md`
- `client-doc-interface-prompts/references/example-interface-prompts.md`
- `client-doc-decisions/references/example-decisions.md`
- `client-doc-changelog/references/example-changelog.md`

## How to write (RULES: non-negotiable)

1. **Projects, Outcomes, and Tasks come from `tasks.xray.tech/api` only.** Authenticate with the `X-Api-Key` header. Never read or write the underlying Airtable base directly, and never route through the `update-projects` skill. If the API cannot return what `build-plan.md` needs, say so and stop. Do not work around it.
   - Read the key from a file on the machine, never from inside this skill. On Rachael's setup it lives at `~/.config/xray/xray-tasks-api-key`. Use your own file at your own path.
   - Never paste the key into a skill file, a document, a commit, or a chat message.
   - **Fallback when the project has no outcomes or tasks in the system yet** (a new client): draft `build-plan.md` from the meeting debriefs and transcripts instead. Find every meeting for the client (search people's names as well as the company name; new clients' meetings are often not linked to a client record), verify each claim against the recording per rule 4, and write outcomes and tasks with owners, each traced to the session it came from. Say in the doc that it was drafted from meetings and that the tasks are candidates until Rachael approves them. Do not create tasks in the system from it without her explicit go-ahead.
2. **Draft locally; push only through `client-doc-push`.** Read the current repo copy with `gh api "repos/XRAY-INC/<CLIENT>/contents/projects/<build>/<file>"` (never clone). Write drafts to `~/Claude-Work/CLIENTS/<CLIENT_FOLDER>/Documents/<doc-type>/<build>/<doc-type>.md`. Never write to GitHub from this skill. `client-doc-push` is the one path to the repo, and it waits for Rachael's "push it".
3. **Update in place, append-style for running docs.** `decisions.md` and `changelog.md` are append-mostly: add dated entries, never rewrite history. The other six are living documents: revise sections, keep them current.
4. **Check debrief summaries against the transcript.** AI-written debrief summaries can contain decisions that were reversed later in the same meeting or the next day. Confirm each claim in the transcript before putting it in a doc.
5. **Plain English.** These are education documents a client-side reader may see. Complete sentences, no record IDs in narrative text (table/field IDs belong in technical appendices only). Say "normalize," never "clean."
6. **Entry formats live in the writing skills.** Use the format in `client-doc-decisions` and `client-doc-changelog` exactly. Don't restate it here.
7. **Keep sensitive details out.** Transcripts can contain meeting passcodes, shared logins, and personal or health details. None of it goes into a client doc, even a draft.

## Update flow (per session or daily run)

1. Identify which client(s) and build(s) the work touched. Create a doc only when there is real content for it, or when Rachael asks for placeholders. Before XRAY has shipped anything, don't create `changelog.md`; without a recorded decision, don't create `decisions.md`; without a prompt that was run, don't create `interface-prompts.md`.
2. Diff mentally against what happened: decisions made → `decisions.md`; things shipped → `changelog.md`; new/changed interface → `interface-prompts.md`; scope moved → `vision-and-scope.md` + `prd.md`; plan changed → `build-plan.md`; new metric → `kpi-report.md`.
3. Read the existing repo copy first. Merge, don't overwrite.
4. Run the matching writing skill for each doc, then hand the drafts to `client-doc-push`.
5. Report what was drafted: which files, which clients, one line each.

## What NOT to do

- Don't invent content to fill a file, a stub that says "No user stories captured yet" beats fabricated stories.
- Don't touch any client repo other than the one you were asked to work on. Other repos belong to other consultants' clients and to finished engagements.
- Don't duplicate what another canonical file owns, link between files instead.
- Don't put credentials, PATs, or internal-only gripes in these docs. Client-readable, always.
