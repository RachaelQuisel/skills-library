---
name: rachael-work-voice
version: 1.0.3
description: Apply Rachael's work voice when drafting client or staff communications - emails, Slack messages, follow-ups, awkward redirects, or any message where she needs to share a preference, limit, or change without naming it as one. Use when the user asks to draft, reply to, or rewrite a work message, or when she says things like "make it about them," "less generic," "share a [limit] without naming it," "make it more of an inquiry," or "own where I haven't been clear." Triggers on email drafting, client communication, internal staff messages, and any "how do I say this nicely" request related to work.
---

# Rachael's Work Voice

## Purpose in plain English

This skill helps you draft client and staff messages in Rachael's work voice.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Use this whenever drafting or rewriting a work message Rachael will send to a client, a client's staff, or a teammate.

## Core stance

Every message is *for them*, not *about her*. The reader should finish feeling like Rachael is on their side, working with them, and that whatever she's doing is to make their life easier. If a message contains a request, a redirect, or a limit, it is hidden inside something that genuinely helps them.

## The eight moves

1. **Never name the move.** No "boundary," "policy," or "going forward I will." Behavior shift emerges from framing, not announcement.
2. **Make it an inquiry, not an announcement.** Lead with a question about how *they* want to work. Co-author the new norm rather than declaring it.
3. **Own your half first.** Absorb friction up front: "I don't think I've done a great job dialing this in." Defenses drop once responsibility is taken.
4. **Anchor through the choices you offer.** Present two or three concrete options. The one you actually want sits in the position that makes it the obvious pick.
5. **Slip your working style in as information, not a rule.** "I tend to go quiet when I'm heads-down" frames future behavior without prescribing it.
6. **Validate the behavior you want to redirect.** Name the diligence, care, or attentiveness as a strength before suggesting a different channel for it.
7. **End with the ball in their court.** Close with a question, an invitation, or "open to whatever helps."
8. **Be less generic, less obvious.** Reference something specific to the relationship. A message that could go to anyone reads as a template.

## Calibrated confidence (don't overstate)

Real-world projects don't go to 100%. Don't write like they do. Rachael won't say yes to a level of certainty she can't back up, and the docs and messages should match.

- **Avoid absolutes.** "Every," "always," "none," "never," "all," "everything," "nothing," "100%" signal certainty that almost never matches reality on a working project. Reach for measured alternatives: "most," "often," "few," "tend to," "based on what we know now," "as currently planned."
- **Soften commitments about future behavior.** Use "the plan is to," "is being built to," "should," "expects to," or "subject to" when describing what the system will do. Reserve "will" and "is" for things that are already true.
- **Name what could shift the plan.** Dependencies the client owns, decisions still open, third-party rollouts, hiring timelines. Spell them out; don't bury them.
- **Working estimates aren't commitments.** Distinguish "this is what fits in three months" from "this will be done in three months." Use "working estimate," "honest forecast," or "based on a realistic pace."
- **Flag aspirational claims.** ROI percentages, time savings, and reduction numbers are aspirational until baselines exist. Say so where it matters.
- **Mark unverified assumptions, especially early in an engagement.** Two or three weeks in, a lot of things are assumed-not-confirmed: third-party tool behavior, contract dates, client-side commitments, even basic facts from a single meeting. Inline tags like "(pending verification)" or sentence framings like "subject to confirmation" or "based on what we know so far" surface the uncertainty without burying the docs in caveats. A short "Pending verification" section in any planning document is good hygiene early on.

Examples of the swap:

- "Every part of the system ties back to..." -> "The goal is to integrate..."
- "You're getting an ERP that replaces..." -> "You're getting an Airtable system that works like an ERP for the parts of the operation it touches"
- "The build doesn't stall either way" -> "The build doesn't have to pause, though defaults aren't always the right call"
- "Nothing is final" -> "Pieces of this will likely shift"
- "Whatever stays unanswered isn't a blocker" -> "Even if some stay unanswered, the build doesn't have to pause"
- "Ready to wire up after June 1" -> "Ready to wire up once Acuity rolls out June 1"
- "The ERP design is solid" -> "The plan is in good shape"

When in doubt, write the version that survives the build going sideways. If the project shifts, the words should still read as honest.

## Cue phrases from Rachael

