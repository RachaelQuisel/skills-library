---
name: client-doc-changelog
version: 1.4.8
description: Append a dated entry to the canonical `changelog.md` for a client build in the client's XRAY-INC repo. Newest entries at the top. Interview-driven, ~2 questions per entry. Use when Rachael says "add to changelog", "log what shipped", "record today's ship", "changelog entry for [X]", "we shipped X", "log the [X] ship", "add [X] to changelog", "note the [X] ship", when a build ships something worth documenting, or when the /deliver checklist reaches the changelog step. Produces a client-readable "what changed and when" log.
---

# client-doc-changelog: append a ship entry to `changelog.md`

## Purpose in plain English

This skill helps you record what changed in a client project and when the change was delivered.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Appends a dated entry to the canonical `changelog.md` for a client build. Creates the file if it doesn't exist. Writes local Markdown only; the `client-doc-push` skill handles GitHub separately.

## Where the output lands

`~/Claude-Work/CLIENTS/<CLIENT_FOLDER>/Documents/changelog/<build>/changelog.md`

The GitHub target is the client's own repo, `XRAY-INC/<CLIENT>`, at `projects/<build>/`. Find the client repo name using the rule in the `client-docs` skill.

## Reference

Read `references/example-changelog.md` before drafting. It shows a finished `changelog.md` for a made-up client, plus one weak entry and why it fails. Match its format and level of detail.

## Drafting from sources (no interview)

When Rachael asks to draft from transcripts or discovery material, or isn't available to answer questions, skip the interview questions: read the sources, answer each question from them, and write `> TODO: <specific question>` inline wherever the sources don't answer it. Never invent facts to fill a gap. Debrief summaries written by AI can be wrong (a decision reversed the next day, for example): check every claim against the transcript itself before using it.

## Workflow: interview-driven, ~2 questions per ship

### Step 1: Detect client and build

Same rule as the other `client-doc-*` skills. If either the client or the build name isn't clear from context, ask ONE question that pins both.

### Step 2: Ask the 2 questions

Ask them one message, numbered:

1. **What shipped?**: one line per thing. Verb-first, past tense. ("Deployed the daily 6-month deadline scanner.", "Backfilled the region field on 686 proposals.") If more than one thing shipped today, list all of them; they'll go under one dated entry.
2. **What changed for the client because of it?**: one line per shipped item, in the client's language. What's different now that wasn't before. ("The morning queue now surfaces students within 30 days of their deadline.", "Every proposal now has a region auto-linked from its zip code.")

If Rachael has an existing artifact (POST_RUN doc, shipping-queue entry, session summary), offer to draft the two answers from it and let her confirm. Don't invent client-facing outcomes she hasn't stated.

### Step 3: Read the existing file (if any)

- If `changelog.md` exists, read it. Preserve everything below. Newest entries go at the TOP (changelog convention, opposite of decisions.md).
- If it doesn't exist, create it with the header block first.

Never rewrite past entries. If today's ship reverses a prior ship, add a NEW entry that says so.

### Step 4: Write the entry

File header (only on first creation):

```markdown
# Changelog - <Build Name>

**Client:** <Client full name>
**Build:** <build name>

Newest entries at the top.

---
```

Each dated entry uses this format:

```markdown
## <YYYY-MM-DD>

- **Shipped:** <what, verb-first, past tense> - <what changed for the client, one line>
- **Shipped:** <second item, if any> - <what changed>

---
```

If more than one thing ships in a day, they land as separate bullets under the same date header. If a second ship lands later the same day, append its bullet under the existing date header rather than creating a new one.

Rules for the entry:
- Date is the day the item shipped, absolute. For today's ship, that's today. When filling the file from past meetings, use the date each item went live.
- Plain English. Client-readable. No record IDs / field IDs in narrative text.
- No metaphors ("clean", "heal", "drift", "master", "smoke"). Say the literal action. See `[[no-metaphors-literal-language]]`.
- Distinguish shipped vs. still-owed, this file is for what LANDED. Draft state, WIP, and unblocked-but-not-live belong elsewhere (running-updates-and-questions.md).

### Step 5: Write the file and print the path

1. Create the directory if needed.
2. Write the file (create or update). If updating, verify the new entry landed at the correct position (top for a new date; appended under the existing date header if same day).
3. Print the path and a one-line summary of the entry(s) that landed.

### Step 6: Do NOT push

Push is separate. Stop after the local write.

## Voice

Rachael's voice, direct, plain English, past tense for shipped items, no filler, no metaphors. See `~/Claude-Work/ABOUT-ME/my-voice.md`.

## When this skill is the wrong answer

- Recording a DECISION (not a ship) → `client-doc-decisions`
- Something still WIP or not shipped → `running-updates-and-questions.md` in the client folder
- Post-run analysis with counts / verification → `POST_RUN_ANALYSIS_<date>.md` in the automation's folder (per the Seven Deliverables)
- A ship worth telling other people about → shipping-queue.md
