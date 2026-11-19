---
name: create-plan
version: 1.0.1
description: Generate a lightweight markdown execution plan with emoji status tracking and a live progress percentage, ready to hand off to `execute`. Use when the user says "create a plan", "write me a plan", "plan this out", "plan mode", or after `brainstorming` / `align` has produced enough clarity to commit to steps. This is the lightweight planning step in the align → create-plan → execute → deliver loop; for a full PRD use `five-signals-prd` or `write-a-prd`, and for breaking a PRD into phases use `prd-to-plan`.
tags:
  - skill
---
# Plan Creation Stage

## Purpose in plain English

This skill helps you write a practical work plan with steps and visible progress tracking.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Based on the full exchange, produce a markdown plan document. Not time to build yet — this stage exists to make the build phase boring.

## Why the structure looks like this

- **Emoji tracker** so progress is visible at a glance and the file works as a status dashboard during `execute`.
- **No extra scope** because anything beyond what was discussed is speculation, and speculation in a plan turns into half-built code.
- **Concrete steps** because vague steps ("set up the data layer") collapse during execution; precise steps ("add `bookings` table with fields X, Y, Z") survive.
- **Critical decisions captured up front** so the build phase doesn't re-litigate choices already made.

## Requirements

- Include clear, minimal, concise steps
- Track status of each step using these emojis:
  - 🟩 Done
  - 🟨 In Progress
  - 🟥 To Do
- Include dynamic tracking of overall progress percentage (at top)
- Do NOT add extra scope or unnecessary complexity beyond explicitly clarified details
- Steps should be modular, elegant, minimal, and integrate seamlessly within the existing codebase

## Behavior Rules

- Still NOT time to build yet - just write the plan document
- No extra complexity or scope beyond what was discussed
- Keep steps actionable and specific

## Markdown Template

```markdown
# Feature Implementation Plan

**Overall Progress:** `0%`

## TLDR
Short summary of what we're building and why.

## Critical Decisions
Key architectural/implementation choices made during exploration:
- Decision 1: [choice] - [brief rationale]
- Decision 2: [choice] - [brief rationale]

## Tasks:

- [ ] 🟥 **Step 1: [Name]**
  - [ ] 🟥 Subtask 1
  - [ ] 🟥 Subtask 2

- [ ] 🟥 **Step 2: [Name]**
  - [ ] 🟥 Subtask 1
  - [ ] 🟥 Subtask 2
```
