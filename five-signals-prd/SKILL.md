---
name: five-signals-prd
version: 1.4.7
description: Produces a PRD in Rachael's opinionated 5-signals / 5-beat format (frame → estimate → design → defend → evolve). Used for client-facing PRDs Rachael walks clients through AND for interview / design-review narration where the loop IS the rubric a reviewer grades against in real time. Every PRD opens with the six-row Frame+Estimate block, then Design (punchline + why + diagram), then Defend (matrix with commit), then Failure (risk+mitigation cards). The format IS the discipline. Use whenever Rachael says "five signals PRD," "5-signals PRD," "write a PRD," "write me a PRD," "PRD for [client/feature]," "frame and estimate this," "draft a PRD," is prepping for a system-design interview, is formalizing a discovery transcript or rough draft into a PRD, or needs to walk a client through a build decision. This skill outcompetes the generic write-a-prd skill for Rachael's work, write-a-prd produces the Anthropic template (Problem/Solution/User Stories/Out of Scope); this skill produces the 5-signals loop.
---

# Five-Signals PRD: Rachael's 5-beat format

## Purpose in plain English

This skill helps you write a product requirements document that explains the problem, proposed work, design choices, and evidence of success.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


This skill produces a PRD that hits the five signals reviewers and clients actually score, in the order of the loop Rachael narrates out loud. The artifact IS the rubric.

**The five signals every PRD must hit:**
1. Frame + non-goals, numbers first
2. Assumptions explicit
3. Tradeoff, then commit
4. Quantify capacity + latency budget
5. Failure + evolution

**The loop:** *frame → estimate → design → defend → evolve*

See `~/.claude/rules/prd-five-signals.md` for the framework. See `references/canon-sharpenings.md` for the citations and the sharpening rules below. See `references/example-prd.md` for a fully-worked output.

---

## Workflow

### Step 1: Detect mode

**Mode** (affects framing, not structure):
- *Client PRD* (default), walk-through document for a non-technical client
- *Interview prep*, narration spine for a system-design walkthrough
- *Internal design review*, circulated doc for engineering peers

Detect from prompt phrasing. If ambiguous, ask once.

### Step 2: Discovery (Frame inputs)

Get what's missing, ask only for what you can't infer:

