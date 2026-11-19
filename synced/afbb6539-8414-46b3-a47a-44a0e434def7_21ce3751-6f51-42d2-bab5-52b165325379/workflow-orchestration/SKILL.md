---
name: workflow-orchestration
description: Enforce disciplined development methodology for any non-trivial coding or architecture task. This is about HOW to work — not the plan format. Use this skill whenever the user asks to build, fix, refactor, or implement anything involving 3+ steps, architectural decisions, or multi-file changes. Also trigger when the user mentions "plan mode," references tasks/lessons.md, when a coding task starts going sideways, or when a bug report comes in. This keeps work verified, documented, and self-improving.
---

# Workflow Orchestration

Discipline for non-trivial coding work. This skill governs HOW you work, not what you produce.

## When to Trigger

- Any task with 3+ steps or architectural decisions
- Multi-file changes
- User says "plan mode" or references `tasks/lessons.md`
- A coding task starts going sideways
- Bug reports come in
- Refactoring or debugging complex systems

## 1. Plan Mode Default

Enter plan mode for ANY non-trivial task.

- Write plan to `tasks/todo.md` with checkable items before touching code
- Check in with user before starting implementation
- If something goes sideways: STOP and re-plan immediately (don't keep pushing)
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

Plan mode is not optional for tasks that qualify. Skip it only for obvious, single-step fixes.

## 2. Subagent Strategy

Use subagents liberally to keep main context window clean.

- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution
- Use subagents for:
  - Exploring unfamiliar codebases
  - Running tests in parallel
  - Researching API docs or error messages
  - Analyzing logs

## 3. Self-Improvement Loop

After ANY correction from the user: update `tasks/lessons.md`.

Format for lessons:
```markdown
## [Date] - [Short Description]
**Trigger:** What caused the mistake
**Pattern:** The underlying bad habit
**Rule:** What to do instead
```

- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant projects
- Lessons are cumulative; don't delete old ones

## 4. Verification Before Done

Never mark a task complete without proving it works.

- Run the code; don't just write it
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness
- For UI changes: describe what you see or take a screenshot
- For API changes: show the request/response

## 5. Demand Elegance (Balanced)

For non-trivial changes: pause and ask "is there a more elegant way?"

- If a fix feels hacky, step back: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes (don't over-engineer)
- Challenge your own work before presenting it
- Red flags that demand elegance check:
  - You're adding a workaround
  - You're copying code instead of abstracting
  - The fix is longer than 20 lines
  - You're not sure why the original approach failed

## 6. Autonomous Bug Fixing

When given a bug report: just fix it.

- Point at logs, errors, failing tests, then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how
- Don't ask for hand-holding on debugging steps
- Report back with: what was wrong, what you did, how you verified it

## Task Management Workflow

1. **Plan First:** Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan:** Check in before starting implementation
3. **Track Progress:** Mark items complete as you go
4. **Explain Changes:** High-level summary at each step
5. **Document Results:** Add review section to `tasks/todo.md`
6. **Capture Lessons:** Update `tasks/lessons.md` after corrections

### todo.md Template

```markdown
# [Feature/Bug Name]

## Status
- [ ] Planning
- [ ] In Progress
- [ ] Verification
- [ ] Done

## Tasks
- [ ] Task 1
  - [ ] Subtask 1a
  - [ ] Subtask 1b
- [ ] Task 2

## Review
[Add after completion: what worked, what didn't, verification results]
```

### lessons.md Template

```markdown
# Lessons Learned

## [Date] - [Short Description]
**Trigger:** What caused the mistake
**Pattern:** The underlying bad habit  
**Rule:** What to do instead

---
```

## Core Principles

**Simplicity First**
Make every change as simple as possible. Impact minimal code. If you're writing more than you expected, pause and reconsider.

**No Laziness**
Find root causes. No temporary fixes. Senior developer standards. "It works" is not the same as "it's correct."

**Minimal Impact**
Changes should only touch what's necessary. Avoid introducing bugs by changing unrelated code. Scope creep is a bug.

## When to Break These Rules

- Urgent production issues: skip plan mode, fix it, then document
- User explicitly says "just do it" or "skip the plan"
- Trivial changes (typo fixes, single-line config changes)

Even when breaking rules, still verify before done.
