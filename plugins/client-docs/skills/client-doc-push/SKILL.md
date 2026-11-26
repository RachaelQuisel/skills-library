---
name: client-doc-push
version: 1.4.7
description: Push locally drafted canonical client docs to the client's own XRAY-INC GitHub repo (XRAY-INC/CLIENT-NAME, folder projects/BUILD-NAME/). Reads .md files from the client's local Documents/DOC-TYPE/BUILD-NAME/ folders and PUTs them via the GitHub API (never clones). Use when Rachael says "push client docs", "push to MONTHLY-CLIENTS", "push to the client repo", "publish the canonical docs", "sync the docs to GitHub", or after any of the `client-doc-*` doc-building skills have staged files locally. Handles create-vs-update sha lookup and one-commit-per-file convention.
---

# client-doc-push: push drafted canonical docs to the client's XRAY-INC repo

## Purpose in plain English

This skill helps you send the prepared client documentation to its designated GitHub repository.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


The ONLY skill that pushes to GitHub. Five `client-doc-*` skills write local drafts (vision-and-scope, user-stories, interface-prompts, decisions, changelog). The other three canonical files come from `five-signals-prd` (`prd.md`), `kpi-report` (`kpi-report.md`), and the tasks.xray.tech API (`build-plan.md`). This skill publishes all of them.

Each monthly client has its own repo, `XRAY-INC/<CLIENT>`. `XRAY-INC/MONTHLY-CLIENTS` only lists those repos in its `.gitmodules` file and holds no client folders. Never push client docs to it.

## Preconditions

- **Local drafts exist:** `~/Claude-Work/CLIENTS/<CLIENT_FOLDER>/Documents/<doc-type>/<build>/<doc-type>.md` (the folder the writing skills save to)
- **`gh` CLI authenticated** OR the `mcp__github-remote__*` tools are attached
- **You have write access to the client's repository.** Ask whoever administers the XRAY-INC organization if you don't. Without it every push returns a permission error, which reads like a broken skill but is not.
- **The client repo exists:** `gh api repos/XRAY-INC/<CLIENT>` returns the repo. If it returns 404, stop and tell Rachael. Mark (person1@example.com) creates client repos; never create one yourself.

## Local client folder → GitHub client repo

Derive the repo name from the local client folder name: take the client's
organization name, drop any contact person's name, uppercase it, and join the
words with hyphens (`Acme_Widgets_Dana_Lee` → `ACME-WIDGETS`).

Before pushing, confirm the repo exists: list the repos in
`XRAY-INC/MONTHLY-CLIENTS/.gitmodules` (`gh api repos/XRAY-INC/MONTHLY-CLIENTS/contents/.gitmodules --jq .content | base64 -d`)
or call `gh api repos/XRAY-INC/<CLIENT>`. If the derived name has no match,
confirm the repo name with the consultant. Never guess. If a repo isn't listed in
`.gitmodules`, check with `gh api` before deciding it is missing.

## The 8 canonical files (only these are pushable)

Refuse to push any file whose basename isn't in this set:

`prd.md`, `vision-and-scope.md`, `build-plan.md`, `kpi-report.md`, `interface-prompts.md`, `user-stories.md`, `decisions.md`, `changelog.md`

## Workflow

### Step 1: Discover what's staged

Use `Glob` (not `find` - see [[no-reflexive-grep]]) to enumerate:

`~/Claude-Work/CLIENTS/<CLIENT_FOLDER>/Documents/*/<build>/*.md`

Each doc has its own folder: `Documents/changelog/<build>/changelog.md`, `Documents/decisions/<build>/decisions.md`, and so on. A file directly in `Documents/` or in a dated subfolder (for example `Documents/kpi-report/2026-07-30-qpi-baseline/`) needs Rachael to name which build it belongs to before it's pushed.

If Rachael didn't name a specific client or build, list what's staged across all clients and ask which to push.

### Step 2: Show the diff before pushing

