---
name: prd-to-issues
version: 1.0.1
description: Break a PRD into independently-grabbable GitHub issues using tracer-bullet vertical slices. Use when user wants to convert a PRD to issues, create implementation tickets, break down a PRD into work items, or mentions "PRD to issues".
tags:
  - skill
---

# PRD to Issues

## Purpose in plain English

This skill helps you turn a product requirements document into separate GitHub issues that each deliver a useful result.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Break a PRD into independently-grabbable GitHub issues using vertical slices (tracer bullets).

## What "tracer bullet" / "vertical slice" means

A **vertical slice** cuts through every layer of the system — schema, API, business logic, UI, tests — and delivers one small, complete behavior end-to-end. A **horizontal slice** does the opposite: all the schemas first, then all the APIs, then all the UI. Horizontal slices feel productive but produce nothing demoable until the last layer is done.

A **tracer bullet** is the original term (Pragmatic Programmer): the first thin vertical slice. It's not a stub or a prototype — it's real code, just narrow. You fire it to verify your aim, then fire more. Each subsequent slice adds one more behavior end-to-end.

Prefer many thin slices over few thick ones, because each thin slice is independently mergeable, independently demoable, and independently reversible if it's wrong.

## Process

### 1. Locate the PRD

Ask the user for the PRD GitHub issue number (or URL). If the PRD is not already in context, fetch it with `gh issue view <number>`.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code.

### 3. Draft vertical slices

Break the PRD into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

Slices may be 'HITL' (human-in-the-loop, requires human interaction like an architectural decision or design review) or 'AFK' (can be implemented and merged without human interaction). Prefer AFK over HITL where possible.

- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Prefer many thin slices over few thick ones

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Type**: HITL / AFK
- **Blocked by**: which other slices (if any) must complete first
- **User stories covered**: which user stories from the PRD this addresses

Ask the user:
- Does the granularity feel right?
- Are the dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked as HITL and AFK?

Iterate until the user approves the breakdown.

### 5. Create the GitHub issues

For each approved slice, create a GitHub issue using `gh issue create`. Create issues in dependency order (blockers first) so you can reference real issue numbers.

<issue-template>
## Parent PRD

#<prd-issue-number>

## What to build

A concise description of this vertical slice. Describe end-to-end behavior, not layer-by-layer implementation. Reference specific sections of the parent PRD rather than duplicating content.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Blocked by

- Blocked by #<issue-number> (if any)

Or "None - can start immediately" if no blockers.

## User stories addressed

Reference by number from the parent PRD:

- User story 3
- User story 7

</issue-template>

Do NOT close or modify the parent PRD issue.
