---
name: next-skill-recommender-local
version: 1.0.1
description: >
  Recommend which Claude Code skill to run next based on current work context.
  Reads the Skill Use Cases table from Airtable, matches against what the user
  is doing right now, and suggests 1-3 skills with reasoning. Use when the user
  says "what now", "what skill should I run", "what am I forgetting", "next skill",
  "what should I do next", or at natural transition points in a work session
  (just finished a call, about to ship code, starting a new project, ending a
  work block). Also activate proactively when the user seems to be doing
  something manually that a skill could handle, or when a natural trigger moment
  occurs (e.g. transcript mentioned, email being drafted, plan just completed).
tags:
  - skill
---

# What Now

## Purpose in plain English

This skill helps you recommend a useful skill for the work currently being discussed.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Recommend the right skill at the right moment based on current work context.

## Workflow

1. Determine the user's current work phase and activity
2. Pull the Skill Use Cases table from Airtable
3. Filter to relevant skills based on phase, category, and insight tags
4. Recommend 1-3 skills with one-line reasoning
5. Show the trigger phrase so the user can run it immediately

## Step 1: Read the Context

Determine what the user is doing by looking at:
- What they just said or asked for
- Current working directory (client project? personal? XRAY?)
- Recent conversation history (just finished building? reviewing? debugging?)
- Time signals (end of day? start of session? post-meeting?)

Map to a **work phase**: Discovery, Building, QA, Delivery, Admin

Map to a **category**: Client Delivery, Writing & Voice, Development, Planning, Internal Ops, Content, Security

## Step 2: Pull Skills from Airtable

Query the Skill Use Cases table. Read references/airtable-ids.md for base, table, and field IDs.

Use `mcp__airtable__list_records` (preferred — has access to this base) or fall back to `mcp__airtable__search_records`. Filter by Work Phase and Category when possible to reduce noise. Do not use `mcp__claude_ai_Airtable__*` tools for this base.

## Step 3: Match and Recommend

Prioritize skills that are:
1. Tagged **Underused** (built but rarely invoked)
2. Tagged **Natural Trigger** for the current moment
3. Tagged **High ROI** for the current category
4. Tagged **Chain With Other Skills** if the user just ran a related skill

## Step 4: Present Recommendations

Keep it short and scannable:

```
Based on what you're doing right now:

1. /skill-name — one-line reason
2. /skill-name — one-line reason
3. /skill-name — one-line reason
```

One skill if only one is relevant. Never more than three. If none are relevant, say so.

### Example

User just finished a client call and dropped a transcript:

```
Based on what you're doing right now:

1. /micro-case-study — mine that transcript for atomic wins before you forget
2. /humanizing — draft the follow-up email in your voice
3. /post-to-huddle — post a call summary to the client's Slack channel
```

User is mid-build on an API endpoint:

```
Based on what you're doing right now:

1. /vibe-safe — run the security checklist on this endpoint before you ship
```

## Automatic Nudge Moments

These are the highest-value trigger points:

| Just happened | Suggest |
|---|---|
| Finished a client call | /micro-case-study, /humanizing (follow-up), /post-to-huddle |
| About to ship code | /review, /peer-review, /simplify |
| Starting a new project | /tech-docs-bootstrap, /explore-first, /write-a-prd |
| New client engagement | /business-requirements, /ubiquitous-language, /kpi-report |
| Building an API/endpoint | /vibe-safe, /vibe-safe-auth, /vibe-safe-errors, /vibe-safe-upload |
| End of work session | /post-to-huddle, /transcript-quotes-miner-local |
| Transcript mentioned | /micro-case-study or /kpi-report |
| Writing an email | /humanizing |
| Planning a build | /grill-me, /create-plan |
| Finished a plan | /prd-to-issues, /execute |
