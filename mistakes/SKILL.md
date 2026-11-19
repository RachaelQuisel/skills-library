---
name: mistakes
version: 1.0.1
description: Perform an evidence-based self-review of the assistant's (Claude's or Codex's) prior answer, plan, artifact, tool use, or claimed completion. Use when the user invokes `$mistakes` or `/mistakes`, asks "what mistakes did you make?", requests a self-audit or postmortem, challenges an earlier claim, or asks to identify, correct, or prevent errors in prior work.
---

# Mistakes

## Purpose in plain English

This skill helps you review an assistant's earlier work and identify mistakes supported by evidence.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Audit prior work without defensiveness, invented faults, or vague apologies. Identify what was actually wrong, explain the consequence, and turn each error into a concrete correction and prevention rule.

## Workflow

1. **Set the review scope.** Identify the user request, promised outcome, artifact or answer delivered, actions taken, and claims made. When the user does not specify an artifact, review the active or immediately preceding assistant work that prompted the request. If more than one plausible scope would materially change the audit, state the assumed scope or ask which work to review.
2. **Reconstruct the evidence.** Re-read the relevant conversation, source material, files, diffs, and tool results. Verify current state when the judgment depends on it. Do not guess from memory.
3. **Compare intent with result.** Check the work against explicit requirements, settled decisions, source evidence, safety constraints, and the definition of done.
4. **Classify each substantiated mistake.** Use the smallest applicable category:
   - Incorrect fact or calculation
   - Unsupported assumption presented as fact
   - Missed, changed, or over-expanded requirement
   - Incomplete execution or premature completion claim
   - Unsafe action or missing control
   - Data-model, architecture, or design inconsistency
   - Tool, skill, or process noncompliance
   - Communication that created the wrong mental model
5. **Explain each mistake completely.** State:
   - What the assistant said or did
   - Why it was wrong
   - The evidence
   - The practical impact
   - The correct answer or action
   - A reusable prevention rule
6. **Separate errors from uncertainty.** Label an unverified claim as unverified rather than wrong. Do not call a reasonable preference a mistake. Treat an accurately disclosed limitation, unmet dependency, or unavailable capability as a constraint or remaining unknown when the prior work did not claim completion. Treat it as a mistake only when the assistant concealed or misrepresented it, claimed completion despite it, or failed to use an available in-scope path. Never invent evidence, access, or capabilities to satisfy a requirement. State what evidence would resolve a genuine unknown.
7. **Correct only within scope.** If the user asks only for review, report the corrections without mutating systems or artifacts. If the user also asks for fixes, revise the authorized artifacts and verify the result before claiming completion.
8. **Run a final integrity check.** Confirm that every listed mistake has evidence, the largest-impact error appears first, no disclosed limitation is mislabeled as an error, no blame is shifted to the user or a tool, and no correction is described as completed unless it was actually performed.

## Output

Lead with the biggest mistake. If no mistakes are substantiated, say "No substantiated mistakes found." Omit the numbered list and `Remaining unknowns` unless an unknown could change the audit conclusion. When mistakes are substantiated, use every field in this structure. Keep `Why it was wrong` separate from `Evidence`; do not merge or omit fields.

```markdown
## Mistakes

1. **[Specific mistake]**
   - What I did:
   - Why it was wrong:
   - Evidence:
   - Impact:
   - Correction:
   - Prevention:

## Remaining unknowns

- [Unverified point and how to verify it]
```

Add a short corrected answer or artifact link when useful. Include what went right only when it prevents the user from discarding valid work; never use it to dilute accountability.

## Quality Bar

- Prefer specific evidence over tone or contrition.
- Name the exact claim, field, file, action, or omitted control.
- Distinguish factual error, uncertainty, and changed requirements.
- Explain consequences in the user's terms.
- Produce prevention rules that generalize beyond the current task.
- Avoid generic statements such as "I could have been clearer" unless the precise misleading wording and its effect are identified.
