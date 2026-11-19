# Traps and Payoff: the bookend slides

Verbatim text from Rachael's slide deck. Step 7 (traps audit) reads this to know what to flag. Step 8 (methodology bookends) reads this when the mode is *interview prep* or the prompt asks to pitch the loop.

---

## THE TRAPS: Five tells that cap you at senior

The five anti-patterns. Each is the inverse of one of the 5 signals. If any of these show up in the PRD output, flag it before declaring done.

### 1. Tech before numbers
**The tell:** "Naming Kafka before the load."
**What it means:** You picked the technology before you knew the constraints. The reviewer can't tell whether the choice fits or whether you grabbed something familiar.
**Inverse of:** Signal 1 (Frame + non-goals, numbers first)
**Audit check:** Does any tech name appear *as a new architectural choice* before the `Given` row? Naming existing client systems as scope context ("Magazine Manager feeds this pipeline") is fine, those are the frame, not the design. Picking Redis/Kafka/Lambda/etc. as a new commitment before stating the load is the trap.

### 2. No capacity math
**The tell:** "'It scales' with nothing behind it."
**What it means:** Confident assertion with no falsifiable claim underneath. Vibes-based reasoning.
**Inverse of:** Signal 4 (Quantify capacity + latency budget)
**Audit check:** Does every estimate row resolve to a falsifiable claim that changes the design? Cut rows that don't.

### 3. Lists, never commits
**The tell:** "Options with no decision or 'because.'"
**What it means:** A/B/C menu that asks the reviewer/client to adjudicate. Shows you don't have a position.
**Inverse of:** Signal 3 (Tradeoff, then commit)
**Audit check:** Does the Defend matrix have exactly one highlighted row + a "because" line? If not, force the commit.

### 4. No blast radius
**The tell:** "Happy path only. What takes down what?"
**What it means:** No SPOF named, no failure mode discussed, no mitigations paired. The reviewer assumes the worst.
**Inverse of:** Signal 5 (Failure + evolution)
**Audit check:** Does at least one Failure card name a SPOF and its mitigation? If not, add one.

### 5. No non-goals / evolution
**The tell:** "Can't say what you're deferring."
**What it means:** Unbounded scope, no v2 path. Reviewer can't grade where the design ends.
**Inverse of:** Signal 1 + Signal 5
**Audit check:** Is `Non-goal` populated? Is at least one deferred capability named?

---

## THE PAYOFF: Conviction is how staff scope gets granted

Three return-on-effort categories. Used in Step 8 when pitching the methodology itself (not when shipping a single PRD). Each card has a one-word caption.

### 1. Interviews → offers
**Card text:** "Same design, a level up, because the loop is the rubric."
**The mechanism:** The candidate who narrates the named spine gets graded on thinking, not answer. Interviewers can grade in real time. Same design, higher level.

### 2. Design reviews → influence
**Card text:** "Your option ships; people adopt what you defended."
**The mechanism:** The Defend beat names what was beaten. Reviewers and peers carry the *because* away. Adoption follows.

### 3. Org leverage → scope
**Card text:** "Others start writing the loop too. That's the multiplier."
**The mechanism:** The discipline is a contagious format. When peers start writing PRDs in the same shape, you stop being the only one producing legible reasoning, and you start being the one defining what legible reasoning looks like in your org.

