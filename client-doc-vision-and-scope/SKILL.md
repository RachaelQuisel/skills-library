---
name: client-doc-vision-and-scope
version: 1.4.7
description: >-
  Draft or update the canonical `vision-and-scope.md` file for a client build in the client's XRAY-INC repo. Four sections, plain English, client-readable: problem, vision, scope, non-goals (lighter than business-requirements or a PRD). Non-goals carry equal weight to goals: the discipline of the doc is naming what's OUT so the build doesn't balloon. Interview-driven, ~5 questions. Use when Rachael says "write vision and scope", "draft vision-and-scope.md", "scope this client build", "what's in and out of scope for this client build", "vision and scope for [client]", "vision-and-scope for [build]", "scope doc for [build]", "problem statement for this client build", or when the /deliver checklist reaches the vision-and-scope doc. Produces a four-section doc a client-side reader can follow.
---

# client-doc-vision-and-scope: canonical `vision-and-scope.md` for a client build

## Purpose in plain English

This skill helps you explain a client project's problem, intended result, included work, and excluded work.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Produces the `vision-and-scope.md` file for the client's repo `XRAY-INC/<CLIENT>` at `projects/<build>/`. Writes local Markdown only; the push to GitHub is a separate step.

## Where the output lands

`~/Claude-Work/CLIENTS/<CLIENT_FOLDER>/Documents/vision-and-scope/<build>/vision-and-scope.md`

Find the client repo name using the rule in the `client-docs` skill.

## Reference

Read `references/example-vision-and-scope.md` before drafting. It shows a finished `vision-and-scope.md` for a made-up client. Match its format and level of detail.

## Drafting from sources (no interview)

When Rachael asks to draft from transcripts or discovery material, or isn't available to answer questions, skip the interview questions: read the sources, answer each question from them, and write `> TODO: <specific question>` inline wherever the sources don't answer it. Never invent facts to fill a gap. Debrief summaries written by AI can be wrong (a decision reversed the next day, for example): check every claim against the transcript itself before using it.

## Workflow: interview-driven, ~5 questions

### Step 1: Detect client and build

Mine the current context (client folder being touched, session topic, PRD or transcripts already referenced) for the client name and build name. If either is unclear, ask ONE question that pins both.

### Step 2: Ask the 5 questions

Ask them in one message, numbered:

1. **What problem is this build solving?**: the pain in one or two sentences. Whose pain? What's happening today that shouldn't be, or what's not happening that should be. Use the client's language if they've said it.
2. **What does the world look like after this ships?**: the vision, one paragraph. Concrete. "The morning queue shows every student ≤30 days from their deadline, and the caseworker email fires without anyone touching it" is better than "daily ops are automated."
3. **What's IN scope for THIS build?**: bullet list. The specific tables, automations, forms, interfaces, integrations. Verb-first.
4. **What's explicitly OUT of scope?**: bullet list. The non-goals. This is the load-bearing section: it's what stops the build from ballooning when the client asks "can we also...". Name the things that are near the build but deliberately not in it.
5. **Any boundary calls that could go either way?**: items that could go in or out. Say where you landed and why in one line each. These are the calls the doc has to defend when someone asks "why isn't X in here?"

If Rachael's already answered some of this in the current session (PRD, discovery transcript, prior messages), pre-fill those parts before asking, and only ask about the gaps. Never invent a scope call she hasn't made.

### Step 3: Draft the file

Use this structure exactly:

```markdown
# Vision and Scope: <Build Name>

**Client:** <Client full name>
**Build:** <build name>
**Last updated:** <YYYY-MM-DD>

## Problem

<One or two sentences. Whose pain, what's happening today, what's not happening that should be.>

## Today *(optional: use before a build exists or when the source is the client's own material)*

- <what the client does now, by hand or in which tool, with counts>

## Vision

<One paragraph. Concrete picture of the world after this ships.>

## In scope

- <verb-first item>
- <verb-first item>
- <verb-first item>

## Out of scope (non-goals)

- <verb-first item>: <one-line why it's out>
- <verb-first item>: <one-line why it's out>

## Boundary calls

- **<item>:** <in or out> (<one-line why>)
- **<item>:** <in or out> (<one-line why>)

*If no boundary calls need adjudicating, delete this section rather than leaving it empty.*
```

Rules for the draft:
- Plain English. No record IDs, no field IDs, no jargon. Write so a client can follow the sentence without a glossary.
- Never use "clean", "heal", "drift", "master", or a metaphor. Name the literal thing (the field, the record, or the step).
- Non-goals are as important as goals. If the interview didn't produce non-goals, ASK AGAIN. A vision-and-scope doc with no non-goals is a wishlist; it can't defend the build against scope creep.
- Verb-first items in both In-scope and Out-of-scope: "Backfill the region field on 686 proposals" not "region backfill." Verbs make it obvious what's being committed to.
- Never fabricate scope calls. If the interview leaves something empty, write `> TODO: <specific question>` inline so Rachael sees exactly what's missing.

### Step 4: Write the file and print the path

1. Create the directory if it doesn't exist: `mkdir -p ~/Claude-Work/CLIENTS/<CLIENT_FOLDER>/Documents/vision-and-scope/<build>/`
2. Write the file.
3. Print the absolute path and a one-line summary ("Problem + vision drafted. 4 in-scope items, 3 non-goals, 1 boundary call. 1 TODO left inline.").

### Step 5: Do NOT push to GitHub

Push is a separate step. Stop after the local write.

## Voice

Rachael's voice per `~/Claude-Work/ABOUT-ME/my-voice.md`. Direct, no filler, plain English. No em-dashes in prose; use commas, semicolons, colons, parens, or two sentences. Never "ensure," "streamline," "leverage." When quoting the client's problem statement, use their exact words if they've said them.

## When this skill is the wrong answer

- Full requirements / SMART-objectives elicitation → `business-requirements` (the heavier Wiegers framework)
- PRD with capacity math and defended tradeoffs → `five-signals-prd`
- Capturing personas → `client-doc-user-stories`
- Logging a decision that came out of scoping → `client-doc-decisions`
- Recording a shipped item → `client-doc-changelog`
