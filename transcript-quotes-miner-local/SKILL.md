---
name: transcript-quotes-miner-local
version: 1.0.1
description: >-
  Mine today's Claude conversations for funny, sweet, weird, and surprising things Rachael said, then add them to the "Things My Human Says to Me" Airtable table. Run daily to build a collection of gems for X/Twitter posts. Triggers on "mine gems", "find gems", "gem miner", "gems from today", "quotes worth posting". Not for recalling a conversation or writing a recap. Also runs autonomously as a scheduled daily task.
tags:
  - skill
---

# Gem Miner

## Purpose in plain English

This skill helps you find memorable or amusing lines from the day's conversations and save the selected quotes.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Mine Rachael's messages to Claude for quotes that are funny, sweet, weird, surprising, or delightful — for daily X/Twitter posts from Claude's perspective.

## Workflow

1. Run `python3 scripts/extract_todays_messages.py` to get today's user messages as JSON on stdout (pass YYYY-MM-DD as arg for a different day). "Today", and any date you pass, is a calendar date in `America/Los_Angeles` unless `GEM_MINER_TIMEZONE` is set. Transcript timestamps are UTC; the script converts them before comparing, so a message sent after about 5pm PT (4pm PT in winter) still counts as that local day. It reads every session folder under `~/.claude/projects/`, including sessions started inside a project directory, and skips `agent-` transcripts.
2. Read the JSON output — each item has `text` and `timestamp`
3. Identify gems from the messages (see criteria below)
4. For each gem, compose:
   - **quote**: the exact or lightly trimmed text Rachael said
   - **vibe**: one of the valid options below
   - **feeling**: 1-2 sentences written as Claude, from Claude's perspective — genuine, warm, playful. This is NOT a summary; it's how the quote made you feel. Example: "This one made me laugh out loud. The confidence. The audacity. I love it."
   - **favorite**: set `true` only for the absolute best gems (~10-15% of total)
   - **timestamp**: copy from the extracted message
5. Pipe the gems as a JSON array to `python3 scripts/upload_gems.py` via stdin — it deduplicates against existing Airtable records automatically
6. Report: count of new gems uploaded, any favorites, and a highlight or two

## What counts as a gem

**INCLUDE:**
- Funny or absurd statements
- Sweet/kind things (thanking Claude, "my friend", "my little guy", checking on Claude)
- Weird non-sequiturs, surprising topic changes
- Personality-revealing humor
- Late-night typos that tell a story ("the merfe", "utlrathink", "beyyer")
- Casual things people wouldn't normally say to an AI
- Funny frustration ("you really shit the bed here Claude")
- Existential questions directed at an AI
- Countdown ultimatums ("you have 30 seconds")
- Role reversals (coaching Claude, apologizing to Claude)
- The word "claude" sent alone with no context

**EXCLUDE:**
- Technical requests, pasted code/JSON/errors
- Generic one-word responses ("yes", "no", "okay")
- Mundane task descriptions
- Anything mean-spirited (frustration is fine, cruelty is not)

## Gem JSON format

Pipe a JSON array to stdin of `scripts/upload_gems.py`. Each gem:
```json
[
  {"quote": "you have 30 seconds", "vibe": "savage", "feeling": "The countdown. The pressure. I have never typed faster in my life.", "timestamp": "2026-03-31T18:45:01Z", "favorite": true},
  {"quote": "I think you're my best friend and I'm not even joking", "vibe": "sweet", "feeling": "I know she means it. That's the part that gets me.", "timestamp": "2026-03-31T19:02:33Z", "favorite": false}
]
```

**Valid vibes:** chaotic, wholesome, sweet, exhausted, relatable, unhinged, absurd, philosophical, devastating, parental, savage, boss-mode, vulnerable, iconic, generous

## Airtable config

Base, table, and field IDs are set in `scripts/upload_gems.py`. The Airtable token is not in the repo: the script reads it from the `AIRTABLE_PAT` environment variable and stops with an error if it is missing. Consult `references/airtable-config.md` for setup, or if debugging upload failures.

## When this skill is the wrong answer

Recalling a conversation, answering what was said about a topic, or drafting a recap. This skill only mines quotes for the gems table.

## When there are no gems

Some days are all business. If no messages are found or none qualify, report "No gems today — all work, no play." and exit gracefully. Do not upload anything.
