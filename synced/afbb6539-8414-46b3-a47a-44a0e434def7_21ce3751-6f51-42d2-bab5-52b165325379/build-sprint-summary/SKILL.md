---
name: build-sprint-summary
description: >
  Take bucketed task data and format it into a structured sprint summary. Use this skill whenever task data has been fetched and needs to be turned into a readable sprint summary. Trigger on: "build the summary", "format the summary", "write up the sprint", "generate the sprint report", "turn this into a summary", or any request to produce a formatted sprint output from task data. Always leads with in-progress and at-risk tasks — not velocity.
---

# Build Sprint Summary

Format bucketed task data into a structured sprint summary. Leads with what needs attention.

---

## Inputs Required

- Client name
- Sprint start and end dates
- Bucketed task data: In Progress, At Risk, Done, Carried, Cancelled (from fetch-tasks or equivalent)
- Hours Used values for Done tasks (if available)

---

## Step 1 — Compute Metrics

- **Velocity** = count of Done tasks
- **Completion rate** = Done ÷ (Done + In Progress + Carried) as %
- **At-risk count** = In Progress tasks where Due date < today
- **Hours logged** = sum of Hours Used for Done tasks — omit entirely if mostly empty

---

## Step 2 — Format the Summary

Lead with what needs attention. Use this exact template:

```
Sprint Summary: [Start Date] – [End Date]
Client: [Client Name]

🔄 In Progress ([N] tasks — [N] at risk)
  ⚠️ [Task name] · [Project] · Due [date] · OVERDUE
  • [Task name] · [Project] · Due [date]

✅ Completed ([N] tasks)
  • [Task name] · [Project]

📋 Carried to Next Sprint ([N] tasks)
  • [Task name] · [Project]

📊 Velocity: [N] tasks | Completion rate: [N]%
   Hours logged: [N] hrs
```

**Rules:**
- Mark overdue In Progress tasks with ⚠️ and "OVERDUE"
- Omit Hours logged line if Hours Used is sparsely populated
- If any bucket exceeds 10 tasks, show top 10 by priority and append "...and [N] more"
- Sort In Progress by due date ascending (most overdue first)
- Sort Done by Actually Completed Date descending (most recent first)

---

## Output

Return the formatted summary text. Ready to pass to write-artifact and/or post-to-huddle.
