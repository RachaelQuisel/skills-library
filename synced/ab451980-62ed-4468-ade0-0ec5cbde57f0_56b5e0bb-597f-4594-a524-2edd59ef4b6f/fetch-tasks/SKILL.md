---
name: fetch-tasks
description: >
  Fetch and bucket tasks from an XRAY Airtable base scoped to a specific client and date range. Use this skill whenever tasks need to be pulled from Airtable for Coding Clarified or AY Media. Trigger on: "get tasks", "pull tasks", "fetch tasks", "what tasks exist", "show me tasks", "look up tasks in Airtable", or any workflow that needs task data as input before building a summary or report. Always use this skill before build-sprint-summary.
---

# Fetch Tasks

Fetch tasks from the correct XRAY Airtable base, scoped to a client's projects and a date window. Returns bucketed task data ready for downstream skills.

---

## Reference Data

| Client           | Base ID           |
|------------------|-------------------|
| Coding Clarified | app6Fzai5bYEsgpA2 |
| AY Media         | appkqflDisG7M8qnp |

**Tables (same IDs in both bases):**
- Tasks: `tblWUk9EExKgdEF32`
- Projects: `tblbikChpLglvICKT`

---

## Step 1 — Confirm Inputs

Before fetching, confirm:
1. Client name (Coding Clarified or AY Media)
2. Date range — start and end dates (accept natural language: "last week", "Feb 24–Mar 7")
3. Optional: specific project name to narrow scope

---

## Step 2 — Scope to Client Projects

Both bases contain tasks for ALL XRAY clients. Always scope by project first or results will include unrelated clients.

Query `tblbikChpLglvICKT`:
- Filter: Archive (`fldKnC98GrcQfdMMD`) = false
- Filter: XRay's Client (`fldBH7eAi8IFPhQ63`) contains the client name
- Collect returned record IDs — these are the allowed project IDs

If a specific project was requested, narrow to just that project's record ID.

---

## Step 3 — Fetch Tasks (Two Queries, Deduplicate)

⚠️ The Airtable MCP does not support nested OR inside AND filters. Run two separate queries and deduplicate by record ID in memory.

**Query A** — tasks due within the window:
- Archived (`fldKb6YVkBaHr5RJT`) = false
- Due date (`fld9dlnRARAXWLB8o`) within date range
- Project (`fldqbQ7QJxRICA8EM`) in client project IDs

**Query B** — tasks completed within the window:
- Archived (`fldKb6YVkBaHr5RJT`) = false
- Actually Completed Date (`fldQV0HJQWFXIXge2`) within date range
- Project (`fldqbQ7QJxRICA8EM`) in client project IDs

Merge both result sets. Remove duplicates by record ID.

**Fields to fetch:**

| Field ID          | Field Name              |
|-------------------|-------------------------|
| fldTFUlrMvxCc4ebA | Task name               |
| fldoGv24RwYziP3lB | Status                  |
| fld5b8iYLQeOcaqCt | Priority                |
| fldwPp3N6rdH7T9td | Assigned To             |
| fld9dlnRARAXWLB8o | Due date                |
| fldQV0HJQWFXIXge2 | Actually Completed Date |
| fldEWFax1tOeJptbs | Hours Estimated         |
| fld04pfo10D69GVF9 | Hours Used              |
| fldqbQ7QJxRICA8EM | Project (linked)        |
| fldPjiUTSQEt5MXx9 | Done (checkbox)         |
| fldmleigTjw1gsp3q | Estimated Done Date     |

---

## Step 4 — Bucket Tasks

Sort deduplicated results into these groups:

- 🔄 **In Progress** — Status = "In Progress"
- ⚠️ **At Risk** — In Progress AND Due date < today
- ✅ **Done** — Status = "Done" OR Done checkbox = true
- 📋 **Carried** — Status = "Backlog" or "Ready to Start"
- ❌ **Cancelled** — Status = "Cancelled" (count only)

---

## Output

Return bucketed task lists and raw records. Pass to build-sprint-summary, write-artifact, or any downstream skill that needs task data. State counts per bucket clearly.
