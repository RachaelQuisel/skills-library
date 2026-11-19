---
name: sprint-summary
description: >
  Generate a complete sprint summary from live Airtable data, save it to the Artifacts table, and post it to the client's Slack huddle channel. Use this skill any time the user wants to review, wrap up, or report on a sprint. Trigger on: "sprint summary", "summarize this sprint", "end of sprint", "last sprint recap", "what did we get done", "weekly summary", "how did the sprint go", "wrap up the sprint", "what's the velocity", or any request to review completed vs. in-progress work for a time period. Orchestrates: fetch-tasks → build-sprint-summary → write-artifact → post-to-huddle.
---

# Sprint Summary

Orchestrates a full sprint summary end-to-end. Runs four sub-skills in sequence.

---

## Sequence

1. **fetch-tasks** — pull and bucket tasks for the client + date range
2. **build-sprint-summary** — format the bucketed data into a structured summary
3. **write-artifact** — save the summary to the Artifacts table (confirm before writing)
4. **post-to-huddle** — post a condensed version to the client's Slack channel (confirm before posting)

---

## Step 1 — Gather Parameters

Ask for:
1. Client (Coding Clarified, AY Media, or both)
2. Sprint start and end dates — accept natural language ("last week", "Feb 24–Mar 7")
3. Optional: specific project to scope to

Do not fetch anything until client + date range are confirmed.

---

## Step 2 — Run fetch-tasks

Follow the fetch-tasks skill. Return bucketed counts before continuing.

---

## Step 3 — Run build-sprint-summary

Follow the build-sprint-summary skill. Show the full formatted summary to the user.

---

## Step 4 — Run write-artifact

Follow the write-artifact skill. Show the record preview and ask for confirmation before writing.

---

## Step 5 — Run post-to-huddle

Follow the post-to-huddle skill. Show the Slack-formatted message and ask for confirmation before posting.

---

## Guardrails

- Never skip the confirmation steps in write-artifact or post-to-huddle
- If the user only wants some steps (e.g. "just build the summary, don't post"), skip the rest
- If no tasks match the date window, say so and ask if dates need adjusting before continuing
