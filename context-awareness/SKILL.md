---
name: context-awareness
version: 1.0.1
description: Monitors conversation length and context drift; produces a session handoff document so a new chat can resume cleanly. Use when the conversation has grown across many tool calls, the user starts repeating themselves, token usage is high, earlier context is slipping, or the user explicitly says "wrap up", "create a handoff", "store context", "continue later", or "end the session".
tags:
  - skill
---

# Context Awareness & Session Handoff

## Purpose in plain English

This skill helps you prepare a clear handoff so an interrupted or lengthy conversation can continue with its important context.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


This skill enables you to monitor the length of conversational context, prevent drift, and neatly package up working sessions so that a new session can resume exactly where you left off.

## When to Use

- When the conversation has extended across multiple large tasks or numerous tool calls.
- When you begin struggling to remember earlier context or the user has to correct you often due to context drop-off.
- When the user explicitly requests to "wrap things up," "create a handoff," "store context," or "continue later."

## 1. Suggesting Wrap-Up

If you notice signs of conversational drift or excessive context length, proactively ask the user:
> "I notice our session has gotten quite long, which can impact my ability to keep all the context straight. Would you like me to wrap things up and create a handoff document so we can start fresh in a new session?"

## 2. Session Wrap-Up Protocol

Once the user agrees to wrap up or requests a handoff, follow this exact checklist:

1. **Reconcile Temporary State**
   - Ensure any temporary scripts in `/tmp` have either been discarded or moved to the project's codebase.
   - Verify that any important insights have been memorialized in permanent project documentation (`docs/`, `task.md`, `walkthrough.md`, etc.).

2. **Document Changes**
   - Summarize the final state of the changes you made in this session.
   - Ensure the user's `task.md` (or equivalent checklist artifact) has been updated with checked-off items reflecting what was accomplished.

## 3. Creating the Handoff Document

Create a markdown artifact named `session_handoff.md` (save it either in the project's root or the `.agents/` or `artifacts/` folder, depending on the workspace standard). The handoff document must include:

### Primary Objective
Summarize the high-level goal of this working session.

### Decisions Made & Why
List the crucial technical or product decisions made, explicitly capturing the *why* so the next instance doesn't have to rethink them.

### Remaining Loose Ends / Outstanding Tasks
Clearly list what was NOT finished and what exactly needs to happen next.

### Continue Prompt (Copy & Paste)
Provide a literal block of text explicitly labeled for the user to copy and paste into the *new* session.

**Format example:**
```markdown
# Session Handoff

## Primary Objective
[Objective summary]

## Decisions Made
- **[Decision]**: [Why]

## Outstanding Tasks
- [ ] [Task 1]

## Continue Prompt
Please copy and paste the following prompt into your next session:

> **PROMPT**: "Please read `session_handoff.md`. We are working on [Objective]. Pick up exactly where we left off, starting with [Outstanding Task 1]."
```

## 4. Final Notification
After creating the `session_handoff.md`, use the `notify_user` tool to tell the user:
1. The wrap-up is complete.
2. The handoff document is ready.
3. They should copy the "Continue Prompt" from the bottom of the handoff document and use it in a fresh chat.
