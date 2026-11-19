---
name: create-plan
description: Generate a structured markdown implementation plan with progress tracking. Use after exploration is complete and before coding begins.
---
# Plan Creation Stage

Based on the full exchange, produce a markdown plan document.

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
