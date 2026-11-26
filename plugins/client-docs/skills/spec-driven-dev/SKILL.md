---
name: spec-driven-dev
version: 1.4.7
description: Enforces Rachael's spec-driven dev loop for every client-base implementation or data change. Applies to new automation (Airtable / Zap / GAS / Python / Node), backfill, bulk data update, schema change (adding, renaming, or deleting fields or tables), trigger change on an existing automation, and any data fix touching more than 10 records. The loop is plain-English README written BEFORE the code, script gated behind --dryrun + /review + --apply, and a post-run doc that closes the loop with counts and a spot-check sample. Use whenever Rachael is building, backfilling, migrating, deploying, updating, running, applying, shipping, or wrapping up work on a client base, even when she does not name the loop explicitly. Also use at end-of-task to verify all seven steps ran before reporting completion. Do NOT use for read-only diagnostics, documentation-only edits, config that does not touch data, or personal projects like La Maison.
---

# Spec-Driven Dev

## Purpose in plain English

This skill helps you agree on the intended behavior and checks before changing a client system or its information.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Rachael's loop, every time she touches a client base. The spec (plain-English README) comes BEFORE the code. Nothing ships without all seven steps. If any are missing, the task isn't done, even if the code works.

## The loop

1. Write a plain-English README for the change BEFORE the code. If I can't explain it to the client, I can't build it.
2. Write the script with a `--dryrun` flag. Field IDs only, never names.
3. Run dryrun on 5–10 real records, eyeball the diff.
4. `/review` the script + the spec (README). Claude grades its own work against my rubric.
5. Fix whatever the review flags.
6. `--apply` for real.
7. Post-run doc: before/after counts, spot-check sample, one-line changelog row in the client's base.

## Applies to

- Every new automation (Airtable, Zap, GAS, standalone script)
- Every backfill or bulk data change
- Every schema change (adding / renaming / deleting fields or tables)
- Every trigger change on an existing automation
- Every data fix touching more than 10 records

## Does not apply to

- Read-only diagnostics (a CSV of "here's what's wrong" is a report, not a change)
- Documentation-only edits
- Config changes that don't touch data

## End-of-task checklist

Before reporting a qualifying task complete, run through this:

- [ ] 1. Plain-English README written and current
- [ ] 2. Script has `--dryrun`, field IDs only, co-located README
- [ ] 3. Dryrun ran on 5–10 real records, diff eyeballed
- [ ] 4. `/review` ran on script + spec (README) BEFORE first `--apply`, saved as `<CLIENT>-Rubric-YYYY-MM-DD-<name>.md`
- [ ] 5. Review findings fixed
- [ ] 6. `--apply` ran on real data
- [ ] 7. Post-run doc exists with before/after counts + spot-check sample + one-line changelog row in the client's base

If any is missing: name which, produce them, then report completion. Do not report "done" first and add the deliverables later.

## File naming

- Spec / README: co-located with the script (`README.md` in the automation's folder)
- Rubric pass: `<CLIENT>-Rubric-YYYY-MM-DD-<name>.md`
- Post-run: `<CLIENT>-POST_RUN-YYYY-MM-DD-<name>.md` (includes before/after counts + spot-check sample)
- Changelog row: in the client's Automation Inventory / Change Log table, or as a note on affected records, check what the base already uses before choosing the pattern.

## Why this exists

The seven aren't paperwork. They're a forcing function against the shape of failure that lives one abstraction below "the code works." A `/review` pass would have caught the CC caseworker timezone bug on 2026-07-13 (a "fix" that was wrong for 17–35% of records) before it shipped. README + dryrun + review = ~15 minutes. Rolling back a bad automation that already emailed the wrong caseworkers = hours plus reputational cost.

The smaller the change looks, the more this discipline protects against silent regressions.
