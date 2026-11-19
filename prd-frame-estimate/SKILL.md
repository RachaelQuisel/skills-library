---
name: prd-frame-estimate
version: 1.4.6
description: Produces the "Frame + Estimate" artifact that opens every PRD and every system design walkthrough, a single six-row block stating Given (quantified inputs), Non-goal (explicit out-of-scope), State (memory math), Ops (ops/s math), Hop (latency math), and Verdict (one-sentence punch line with the two ceilings). This is beats 1-2 of Rachael's five-signals framework (frame → estimate → design → defend → evolve). Use whenever Rachael starts a PRD, drafts a system design, says "frame and estimate," "put numbers on it," "before I draw," "numbers first," is prepping a design walkthrough or interview, or asks for the opening block of a PRD.
---

# Frame + Estimate

## Purpose in plain English

This skill helps you explain a proposed project's starting point, limits, and estimated work before developing the full plan.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Beats 1-2 of the five-signals loop (see `~/.claude/rules/prd-five-signals.md`). The artifact reviewers grade against **before** any architecture diagram appears. Always ships as the top of the PRD.

This skill is invoked as a sub-step by the parent `five-signals-prd` skill (which produces the full 5-beat PRD). It also runs standalone when only the opening block is needed (interview practice, napkin-math sanity check, scoping a build before drafting the full PRD).

## Outcome sentence: ABOVE the block

Before the block, write one sentence answering "what does the user/client get?", Minto answer-first. This is what a non-technical reader sees first. It anchors the math that follows.

Example: *"Every API caller gets a fair share of capacity, and one misbehaving caller can't take the API down for everyone else."* → then the `Given` row.

## The artifact

A single fenced code block, six rows, always in this order:

```
Given     <quantified inputs separated by · >
Non-goal  <what's explicitly out of scope>
State     <memory math>   →  <fits where>
Ops       <ops/s math>    →  <fits where>
Hop       <latency math>  →  <inside budget?>
Verdict   <one sentence: what works + the two ceilings>
```

Canonical example to match:

```
Given     50k rps peak · 2M users · cap 100 req/min/user · p99 budget < 5 ms
Non-goal  global exactness across regions - approximate is fine, say so up front
State     2M × ~30 B/bucket ≈ 60 MB → fits one Redis node's RAM, trivially
Ops       50k rps × 1 atomic op = 50k ops/s → under one primary (~100k+ ops/s)
Hop       +1 round trip intra-AZ ≈ 0.2 ms → inside the 5 ms budget
Verdict   centralized Redis works to ~100k rps; the ceilings are primary ops/s and the per-call hop
```

## How to fill each row

### Given: numbers first
Separate items with ` · ` (space-dot-space). Include:
- Peak traffic (rps / qps / events-per-min, pick the unit that matters)
- User count
- Per-user rate cap (if any)
- Latency budget (p99 or p95, with the actual ms)

### Non-goal: say it out loud
One line. State what is explicitly NOT being solved so the reviewer can't waste your time arguing about it. Lead with the thing most likely to get challenged (global scale, perfect consistency, sub-ms latency, etc.).

### State: memory/storage math
`<count> × <size> ≈ <total> → <fits where>`

### Ops: throughput math
`<rps> × <ops/req> = <ops/s> → <fits where vs. a single-instance ceiling>`

### Hop: latency math
`<hop description> ≈ <ms> → <inside the budget?>`

### In-row business translation (for client-facing PRDs)

When the audience is non-technical, add a business translation at the end of each estimate row in parentheses or after a `-`. The math stays; the meaning travels with it.

Example: `Ops       50k rps × 1 atomic op = 50k ops/s → under one primary (~100k+ ops/s) - peak Monday morning`

For interview / engineering-only audiences, the business translation is optional.

### Verdict: one sentence, two ceilings
`<approach> works to ~<scale>; the ceilings are <ceiling 1> and <ceiling 2>`

The two ceilings matter: they tell the reviewer where the design will break first, which sets up beats 4-5 (defend + evolve).

## When inputs are missing

If Rachael hasn't given the numbers, **ask before drafting**: one short message, the five things needed:
1. Peak traffic + unit
2. User count
3. Per-user rate cap (or "none")
4. Latency budget (p99 ms)
5. One thing explicitly out of scope

Then produce the block. **Do not** draw architecture, write design narrative, or pick technologies before the block is on the page. The numbers constrain the design, not the other way around.

## Format rules

- Always a fenced code block (` ``` `) - preserves alignment, copy-pasteable
- Row labels left-aligned, two spaces minimum before the content column
- Use `→` (not `->`) for the "fits where" arrow
- Use `≈` for approximate, `<` for "under," `~` for rough orders of magnitude
- Lowercase units (`ms`, `rps`, `B`, `MB`), match the example

## Related
- `~/.claude/rules/prd-five-signals.md` - full framework (5 signals + the loop)
- `reference_prd_five_signals` memory, pointer index
- `five-signals-prd` skill, the parent skill that invokes this for the opening block, then continues through Beats 3-5 (Design, Defend, Failure)
