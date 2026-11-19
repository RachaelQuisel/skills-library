---
name: create-issue
version: 1.0.1
description: Capture bugs, features, or improvements quickly while the user is mid-development. Create complete issues with all necessary details in under 2 minutes.
tags:
  - skill
---

# Create Issue

## Purpose in plain English

This skill helps you turn a reported problem or improvement into a clear GitHub issue.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


User is mid-development and thought of a bug/feature/improvement. Capture it fast so they can keep working.

## Your Goal

Create a complete issue with a clear title, the right body shape for the archetype (see below), and proper type/priority/effort labels.

## Two Archetypes

**Code / feature issue** (a bug, a feature ask, a refactor — audience is a code reviewer):
- TL;DR
- Current behavior vs expected behavior
- Relevant files that need touching
- Risk / notes if applicable

**Process / operational issue** (permissions gap, infra friction, onboarding bottleneck — audience is a stakeholder like a CTO, PM, or platform owner):
- What blocked me (concrete, first-person)
- Diagnostic evidence inline (paste raw API output, error messages, perm tables in a fenced code block — don't paraphrase)
- Suggested fix (one or two specific actions, not architecture opinions)
- Related (cross-reference other issues with `#N` so they're tracked together)

Pick the archetype before drafting. If unsure, the body shape will tell you — code-shape questions need code-shape answers, process-shape questions don't.

## Voice

If the audience is a stakeholder (CTO, PM, client, teammate) and not a code reviewer, write the issue in **first person** ("I ran into...", "I couldn't push...") not third-person Claude-analysis voice. Per `feedback_first_person_when_drafting_for_rachael` — the issue is going out under Rachael's name.

## Filing — Permissions and Syntax

- **Org members with `pull: true` on a private repo CAN open issues** in most setups, even without push. Don't pre-emptively fall back; just try.
- Canonical filing: `gh issue create --repo OWNER/REPO --title "..." --body "..."`. Use `--body "$(cat <<'EOF' ... EOF)"` for multi-line bodies with code blocks.
- If creation does fail, fall back to a repo where you have admin and add a one-line note in the body explaining the fallback — that's evidence reinforcing the permission issue itself.

## How to Get There

**Ask questions** to fill gaps - be concise, respect the user's time. They're mid-flow and want to capture this quickly. Usually need:
- What's the issue/feature
- Current behavior vs desired behavior
- Type (bug/feature/improvement) and priority if not obvious

Keep questions brief. One message with 2-3 targeted questions beats multiple back-and-forths.

**Search for context** only when helpful:
- Web search for best practices if it's a complex feature
- Grep codebase to find relevant files
- Note any risks or dependencies you spot

**Skip what's obvious** - If it's a straightforward bug, don't search web. If type/priority is clear from description, don't ask. **If the issue body is already drafted in conversation** (e.g., you're filing items from a feedback message), skip the question phase entirely — confirm repo + title only, then file.

**Keep it fast** - Total exchange under 2min. Be conversational but brief. Get what you need, create ticket, done.

## Behavior Rules

- Be conversational - ask what makes sense, not a checklist
- Default priority: normal, effort: medium (ask only if unclear)
- Max 3 files in context - most relevant only
- Bullet points over paragraphs