First run `gh api repos/XRAY-INC/<CLIENT>`. If it returns 404, stop here and tell Rachael the repo doesn't exist yet (Mark creates client repos). A missing repo and a missing file both return 404, so without this check every file would show as CREATE.

For each candidate file:

1. Read the local file.
2. Fetch the current GitHub version via `mcp__github-remote__get_file_contents` at `XRAY-INC/<CLIENT>`, path `projects/<build>/<file>` (or `gh api "repos/XRAY-INC/<CLIENT>/contents/projects/<build>/<file>"`).
3. If the remote doesn't exist → mark as CREATE.
4. If the remote exists and content differs → mark as UPDATE (capture the `sha`).
5. If the remote exists and content is identical → mark as SKIP.

Print a table: file · action (CREATE / UPDATE / SKIP) · brief change summary.

### Step 3: Confirm before pushing

**Never push without an explicit "push it" from Rachael in this session.** See [[feedback_confirm_before_sending.md]], GitHub pushes are external-system writes and always require a per-session confirmation, even in auto mode.

If she says push, proceed. If she says "just show me the diff", stop after Step 2.

### Step 4: Push, one commit per file

For CREATEs and UPDATEs:

- Prefer `mcp__github-remote__create_or_update_file` (handles sha automatically for updates).
- Fallback (raw `gh` CLI):
  ```bash
  gh api -X PUT "repos/XRAY-INC/<CLIENT>/contents/projects/<build>/<file>" \
    -f message="<CLIENT>: <file> - <one-line what changed>" \
    -f content="$(base64 < <local-path>)" \
    [-f sha=<sha-from-Step-2>]
  ```
  `sha` is required for updates, omitted for creates.

Commit message format (non-negotiable):

`<CLIENT>: <file> - <one-line what changed>`

Examples:
- `ACME-WIDGETS: changelog.md - added 2026-07-25 region backfill entry`
- `ACME-WIDGETS: decisions.md - first ADR: applicant vs. member naming`

One commit per file. Never bundle. A single bad push can then be reverted on its own.

### Step 5: Report

For each file pushed, print:
- The GitHub URL (`https://github.com/XRAY-INC/<CLIENT>/blob/main/projects/<build>/<file>`)
- Action (CREATED / UPDATED)
- Commit SHA

For each SKIP, print the file name + "no change".

## What NOT to do

- **Never clone the repo.** GitHub API only, always. See `feedback_github_no_clone.md`.
- **Never bulk-edit multiple files in one commit.** One commit per file.
- **Never push a file whose basename isn't in the 8 canonical set.**
- **Never push to another client's repo.** Verify the local client folder → repo name match before every push.
- **Never push client docs to `XRAY-INC/MONTHLY-CLIENTS`.** It holds only the list of client repos.
- **Never push without the per-session "push it" confirmation.**
- **Never invent a commit message** that overstates what changed. If you can't summarize the change in one line, re-read the diff.
- **Only touch the repo of the client you were asked to work on.** Other client repos belong to other consultants and other engagements. Leave them alone.
- **Don't include credentials, PATs, or internal-only notes in any pushed file.** Client-readable, always.

## Sanity checks (run inline before Step 4)

- [ ] Every file basename ∈ the 8 canonical set
- [ ] CLIENT_FOLDER → `XRAY-INC/<CLIENT>` repo match confirmed with `gh api`
- [ ] Every file is plain-English (no leaked field IDs / record IDs in narrative text, technical appendices allowed)
- [ ] For updates, the sha was fetched in Step 2 (never re-use an old sha)
- [ ] For decisions.md: newest entry at the BOTTOM
- [ ] For changelog.md: newest entry at the TOP
- [ ] Rachael has said "push it" this session

## Voice for the report to Rachael

Direct summary. File · action · URL. No throat-clearing, no trailing explanatory clauses.

## When this skill is the wrong answer

- Building/editing the doc itself → the matching `client-doc-<name>` skill
- Pushing something OTHER than a canonical doc → generic `gh api` or the `mcp__github-remote__*` tools
- New client repo, or a repo restructure → Mark (person1@example.com); see `project_client_docs_infrastructure.md`
