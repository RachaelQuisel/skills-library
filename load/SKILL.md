---
name: load
version: 1.0.1
description: Load the five ABOUT-ME files (about-me, my-voice, my-rules, shipping-queue, working-with-claude-best-practices) so every reply that follows is grounded in Rachael's context. Use when Rachael types "/load," when the SessionStart hook did not fire, after "/clear" or context compaction, or any time the about-me-gate hook reports that one of the five files is missing from context.
---

# load

## Purpose in plain English

This skill helps you read Rachael's background, preferences, and working rules before continuing the conversation.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Read the five ABOUT-ME files that ground every reply in Rachael's context. The SessionStart hook already fires this on turn 1; this skill is the manual re-load path for when context has been reset (after `/clear`, after compaction, after the gate hook reports a missing file) or when Rachael wants a fresh pull.

## Why this exists

Claude Code caps the SessionStart hook's `additionalContext` at about 2KB. The five files together are around 40KB, so the hook cannot inject them directly — it can only emit a directive telling Claude to Read them. This skill is the Read.

## The five files

Read all five in ONE tool-use block (parallel Read calls, not one at a time):

- `/Users/rachaelquisel/Claude-Work/ABOUT-ME/about-me.md`
- `/Users/rachaelquisel/Claude-Work/ABOUT-ME/my-voice.md`
- `/Users/rachaelquisel/Claude-Work/ABOUT-ME/my-rules.md`
- `/Users/rachaelquisel/Claude-Work/PROJECTS/shipping-queue/shipping-queue.md` — stop at the `## Shipped` heading. The Shipped archive stays on disk and is only opened when appending or moving items. (Moved from ABOUT-ME/ on 2026-07-31; not auto-loaded by the SessionStart hook anymore — /load still pulls it.)
- `/Users/rachaelquisel/Claude-Work/ABOUT-ME/working-with-claude-best-practices.md`

## Rules

- Do not defer the reads. Do not summarize any file from memory. Do not skip any file.
- One tool-use block, parallel Reads.
- Re-Read all five every time `/load` runs, even if the SessionStart hook fired earlier this session. Rachael wants the fresh pull.
- If any of the five files is missing or unreadable, stop and print `MISSING: <full path>. /load cannot continue until this file exists.` Do not proceed to the next reply until Rachael fixes it. These files are load-bearing.

## Confirmation line

After all five Reads land, print exactly this four-line block (no more, no less):

```
Loaded ABOUT-ME (5 files).
Today: <YYYY-MM-DD from the system prompt's currentDate>.
Active clients: <comma-separated list from about-me.md's Current Clients section — client short names only, e.g., THFH, CC, GoL>.
Next to ship: <title of the top item under "## Open — needs to ship" in shipping-queue.md, verbatim>.
```

If the Shipping Queue has zero open items, the fourth line reads `Next to ship: nothing open.`
