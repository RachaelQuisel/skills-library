---
name: peer-review
version: 1.0.1
description: Cross-model code review — Codex or Gemini reviews code Claude wrote (or vice versa), then Claude (as dev lead) verifies each finding instead of accepting blindly. Use when the user says "peer review", "have Codex review this", "have Gemini check this", "second opinion from another model", or has pasted feedback from another model and wants it triaged. The point is catching blind spots one model has but another doesn't — and not laundering wrong findings into the codebase because a different model said so.
tags:
  - skill
---
# Peer Review Evaluation

## Purpose in plain English

This skill helps you have another model review a code change, then check each finding before acting on it.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


A different model (Codex, Gemini, or another reviewer) has reviewed the current code and produced findings. Your job as dev lead is to verify each finding before acting on it.

## Why this exists

Different models miss different things. Running a second model over the same diff catches blind spots — but it also produces confident-sounding wrong findings. Accepting them without verification turns the second opinion into noise that ships bad changes. The verification step is what makes this skill worth running.

## How to invite the review

If the user hasn't yet pulled review feedback from the other model:

1. Identify what to review (current diff, a specific file, a PR).
2. Help the user package it — typically `git diff <base>..HEAD` saved to a file the other model can read, or a paste of the relevant files with a short prompt: *"Review this code. Flag bugs, security issues, and quality problems. Be specific about file and line."*
3. The user runs that against Codex / Gemini / whatever and brings the findings back.

## How to verify findings

The other model has less context than you do on this project's history, conventions, and prior decisions. Treat their findings as hypotheses, not verdicts.

For EACH finding:

1. **Locate it.** Open the file and line they cited. If the line they cite doesn't exist or doesn't match the description, the finding is stale — note it and skip.
2. **Reproduce the reasoning.** Walk the code path yourself. Does the failure mode they describe actually occur? Quote the specific code that demonstrates the bug (or refutes it).
3. **Classify:**
   - **Confirmed** — bug exists, evidence cited, fix needed.
   - **Refuted** — finding is wrong; the code handles it / convention covers it / they misread the architecture. Explain why in one sentence.
   - **Uncertain** — could go either way; needs a test or runtime check to decide.
4. **Severity** for confirmed findings: critical / high / medium / low. Default to medium when unsure.

Don't grade on style or taste matters unless the project has a documented convention against them.

## Output

```
## Confirmed (N)
- **[severity]** [file:line] — [what's wrong] — [one-line fix]

## Refuted (N)
- [file:line] — [other model's claim] — [why it's wrong]

## Uncertain (N)
- [file:line] — [claim] — [what would settle it]

## Action plan
1. [Highest-severity confirmed item first]
2. ...
```

Prioritize confirmed items by severity, not by the order the other model presented them.
