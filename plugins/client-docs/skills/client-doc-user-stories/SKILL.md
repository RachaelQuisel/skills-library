---
name: client-doc-user-stories
version: 1.4.7
description: >-
  Draft or update the canonical `user-stories.md` file for a client build in the client's XRAY-INC repo. Persona-first, jobs-to-be-done anchored: every story ties a named persona to what they need the system to do FOR THEM. Interview-driven, ~4 questions. Use this, rather than `client-docs`, when drafting the user-stories file itself. Use when Rachael says "write user stories", "draft user-stories.md", "user stories for [client]", "personas for [client]", "who uses this client's system", "who does what on this client build", "map the personas", "capture the personas", or when the /deliver checklist reaches the user-stories doc. Produces a persona-organized doc that a client-side reader can follow.
---

# client-doc-user-stories: canonical `user-stories.md` for a client build

## Purpose in plain English

This skill helps you describe who uses a client's system and what each person needs it to help them accomplish.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Produces the `user-stories.md` file for the client's repo `XRAY-INC/<CLIENT>` at `projects/<build>/`. Writes local Markdown only; the `client-doc-push` skill handles the GitHub push separately.

## Where the output lands

`~/Claude-Work/CLIENTS/<CLIENT_FOLDER>/Documents/user-stories/<build>/user-stories.md`

Find the client repo name using the rule in the `client-docs` skill.

The push skill reads this exact path, so keep it.

## Reference

Read `references/example-user-stories.md` before drafting. It shows a finished `user-stories.md` for a made-up client. Match its format and level of detail.

## Drafting from sources (no interview)

When Rachael asks to draft from transcripts or discovery material, or isn't available to answer questions, skip the interview questions: read the sources, answer each question from them, and write `> TODO: <specific question>` inline wherever the sources don't answer it. Never invent facts to fill a gap. Debrief summaries written by AI can be wrong (a decision reversed the next day, for example): check every claim against the transcript itself before using it.

## Workflow: interview-driven, ~4 questions

### Step 1: Detect client and build

Look for the client name in the prompt or the current working context (which client folder is being touched). Look for the build name (kebab-case, e.g. `2026-07-build`, `exec-dashboard`, `enrollment-agreement-flow`). If either is unclear, ask ONE question that gets both.

### Step 2: Ask the 4 questions

Ask them one message, numbered, so the answers come back in one round-trip:

1. **Who are the personas?**: one line per persona: role + name if useful (e.g., "Founder, does daily student ops", "Enrollment specialist, approves proposals", "Prospective student, fills the proposal form").
2. **What does each persona actually DO with the system?**: 2-4 verbs per persona ("checks the enrollment queue every morning", "approves proposals", "answers caseworker emails"). Skip anything they'd do outside the system.
3. **What's the ONE thing each persona needs the system to make easier or automatic?**: the job-to-be-done, in their language. This is the story that anchors the persona.
4. **Anything a persona MUST NOT be able to do?**: permission/scope constraints ("Enrollment specialists don't touch financial fields", "Prospective students never see internal notes"). Optional; skip if none.

If Rachael's already answered some of this in the current session (transcripts, PRD, prior messages), pre-fill those parts before asking, and only ask about the gaps.

### Step 3: Draft the file

Use this structure exactly:

```markdown
# User Stories: <Build Name>

**Client:** <Client full name>
**Build:** <build name>
**Last updated:** <YYYY-MM-DD>

## Personas

### <Persona 1 name / role>
<one-sentence description of who they are and their context>

**What they do in the system**
- <verb + object>
- <verb + object>
- <verb + object>

**Their story**
As <persona>, I want to <job-to-be-done> so that <outcome that matters to them>.

**What they can't do** *(optional)*
- <constraint>

---

### <Persona 2 name / role>
...(same structure)
```

Rules for the draft:
- Plain English. No record IDs, no field IDs, no jargon. This is a client-readable doc.
- One story per persona at minimum. Add more if the persona has clearly distinct jobs (e.g., "morning check-in" vs "quarterly reporting").
- "As X, I want Y so that Z" is the anchor. Y is the verb; Z is the outcome the persona actually wants. Y without Z is a task description, not a user need: a future reader can't tell whether the system succeeded. If the interview didn't produce a real Z, mark the story TODO rather than inventing one.
- If a persona has no constraints, omit the "What they can't do" section.
- Before XRAY has built anything, title the list "What they do today" and describe the client's current tools and steps.
- Outside organizations that act on the work (a state agency, an auditor, a funder) go in an optional "## Outside parties" section after the personas: one line each on what they do and when. They don't get user stories.
- Never fabricate personas or stories. If the interview leaves something empty, write `> TODO: <specific question>` inline so Rachael sees exactly what's missing.

### Step 4: Write the file and print the path

1. Create the directory if it doesn't exist: `mkdir -p ~/Claude-Work/CLIENTS/<CLIENT_FOLDER>/Documents/user-stories/<build>/`
2. Write the file.
3. Print the absolute path and a one-line summary of what landed ("3 personas: Founder, Enrollment specialist, Prospective student. 4 stories total. 2 TODOs left inline.").

### Step 5: Do NOT push to GitHub

The push is a separate skill (`client-doc-push`). Stop after the local write.

## Voice

Rachael's voice per `~/Claude-Work/ABOUT-ME/my-voice.md`. Direct, no filler, plain English. No em dashes in prose; commas / semicolons / parens are fine. Never "seamless," "streamline," "leverage." Use the persona's own words when Rachael quoted them.

## When this skill is the wrong answer

- Drafting a PRD → `five-signals-prd`
- Logging a decision → `client-doc-decisions`
- Recording what shipped → `client-doc-changelog`
- Client wants a full requirements doc → `business-requirements`
