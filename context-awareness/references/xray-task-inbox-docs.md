# XRAY Task Inbox — Documentation

[XRAY Task Inbox](/)

[About](/docs.html) [API Reference](/api-docs.html)

## XRAY Task Inbox

A centralized triage inbox for all work requests at XRAY. Tasks land here from humans, AI agents, and automations — then get reviewed, enriched, and routed to projects.

## How It Works

Every task enters the inbox with `Status = "Backlog"` and `Triage Status = "New"`. The assignee reviews each task and takes one of three actions:

* **Accept** — links the task to a project and marks it as accepted
* **Reject** — provides a reason and removes it from the inbox
* **Needs More Info** — requests clarification before deciding

Tasks can also be marked **Done** directly from the inbox for quick-win items, or **Enriched** with additional details (due date, hours estimate, reassignment, project link).

## Task Lifecycle

| Stage | Status | Triage Status | What Happens |
|-------|--------|---------------|--------------|
| New request | Backlog | New | Appears in inbox for triage |
| Accepted | Backlog | Accepted | Linked to project, ready for work |
| Rejected | Backlog | Rejected | Reason recorded, removed from inbox |
| Needs info | Backlog | Needs More Info | Clarification requested |
| Done | Done | Accepted | Completed and archived |

## Minimum Required Fields

| Field | Type | Requirement | Notes |
|-------|------|-------------|-------|
| `title` | Text | Required, max 120 chars | Clear, actionable task title |
| `origin` | Select | Defaults to `"Human"` | One of: `Human`, `AI Agent`, `Automation` |
| `assignedTo` | Email | Defaults to current user | Who will triage/execute this task |

`Status` and `Triage Status` are set automatically to `"Backlog"` and `"New"`.

## Recommended Fields

| Field | Type | Purpose |
|-------|------|---------|
| `description` | Text (max 500 chars) | 1-3 sentences on the "what" and "why" |
| `priority` | Select | `Normal` (default), `High` (today), `Urgent` (blocking) |
| `originDetail` | Text | Who/what specifically created this (e.g., "Claude Code", "Mark via Slack") |
| `project` | Record ID | Pre-link to a project if known — saves triage time |
| `dueDate` | Date (YYYY-MM-DD) | Only if there's a real deadline |

## Enrichment Fields

After creation, tasks can be enriched with additional detail via the Enrich button or PATCH API:

| Field | Type | Purpose |
|-------|------|---------|
| `dueDate` | Date | When the task should be completed |
| `startDate` | Date | When work should begin |
| `hoursEstimated` | Number | Estimated effort in hours |
| `assignedTo` | Email | Reassign to a different team member |
| `project` | Record ID | Link to an XRAY project |
| `description` | Text | Add or update the task description |

## Authentication

The Task Inbox supports two authentication methods:

* **Google OAuth (web users)** — Sign in with your `@xray.tech` Google account. Sessions last 7 days.
* **API Key (machine clients)** — For automations, AI agents, and scripts. See the [API Reference](/api-docs.html) for details.
