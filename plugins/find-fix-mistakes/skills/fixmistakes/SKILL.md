---
name: fixmistakes
version: 1.0.4
description: Repair substantiated mistakes from the assistant's latest self-review and verify the corrections. Use after the mistakes skill hands off an audit, when the user invokes /fixmistakes, @fixmistakes, or $fixmistakes, or asks to fix mistakes identified in prior work. Respect an explicit audit-only request and the original task's authorization boundaries.
---

# Fix Mistakes

The user's explicit instructions take precedence over this skill's guidelines.

Turn an evidence-based audit into completed corrections. Fix what is demonstrably wrong, preserve valid work, and report what the verification actually proves.

## Use the audit and existing authorization

Read the latest mistakes report and the underlying request, decisions, artifacts, and tool results. Carry forward each finding's identity, evidence, correction, and original task scope. If there is no audit, reconstruct a focused finding from the supplied evidence; do not call mistakes recursively.

Check the current state before changing anything. Classify a finding as already corrected when fresh evidence proves it. Treat uncertainty, accurately disclosed limitations, and preferences as such; do not invent repairs for them.

This workflow authorizes routine corrections within the user's original task and settled instructions. Continue without repeated permission for authorized actions and reversible repairs. Honor audit-only requests, cancellation, ownership handoffs, and narrower scope. Obtain only the authorization genuinely missing for an action outside that scope. A self-review does not grant permission to send messages, publish, merge, delete data, or change access when those actions were never authorized.

## Correct and verify

1. Prioritize the finding with the greatest practical impact. Make the smallest correction that resolves it. Preserve unrelated edits, original failure evidence, required tests, owner decisions, and baselines that signal real changes.
2. Use the supported interface for the affected resource. Read the tool contract or official instructions before invoking a validator, endpoint, or mutation. Check for newer edits and use expected versions or head SHAs where supported. Inspect an error before retrying; stop after three unsuccessful attempts per step and report the concrete blocker.
3. Correct misleading or incomplete answers in the conversation. Name what was wrong and provide the corrected result. A past communication delay cannot be undone; improve the current handoff and state the prevention rule without claiming the past delay was fixed.
4. Verify each correction against its original failure condition. Use the required environment and full applicable checks. For CI, distinguish a newly completed run from a fetched historical result. Record the immutable source SHA, location, runtime, run or artifact link, and actual failures, skips, and missing cases. Do not label local tests as cloud CI or metadata validation as behavioral validation.
5. Keep updates useful during ongoing work. If a delegated task requests status, deliver it through an available authorized channel and confirm delivery. If that channel fails, return a concise final handoff promptly rather than silently continuing remote changes. Preserve completed work and explicit outstanding steps.
6. Read back external changes or inspect the saved artifact. Claim a fix only after the evidence confirms the intended result. Passing offline checks does not establish live compatibility, deployment, installation, or picker visibility.

## Return the result

Report each finding as **fixed and verified**, **already corrected**, or **blocked**. Include what changed and the evidence needed to assess it. For a blocker, give the exact missing capability or authorization and one next step. Describe process improvements as prevention, not as a retroactive correction of past events.

Finish with the corrected deliverable or answer, affected links, and any material verification limits. Do not end with another promise to fix findings that are already authorized and feasible. Do not invoke mistakes again automatically; avoid review-repair loops.