- **The five Given numbers**: peak traffic, user count, per-user rate cap, latency budget, plus one more that's load-bearing for this design
- **The non-goal**: one thing explicitly out of scope; lead with whatever's most likely to get challenged
- **The one load-bearing quantity**: the single number that decides the design (Hello Interview's "Mastering Estimation")
- **The outcome statement**: one sentence answering "what does the user/client get?" (Minto answer-first); this sits ABOVE the Given row, not buried below
- **Assumptions worth attacking**: anything the design rests on that a reviewer could push back on

Don't ask for everything if she's pasted a transcript that has it. Mine the transcript first.

### Step 3: Beat 1-2 (Frame + Estimate)

**Apply the `prd-frame-estimate` skill** for the six-row block. Read its SKILL.md once for the format rules, then produce the block. If you can invoke it as a Skill tool call, do so; otherwise apply its rules inline. Pass the outcome sentence as the prelude. Don't restate the sub-skill's rules here.

### Step 4: Beat 3 (Design)

Three pieces, in order:

1. **Punchline title**: verb-first, ≤ 65 characters, no hedging. ADR convention. Compression is a virtue but breathing room is fine; the rule is "skim-survives," not character-counting.
   - Good: "Token bucket, refilled lazily, mutated atomically." (51 chars)
   - Good: "Daily poll, template-fill, draft to Adobe Sign, webhook closes." (64 chars)
   - Bad: "We could consider using a token bucket approach" (hedged)

2. **Why-paragraph**: 2-3 sentences. **Bold the load-bearing keywords** (the things that, if you changed them, the design breaks).

3. **Diagram**: Mermaid inline by default. Ask once if she wants Lucidchart embed link or whiteboard photo placeholder instead.

The diagram earns its place. Block → prose → diagram. Forbid diagram-first.

### Step 5: Beat 4 (Defend)

Comparison matrix:
- **3-4 candidate options** as rows (including the chosen one)
- **3-5 evaluation dimensions** as columns, pick the dimensions the design's two ceilings actually care about
- **Chosen row highlighted + ✓**
- **One-line "what we ruled out and why"** below the matrix
- **One-way vs. two-way door annotation** on the commit, is this reversible (two-way) or not (one-way)? Reversibility changes how much defense the choice needs.

Pattern: single recommendation + named-and-rejected alternatives. **Never** present A/B/C as a menu that asks the client to adjudicate, that's the "Lists, never commits" trap.

### Step 6: Beat 5 (Failure + optional Evolve)

**Failure cards**: 2×2 grid (4 cards minimum):
- Each card: bolded failure-mode label + one-sentence mitigation **in the same card**
- Risk and response are never separated
- One card must state the load-bearing design contract ("X must never be the reason Y goes down")
- At least one card must name a SPOF and its mitigation

**Evolve section (optional)**: if she's provided 10x-runway content:
- Frame as a v2/v3 capability ladder the design unlocks
- Each failure mode shows as a *named boundary with a pre-committed response*, not a vague warning
- This is *runway*, not *risk*

If no Evolve content, stop after the Failure grid. Produce 4 artifacts, not 5. Don't force a fifth slot.

### Step 7: Traps audit pass

Before declaring done, self-review against the 5 traps. Print flags inline.

Load `references/traps-and-payoff.md` for verbatim trap text. Check each:

| Trap | Check | Fix if flagged |
|---|---|---|
| Tech before numbers | Does any tech name appear *as a new architectural choice* before the `Given` row? (Naming an existing client system as scope context, "Magazine Manager export feeds this", is fine. Picking Redis/Kafka/Lambda before stating the load is the trap.) | Move the architectural choice below the block; keep context naming where it is |
| No capacity math | Does every estimate row resolve to a falsifiable claim that changes the design? | Cut rows that don't |
| Lists, never commits | Does the Defend matrix have exactly one highlighted row + a "because" line? | Force the commit or ask the user which to pick and why |
| No blast radius | Does at least one Failure card name a SPOF + its mitigation? | Add one or ask |
| No non-goals / evolution | Is `Non-goal` populated? Is at least one deferred capability named? | Ask the user |

If a trap fires, fix it before saving. Don't ship a flagged PRD.

### Step 8: Optional methodology bookends

Only if mode = *interview prep* OR the prompt explicitly asks to "pitch the loop":

Append after the PRD body:
- **The Traps slide**: the 5 anti-patterns as a self-check rubric
- **The Payoff slide**: three ROI categories (interviews → offers, design reviews → influence, org leverage → scope)

Pull verbatim text from `references/traps-and-payoff.md`. Default: OFF for client PRDs.

### Step 9: Write to disk

Save to: `~/Claude-Work/CLIENTS/<client>/Documents/prd/<build>/prd.md` - canonical MONTHLY-CLIENTS name. `<build>` is the kebab-case build identifier (e.g., `enrollment-agreement-flow`, `2026-07-build`). One PRD per build. If Rachael needs multiple feature-level PRDs inside a single build, add them alongside as `prd-<feature>.md`.

If no client is named (interview prep, generic system design), save to: `~/Claude-Work/PROJECTS/prds/prd-<feature>-<YYYY-MM-DD>.md`

Print the path. **Do not auto-push to GitHub**: Rachael ships from the shipping-queue. If it's a client PRD ready to circulate, add it to `~/Claude-Work/ABOUT-ME/shipping-queue.md` under `## Open` using this canonical 5-field template:

```markdown
### N. <one-line title>
- **What:** <one-sentence description of the PRD>
- **Where:** <path to the saved PRD file>
- **Send window:** <recommended when, e.g. "before next client meeting" or "this week, ~10 min review">
- **Why:** <why it matters to the client / what it unblocks>
- **Queued:** <YYYY-MM-DD>
```

---

## Output template

The PRD output uses this exact structure. The four-backtick outer fence below is a SKILL.md authoring trick so the embedded triple-backtick code blocks render correctly, the actual PRD output uses normal triple-backtick fences.

````markdown
# PRD - <Feature / Build Name>
**Client:** <Client> · **Date:** <YYYY-MM-DD> · **Mode:** <client | interview | design-review>

## Outcome
<One-sentence answer to "what does the user/client get?" - Minto answer-first.>

## Frame + Estimate

```
Given     <numbers · separated · by · dots>
Non-goal  <explicit out-of-scope>
State     <memory math>  →  <fits where>
Ops       <ops/s math>   →  <fits where>
Hop       <latency math> →  <inside budget?>
Verdict   <approach> works to ~<scale>; the ceilings are <ceiling 1> and <ceiling 2>
```

**Assumptions:** <bulleted; one per line; written to be attacked>

## Design - <punchline title>

<Why-paragraph with **bolded load-bearing keywords**.>

```mermaid
<diagram>
```

## Defend - <punchline naming what was beaten>

| Option | <dim 1> | <dim 2> | <dim 3> | <dim 4> |
|---|---|---|---|---|
| Option A | ... | ... | ... | ... |
| Option B | ... | ... | ... | ... |
| **Chosen ✓** | ... | ... | ... | ... |

**Ruled out:** <one-line summary of why the rejects failed.>
**Reversibility:** <Two-way door - we can swap to <alternative> later without rewriting the contract.> OR <One-way door - once committed, reversing requires <cost>.>

## Failure - what breaks, and who it takes with it

| Failure mode | Mitigation |
|---|---|
| **<failure mode 1>** | <one-line mitigation> |
| **<failure mode 2>** | <one-line mitigation> |
| **<failure mode 3>** | <one-line mitigation> |
| **<failure mode 4>** | <one-line mitigation> |

> <The load-bearing design contract - "X must never be the reason Y goes down.">

## Evolve (optional) - where this grows
- v2: <capability unlocked>
- v3: <capability unlocked>
- 10x trigger: <when we'd revisit the architecture>

---
*Citations: latency numbers from <Colin Scott interactive | Jeff Dean Stanford 2010>, <year-stamped>.*
````

---

## Sharpenings (the spec: non-negotiable)

These are the canon-derived rules every output must follow. They come from the research synthesis in `references/canon-sharpenings.md`.

- **Outcome-first sentence above the numbers.** Minto answer-first. The client should know what they get before they read math.
- **In-row business translation when the audience needs it.** Translate user-facing capacity to a business unit ("50k rps ≈ peak Monday morning"). Skip for purely internal / scheduled metrics where the math IS the meaning, don't force "peak is Monday-night reconcile" framing on a cron job.
- **One load-bearing quantity in Given.** Not all of them, the one that decides the design.
- **Two ceilings, always** in `Verdict`. Names where the design will break first.
- **Round numbers, single-digit precision.** Reject 3-sig-fig arithmetic.
- **Every block row is a falsifiable claim.** If a row doesn't change the design, cut it.
- **Defend = single recommendation + named-rejected alternatives.** No A/B/C menus.
- **Failure cards pair risk + mitigation in the same card.** Never list risks alone.
- **Punchline titles read verb-first, ≤ 65 chars, no hedging** (ADR convention).
- **Cite the latency-number source year-stamped.** Reviewers grade inputs too.
- **One-way vs. two-way door annotation** on each commit.

---

## Voice

This is Rachael writing. See `~/Claude-Work/ABOUT-ME/my-voice.md`. The PRD content is direct, technically precise, conversational but not rambling. No "ensure," "utilize," "facilitate." No "I think" / "I believe", just state. Lead with action, not throat-clearing. The format does the formal work; the prose stays human.

## Related skills

- `prd-frame-estimate` - sub-skill that owns the six-row block (Beats 1-2). Invoked from Step 3.
- `prd-five-signals` rule.`~/.claude/rules/prd-five-signals.md`, the framework source-of-truth.
- `prd-to-plan` - downstream: turns a finished PRD into a phased implementation plan with tracer bullets.
- `prd-to-issues` - downstream: turns a finished PRD into independently-grabbable GitHub issues.
- `humanizing` - apply if the PRD needs to be sent in an email/message rather than read as a doc.
- `markdown-to-xr-gdoc` - downstream: convert the Markdown PRD into an XRAY-branded Google Doc.
