# Canon Sharpenings: research synthesis backing the five-signals-prd skill

This file holds the citations and the "why" behind each non-negotiable rule baked into `SKILL.md`. Load when the skill needs to defend a choice or explain a rule's origin. The skill itself only needs to *follow* the rules, it doesn't need to read this file every run. Read it on demand when (a) a user pushes back on a rule, or (b) you're iterating the skill and need the source material.

---

## Origin trace: where the 5 signals and the loop come from

Every *noun* in Rachael's framework is canonical. What's novel is her synthesis (the verb-form loop, the named "Defend" beat, and the six-row Frame+Estimate block as a fixed glance-readable opener).

### Per signal

| Signal | Closest canonical equivalent | Source |
|---|---|---|
| 1. Frame + non-goals, numbers first | "Step 1: Requirements" + numbers up front | Alex Xu, *System Design Interview* Vol. 1; Hello Interview Requirements phase ([hellointerview.com](https://www.hellointerview.com/learn/system-design/in-a-hurry/delivery)) |
| 1b. Non-goals | "Things that could reasonably be goals but are explicitly chosen not to be" | Google design docs ([industrialempathy.com](https://www.industrialempathy.com/posts/design-docs-at-google/)); Kevin Yien / Square PRD via Lenny Rachitsky |
| 2. Assumptions explicit | Standard convention in Google design docs + tech specs | Will Larson ([lethain.com](https://lethain.com/engineering-strategy/)) |
| 3. Tradeoff, then commit | "For this dating app, I'll prioritize consistency for matching but optimize for availability when viewing profiles" | Hello Interview CAP framing ([hellointerview.com](https://www.hellointerview.com/learn/system-design/core-concepts/cap-theorem)) |
| 4. Quantify | Back-of-the-envelope estimation | Jeff Dean / Peter Norvig ([brenocon.com/dean_perf.html](https://brenocon.com/dean_perf.html)); ByteByteGo ([bytebytego.com](https://bytebytego.com/courses/system-design-interview/back-of-the-envelope-estimation)) |
| 5. Failure + evolution / blast radius | Chaos engineering vocabulary | Netflix / Gremlin ([gremlin.com/chaos-engineering](https://www.gremlin.com/chaos-engineering)) |
| 5b. Path at 10x | "Deep Dives" phase | Hello Interview |

### The loop (frame → estimate → design → defend → evolve)

Closest sequence is **Hello Interview's six-phase delivery**: Requirements → Core Entities → API → Data Flow → High-Level Design → Deep Dives. Rachael's loop compresses Xu's 4-step and Hello Interview's 6-step into a verb-driven spine. The **verb-form** (not noun-form) is novel; the **named "Defend" beat with its own air time** (not reactive Q&A) is novel.

### Strongest citations to anchor the framework

1. **Hello Interview, Delivery Framework**: https://www.hellointerview.com/learn/system-design/in-a-hurry/delivery
2. **Alex Xu, System Design Interview Vol. 1**: most-cited PRD-adjacent template
3. **Design Docs at Google**: https://www.industrialempathy.com/posts/design-docs-at-google/, strongest authority for Non-Goals + explicit assumptions

---

## The sharpenings (each rule and its source)

### Outcome-first sentence above the numbers
**Source:** Minto Pyramid Principle (Barbara Minto, via McKinsey); Lenny Rachitsky on Square PRD style.
**Why:** Business clients read top-down. The first sentence answers "what does the user get?", *then* they read math. Inverted order loses the room.

### In-row business translation
**Source:** IEEE Spectrum "Improve Engineering Communication"; Stanford Online "10 Tips for Communicating Technical Ideas to Non-Technical People."
**Why:** "50k rps" is invisible to a magazine publisher. "≈ peak Monday morning" lands instantly. Translate every number in the same row so the math and the meaning travel together.

### One load-bearing quantity in Given
**Source:** Hello Interview, "Mastering Estimation" (Evan King): *"It's not the answer that matters as much as the thought process that led you there."*, https://www.hellointerview.com/blog/mastering-estimation
**Why:** A wall of numbers is the "No capacity math" trap with extra steps. Name the one number that decides the design.

### Two ceilings, always in Verdict
**Source:** Rachael's own example, already in the canonical Frame+Estimate slide.
**Why:** The two ceilings name where the design breaks first. They direct the next round of review questions. Without them, reviewers don't know where to push.

### Round numbers, single-digit precision
**Source:** Fermi estimation; Hello Interview "Keep It Simple."
**Why:** 3-significant-figure arithmetic is overfit to inputs you don't know precisely. It also reads as a lack of altitude. Round.

### Every block row is a falsifiable claim
**Source:** Hello Interview warns against math that doesn't change the design.
**Why:** This is the "No capacity math" trap from the other side, math for its own sake. If cutting the row wouldn't change anything downstream, cut the row.

### Defend = single recommendation + named-rejected alternatives
**Source:** Qwilr on sales proposals, https://qwilr.com/blog/how-to-write-sales-proposals/; ADR convention.
**Why:** Modern consultant consensus reverses the old A/B/C menu. Multiple options slow decisions because they force the buyer to adjudicate. Lead with one recommendation; surface alternatives as *already considered and rejected because…*

### Failure cards pair risk + mitigation in the same card
**Source:** Hinz Consulting "Proposal Risk Assessment", https://hinzconsulting.com/proposal-risk-assessment/
**Why:** *"Risks build trust when paired with mitigations; they erode it when listed alone."* Rachael's own Beat 5 slide already does this, formalize it.

### Punchline titles verb-first, < 50 chars, no hedging
**Source:** ADR title convention (Michael Nygard, 2011), https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
**Why:** Skim-survives. The title is the commit; the body defends it. Hedged titles ("We could consider...") read as no-commit.

### Cite the latency-number source year-stamped
**Source:** Colin Scott interactive latency numbers, https://colin-scott.github.io/personal_website/research/interactive_latency.html
**Why:** Dean's 2010 numbers are off by orders of magnitude for current hardware. Pin a year-stamped source so reviewers can grade the input, not just the math.

### One-way vs. two-way door annotation
**Source:** Jeff Bezos 1997 shareholder letter; popularized by Shreyas Doshi.
**Why:** Reversible commits (two-way doors) deserve light defense; irreversible commits (one-way doors) deserve heavy defense. Annotating the door type tells the reviewer how much weight the commit needs to bear.

---

## Risk framings the skill should refuse

These are anti-patterns the research surfaced. The skill should reject them.

- **A/B/C menus that ask the client to adjudicate.** Single recommendation only.
- **Risks listed without mitigations.** Always paired.
- **Forward-looking "fragility lists."** Evolve sections frame as v2/v3 runway, not as scary unknowns.
- **Math without design consequence.** Cut rows that don't change the architecture.
- **Tech name before constraint.** Numbers come first, always.

---

## Where this came from

Three parallel research agents, 2026-06-02 session. Synthesis lives in the plan file `~/.claude/plans/virtual-strolling-swing.md`. Subagent run summaries persisted at the agent IDs `aabba3551a2deeaea`, `a335c317435e02814`, `a42c66799d6c87bb3` (recoverable via session transcripts if needed).