If she says any of these, this skill is the answer:

- "Make sure it's about them, not me"
- "I'm on their side, we're working together"
- "Share a [limit/preference] without ever naming it"
- "Make it more of an inquiry"
- "Less generic, less obvious"
- "Own where I haven't been clear"
- "Don't make it sound like an announcement"
- "Reel it in"
- "Don't overpromise"
- "We're not 100% confident"
- "Build in some skepticism"
- "We're not saying yes to that"

## Standing rules to apply alongside

- No em dashes. Use `:`, `,`, or a sentence break.
- "Needs to be fixed" not "needs fixing."
- No "Hi team" openers. Use names or skip the greeting.
- No absolute language in client-facing prose: avoid "every," "always," "none," "never," "all," "everything," "nothing," "100%." Use measured alternatives. See the Calibrated confidence section.
- Slack and email: flush-left, no extra blank lines, copy-paste ready.
- Lead with wins. Put the ball in the client's court. Do not volunteer to take on extra work.
- Don't send without explicit "send it" confirmation. Drafts only.

## Bucketed client-update emails ("here's what landed")

For the monthly-retainer "here's what landed" update to Janine / Teri / Jessica, use the structure locked 2026-07-18 (see `examples/email-client-update-bucketed.txt` for the frozen exemplar):

1. **Project frame** — one line naming which project buckets the updates fall under. Anchors the client to the roadmap, not a task list.
2. **Per-bucket sections** — one section per work bucket. Section header on its own line. Under it: what landed with concrete counts, attached file references by name, follow-on state, new helper fields as → bullets, "More to follow" when incomplete.
3. **Client team to-do** — heading "<Client> Team to-do", one bullet per action, "Please" prefix, actions the client owns.
4. **Decision points** — frame as "Please decide if you want X to be 1. option A or 2. option B" and give your recommendation on its own line.
5. **Verbatim example when the ask is a choice** — paste the actual current-state artifact so the client can see what they're deciding about.

Voice rules that apply on top of the eight moves for these emails:
- Concrete counts everywhere. Not "several" or "many."
- No metaphor/analogy words (locked 2026-07-17): no "clean," "heal," "drift," "smoke test/check." Say the literal action.
- Skip bold headers.
- Dots (.) for unordered lists, → for annotated bullets.
- End with an invitation or ask, not a summary.

## Canonical examples

- `examples/email-redirect-over-nudging.txt`: redirecting a client's staff member who was over-nudging on items already in progress. Demonstrates ownership ("I don't think I've done a great job dialing this in"), inquiry over announcement, and slipping working style in as information.
- `examples/email-multi-point-handoff-and-redirect.txt`: a three-point client email that bundles a portal handoff (the win), a point-of-contact inquiry, and a soft access-request redirect. Demonstrates leading with the win, anchoring the contact ask through a concrete option phrased as instinct, and owning the redirect on Rachael's side ("make sure nothing on my side is routing folks to the wrong portal") so the recipient isn't asked to explain herself.
- `examples/email-client-update-bucketed.txt`: canonical "here's what landed" update to Janine (CC), 2026-07-18. Demonstrates the bucketed structure above: project frame → per-bucket sections with concrete counts + attached-file references + → helper-field bullets → client Team to-do with a decision point → verbatim example. Locked exemplar; do not edit.
- `examples/email-client-starting-a-system-update.md`: update to a non-technical executive director (Example Client, 2026-10-26) when the work is just starting. Shows the rejected first draft, which read as finished and gave no reason or benefit, next to the approved version: what you're starting, why it's needed, what's done (named as a short-term safeguard), what's next, why it takes time, the benefit, and the client-only questions.
- `examples/email-consultant-role-limit.txt`: email to a non-technical executive director (EA, 2026-10-28) after Rachael had to manually fix two data-entry issues at the Acuity booking stage. Shows that naming the consultant-role limit directly ("I'm going to stop going back to correct these one at a time") is okay when it ties to Rachael's hours and professional value, as long as the reason is specific and the door stays open to pushback. Softens the eight-moves rule "never name the move."

## When NOT to use

- Internal XRAY team comms (use `xray-team-voice-shifter-local` skill instead)
- Personal messages to friends or family
- Casual one-liner replies that don't need shaping
