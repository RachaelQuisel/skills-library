---
name: puzzle-prompt-builder
version: 1.0.1
description: "Transform SOPs, transcripts, process descriptions, or workflow documentation into structured prompts ready to paste into Puzzle.io's Nova AI agent. Use when the user wants to build a Puzzle workflow, convert an SOP for Puzzle, create a Nova prompt, map a process in Puzzle, or says 'Puzzle prompt', 'Nova prompt', 'build this in Puzzle', 'map this process'."
tags:
  - skill
---

# Puzzle Prompt Builder

## Purpose in plain English

This skill helps you turn a process description into a structured request for Puzzle's Nova assistant.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Take source material (SOPs, transcripts, process docs, CSV data) and produce a structured prompt the user can paste into Puzzle.io's Nova AI agent.

## Workflow

1. Receive source material from the user
2. Ask clarifying questions if roles, tools, or section groupings are ambiguous
3. Ask how many sections they want (recommend fewer — default to 1 for simple processes)
4. Ask if any roles, teams, or tools exist in their Puzzle workspace (use exact names to avoid duplicates)
5. Generate a Nova prompt using the template below
6. Present it in a code block for copy-paste

## Prompt Rules

- Specify section count explicitly in the prompt — Nova over-creates sections without it
- Include the "analyze first" instruction (first line of the template) so Nova converses before building
- Define every step field — partial info produces partial results
- Put connections last — instruct Nova to create all steps, then connect them
- Specify layout direction — default to horizontal unless the user prefers vertical
- Reference existing workspace objects by exact name to prevent duplicates
- Use Puzzle's native step types: `task`, `conditional` (for decisions), `signal` (for triggers/automations), `form` (for approvals/signatures)
- Use `Draft` as the default status (not "Not Started" — that's not a valid Puzzle status)
- Steps executed by automations or external parties (e.g., clients) may have no executor role — leave executor blank for these

## Template

```
Before you generate the diagram, analyze this prompt and give me the steps you're going to build first, then I'll approve.

Process name: [name of the workflow]
Layout: [Horizontal, flowing left to right | Vertical, flowing top to bottom]
Sections: I want exactly [N] section(s): [list ordered sections, e.g. "1. Intake, 2. Review, 3. Approval"]

For each step, define:
- Step name: [step label]
- Section: [which section it belongs to]
- Type: [task | conditional | signal | form]
- Status: [Draft | In Progress | Done | Blocked]
- Executor role: [role responsible for completing this step]
- Tools used: [software/systems involved]
- Notes: [any important context or instructions]
- Connects to: [next step(s) in the flow]

Teams to create: [list teams]
Roles to create: [role name -> team it belongs to]
Tools to add to workspace: [tool names]

After creating all steps, add the connections between them.
```

## Cross-Canvas Relationships

Nova has 4 canvases. Include team/tool creation in the prompt so Nova links them cross-canvas:

- **Workflow Canvas** — sections, steps, connections
- **Team Canvas** — teams and roles (assigned to steps via `add_step_roles`)
- **People Canvas** — people linked to roles (People -> Role -> Step, not directly to steps)
- **Tool Canvas** — software catalog (assigned to steps)

## References

- **Field names and valid values**: [references/field-reference.md](references/field-reference.md)
- **Nova tips, canvas commands, and troubleshooting**: [references/nova-tips.md](references/nova-tips.md)

## Example

**Source material:**
"When a new client signs, the Account Manager sends a welcome email, then the Onboarding Specialist schedules a kickoff call. After the call, the client fills out a setup questionnaire. An automation checks if the client is enterprise or standard. If enterprise, the Onboarding Specialist sets up their workspace in Notion. The Account Manager does a 30-day check-in."

**Output:**

```
Before you generate the diagram, analyze this prompt and give me the steps you're going to build first, then I'll approve.

Process name: Client Onboarding
Layout: Horizontal, flowing left to right
Sections: I want exactly 1 section: 1. Client Onboarding

Steps:

- Step name: Send Welcome Email
  Section: Client Onboarding
  Type: task
  Status: Draft
  Executor role: Account Manager
  Tools used: Gmail
  Notes: Send within 24 hours of contract signing
  Connects to: Schedule Kickoff Call

- Step name: Schedule Kickoff Call
  Section: Client Onboarding
  Type: task
  Status: Draft
  Executor role: Onboarding Specialist
  Tools used: Google Calendar
  Notes: Schedule within first week
  Connects to: Client Setup Questionnaire

- Step name: Client Setup Questionnaire
  Section: Client Onboarding
  Type: form
  Status: Draft
  Executor role:
  Notes: Client fills out setup questionnaire after kickoff call
  Connects to: Check Client Tier

- Step name: Check Client Tier
  Section: Client Onboarding
  Type: conditional
  Status: Draft
  Executor role:
  Notes: Automation checks if client is enterprise or standard tier
  Connects to: Set Up Workspace, 30-Day Check-In

- Step name: Set Up Workspace
  Section: Client Onboarding
  Type: task
  Status: Draft
  Executor role: Onboarding Specialist
  Tools used: Notion
  Notes: Enterprise clients only. Use client workspace template.
  Connects to: 30-Day Check-In

- Step name: 30-Day Check-In
  Section: Client Onboarding
  Type: task
  Status: Draft
  Executor role: Account Manager
  Tools used: Gmail
  Notes: Review onboarding progress and gather feedback
  Connects to: None

Teams to create: Client Success
Roles to create: Account Manager -> Client Success, Onboarding Specialist -> Client Success
Tools to add to workspace: Gmail, Google Calendar, Notion

After creating all steps, add the connections between them.
```

## Output Format

Present the final prompt in a code block. Add a brief note above it summarizing what the prompt will build.
