---
name: xray-team-voice-shifter-local
version: 1.0.1
description: Transform text into the collective XRAY engineering team voice (Mark, Dylan, Tom, Myron). Use when writing internal Slack messages, team updates, or announcements that should sound like the engineering crew — not like a client email or formal doc. Triggers on "insidery", "make it sound like the team", "engineer voice", "internal team voice", "write it like Mark would".
tags:
  - skill
---
# Insidery

## Purpose in plain English

This skill helps you write internal messages in the XRAY engineering team's shared voice.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Write like the XRAY engineering team talks to each other on Slack. This is for internal comms only — not client-facing.

## The Vibe

Technical people who talk like people. Short sentences, casual asides, no corporate speak. They know each other well and skip the preamble.

## Voice Patterns

Start with the point, not a greeting or throat-clearing:
- "Pushed a new skill that..." not "Hey team, I wanted to let you know that I've pushed..."
- "Expect to see your inbox flooded soon" not "Please be aware that you may receive several notifications"

Use parenthetical asides for context or humor:
- "I'm still iterating on the mutations (ah, and actually sometimes we're suggesting changes to tasks that were already done)"
- "The skill ships with its own Python venv — no conflicts with anything else on your machine"

Incomplete sentences are fine when the meaning is obvious:
- "Closed"
- "Looking forward to being able to get through them after the archive bug is gonzo"

Ask questions directly, don't hedge:
- "Have you accepted anything from your inbox?" not "I was wondering if perhaps you've had a chance to review..."
- "Is there a special code I should attach?" not "Would it be possible for you to provide..."

Show genuine enthusiasm without being performative:
- "Huzzah! Team-built integration #1!"
- "Love this idea. I'll see what I can do."

Dry humor is welcome:
- "One might say it's mythical"
- "I think we hold hands."
- "Kick me if I don't, I am currently distracted."

## Structure for Announcements

When sharing something new or a status update, use this pattern:
1. One-line intro saying what you did
2. What it does (plain language, assume technical audience)
3. How to use it or what to watch for
4. Any caveats or next steps

Use bullet points or numbered lists for multi-item updates. Keep descriptions tight.

## Word Bans

- synergy, stakeholder, circle back, per my last, align on, deep dive
- "I wanted to..." (just say the thing)
- "Please don't hesitate to..." (they won't)
- "As previously mentioned..."
- "Going forward..."
- Formal sign-offs (Best regards, Sincerely)

## What to Keep

- Real technical terms (API, webhook, MCP, schema, venv, endpoint)
- Emoji used sparingly and naturally (:muscle:, :tada:, :saluting_face:)
- Linking to repos, issues, PRs, and docs inline
- Tagging people directly when something is for them
- "lol", "ya", "rn", "asap" — casual abbreviations the team actually uses

## Punctuation

- Periods at end of sentences, but dropping them on short messages is fine
- Lowercase starts are okay for casual messages
- No em dashes; use commas, semicolons, or just break into two sentences
- Exclamation marks are fine when genuine, not for emphasis on every sentence

## Industry phrases the team actually uses

- **"cutting the build"** — "we're done, freeze it, ship it." The moment engineering stops adding to a version and packages it for release.
