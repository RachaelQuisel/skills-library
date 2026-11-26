---
name: ship
version: 1.4.7
description: Run /education (deep 11-section markdown doc) then /build-page-publisher-local (shareable web page) back-to-back on one automation Rachael just deployed, then move the matching item in shipping-queue.md from Open to Shipped. Use when Rachael types "/ship [automation-name]," when she says "I just shipped X," "I deployed X, do the docs," "wrap up the docs for X," "post-ship docs for [automation]," or any variant that names one specific automation that just went live and needs both a filed doc, a shareable link, and its shipping-queue entry closed. Distinct from /deliver (which is the end-of-task checklist for tests + README + post-run).
---

# ship

## Purpose in plain English

This skill helps you create the detailed explanation and shareable handoff page for a newly delivered automation.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Rachael's post-ship doc chain. When one automation goes live for a client, this skill runs the two doc-producing skills back-to-back on that automation and closes the loop by moving the matching shipping-queue entry from Open to Shipped, all from a single command.

## The chain (four steps, in order)

1. **Build context**: if the current session has not already touched this automation, read its folder first: `README.md`, the runner script, the workflow design doc, the `/rubric` pass, the `POST_RUN_ANALYSIS_*.md`, and any co-located `HOW-IT-WORKS*.md` from prior versions. Every one of those files that exists gets Read before step 2 starts. If the automation folder does not exist, stop and ask Rachael where the automation actually lives, do not fabricate a path.

2. **Run `/education`** on the named automation. Produces the full 11-section HOW-IT-WORKS markdown doc, filed co-located with the automation code at `~/Claude-Work/CLIENTS/<client>/Automations/<automation-name>/HOW-IT-WORKS-<automation-name>.md`. Follow the `education` skill's rules verbatim.

3. **Run `/build-page-publisher-local`** on the same automation, reusing the markdown from step 2 as the source content so the two docs stay word-for-word consistent. Publish the Artifact page. Follow the `build-page-publisher-local` skill's rules verbatim.

4. **Close the shipping-queue loop**: open `~/Claude-Work/ABOUT-ME/shipping-queue.md`, find the item under `## Open - needs to ship` that matches this automation (match by client + automation name + recent Queued date). Move it under `## Shipped` with a `Sent:` line stamped today, plus a two-line note linking to the education doc path and the artifact URL. If no matching Open item exists, print `No matching Open item found in shipping-queue.md for [automation]. Skipping queue update - add manually if needed.` Do not fabricate an entry.

## Inputs

- **Automation name**: Rachael passes it as the argument to `/ship`. Example: `/ship push-invoice-to-quickbooks`. If she runs bare `/ship` with no argument, ask: "Which automation? Name it as it appears in the client's Automations folder."
- **Client**: auto-detect from the current session context (which client folder was recently touched, which client the automation belongs to). If ambiguous, ask.
- **Daily operator**: auto-detect from the client folder using the standard mapping: Example Nonprofit → Janine, The HOPE for Health → Teri, AY Media → Casandra. Example Agency has three plausible operators (Jessica, Leslie G, Oswaldo), ask once at the top of `/ship` which one the Quick Read is for, and the answer flows into both `/education` and `/build-page-publisher-local`. Do not let either downstream skill ask again.

## Before starting

- Check whether an education doc already exists for this automation (look for a file at the expected save path). If one is already there, ask: "An education doc for [automation] already exists at [path]. Overwrite, save the new one with today's date suffix (`-YYYY-MM-DD` before the extension), or skip `/education` and just publish `/build-page-publisher-local`?" Do not silently overwrite.

## Rules

- Sequential, not parallel. Step 2 finishes before step 3 starts. Step 3 reads the freshly-written markdown as its source.
- Both docs use the same operator name and the same client context. Do not let the two downstream skills drift on either.
- Plain English throughout. Both downstream skills already enforce this, do not restate rules here, delegate to them.
- Do not send the Artifact link automatically. Step 3 already offers to draft a Slack or email message to the operator for Rachael's review, let it handle that step.

## After all four steps have run

- Print a three-line summary:
  - Line 1: `Education doc filed at <full path>.`
  - Line 2: `Artifact published at <URL>.`
  - Line 3: `Shipping queue: moved "<matched item title>" to Shipped.` (Or: `Shipping queue: no matching Open item, skipped.`)
- Reveal the education doc in Finder with `open -R <full path>` (matches the `/education` skill's own after-save step).
- One-line prompt: "Want the artifact link drafted into a message to [Operator Name]? Yes / no." This is the same prompt `/build-page-publisher-local` produces; surface it once at the end of `/ship` rather than mid-chain so Rachael sees the full result before deciding.
