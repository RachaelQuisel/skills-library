---
name: client-doc-decisions
version: 1.4.6
description: Append a lightweight ADR entry (or seed the file) to the canonical `decisions.md` for a client build in the client's XRAY-INC repo. Append-only; never rewrites history. Interview-driven, ~3 questions per entry. Use when Rachael says "log this decision", "add to decisions.md", "we decided X", "we picked X over Y", "settled on X", "just decided", "record this ADR", "capture the [X] choice", "log the [X] call", or when a session lands a design/scope/tech decision worth preserving. Produces a dated ADR entry a client-side reader can follow.
---

# client-doc-decisions: append an ADR to `decisions.md`

## Purpose in plain English

This skill helps you record a project decision, the reasons for it, and the alternatives considered.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Appends a dated, lightweight ADR entry to the canonical `decisions.md` for a client build. Creates the file if it doesn't exist. Writes local Markdown only; the `client-doc-push` skill handles GitHub separately.

## Where the output lands

`~/Claude-Work/CLIENTS/<CLIENT_FOLDER>/Documents/decisions/<build>/decisions.md`

The GitHub target is the client's own repo, `XRAY-INC/<CLIENT>`, at `projects/<build>/`. Find the client repo name using the rule in the `client-docs` skill.

## Reference

Read `references/example-decisions.md` before drafting. It shows a finished `decisions.md` for a made-up client, plus one weak entry and why it fails. Match its format and level of detail.

## Drafting from sources (no interview)

When Rachael asks to draft from transcripts or discovery material, or isn't available to answer questions, skip the interview questions: read the sources, answer each question from them, and write `> TODO: <specific question>` inline wherever the sources don't answer it. Never invent facts to fill a gap. Debrief summaries written by AI can be wrong (a decision reversed the next day, for example): check every claim against the transcript itself before using it.

## Workflow: interview-driven, ~3 questions per entry

### Step 1: Detect client and build

Same detection rule as the other `client-doc-*` skills: mine the current context (client folder, session topic), and if either the client or the build name isn't clear, ask ONE question to pin both.

### Step 2: Ask the 3 questions

Ask them one message, numbered:

1. **What did you decide?**: the decision title in one line. Verb-first, no hedging. ("Route state-assigned emails from day one.", "Anchor training deadlines to first RFA approval date.")
2. **Why?**: one or two sentences. The constraint, incident, stakeholder ask, or reasoning that forced this choice. This is the field future-you will read to judge whether the decision still holds.
3. **What did you pass on, and why?**: one line naming the runner-up option and the one reason it lost. If there was no real alternative, write "No real alternative, <constraint that ruled everything else out>".

If Rachael answers with a decision that clearly implies the why (e.g., "we're moving to Fillout because Gravity Forms hit its state-template limit"), don't force question 2, pull the why from her answer.

### Step 3: Read the existing file (if any)

- If `decisions.md` exists, read it. Preserve everything above. Append the new entry at the BOTTOM (newest at bottom is the ADR convention, newest-at-top belongs to changelog).
- If it doesn't exist, create it with the header block first.

Never rewrite or reorder past entries. `decisions.md` is an audit trail: the reasoning at the moment of the decision has to survive intact, even after the decision is reversed. If a past decision has been reversed, ADD a new entry that says so and references the earlier one by date. The old entry stays. Editing it erases the trail future-Rachael will need when someone asks "why did we pick that?"

### Step 4: Write the entry

File header (only on first creation):

```markdown
# Decisions - <Build Name>

**Client:** <Client full name>
**Build:** <build name>

Append-only ADR log. Newest entries at the bottom.

---
```

Each entry uses this exact format:

```markdown
## <YYYY-MM-DD> - <decision title, verb-first>

**Decided:** <what - one sentence>
**Because:** <why - one or two sentences>
**Alternatives passed on:** <runner-up + one reason>

---
```

Rules for the entry:
- Date is the day the decision was made, absolute (not "yesterday", not "last week"). For a decision made today, that's today. When filling the file from past meetings, use each meeting's date.
- Title is verb-first, ADR convention, ≤ 80 chars, no hedging.
- Plain English. No field IDs / record IDs in narrative text. Client-readable.
- No causal speculation the consultant didn't confirm. "Because the client confirmed on 7/23" is fine; "because the client probably wants..." is not.
- Never use "clean" / "heal" / "drift" / "master" / metaphor. Say the literal thing. See `[[no-metaphors-literal-language]]`.

### Step 5: Write the file and print the path

1. Create the directory if needed.
2. Write the file (create or append).
3. Print the path and a one-line summary of the entry that landed ("Appended: 2026-07-25, Route state-assigned emails from day one.").

### Step 6: Do NOT push

Push is separate. Stop after the local write.

## Voice

Rachael's voice, direct, plain English, no filler, no metaphors. See `~/Claude-Work/ABOUT-ME/my-voice.md`. Client-readable throughout.

## When this skill is the wrong answer

- Recording that something SHIPPED → `client-doc-changelog`
- Capturing what a persona does → `client-doc-user-stories`
- Full PRD-level design → `five-signals-prd`
- Logging an internal-only preference or feedback → memory file (`feedback_*.md`), not decisions.md
