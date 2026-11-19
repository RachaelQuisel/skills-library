---
name: fetch-tasks
version: 1.4.6
description: "Fetch tasks from the XRAY task hub (base appQAdxI2hDNJj1g5), scoped to a client and an optional date window. Use when Rachael asks for her tasks, a client's open tasks, a sprint window, \"what's open for [client]\", or when a downstream skill such as build-sprint-summary or todays-focus needs task data. Client-agnostic: it confirms the client and never assumes a client list."
---

# Fetch Tasks

## Purpose in plain English

This skill helps you collect a named client's tasks for the requested period and organize them for review.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Fetch tasks from the XRAY task hub, scoped to a client and an optional date window. Return bucketed task data for downstream skills such as build-sprint-summary, write-artifact, and todays-focus. This skill is client-agnostic. It never carries a client list of its own.

---

## Reference data: the task hub

All client work tracks in one base, the XRAY Daily hub:

- Base: `appQAdxI2hDNJj1g5`
- Tasks table: `tblvlJq7I2GvIQEyP`
- Projects table: `tblOaFlYpPXlHrT2c`
- Clients table: `tblVS1aUCNeqtVq5U`

**Task fields:**

| Field ID | Name |
|---|---|
| fld1AkoHwZc1n9ynS | Task (name) |
| fldxcjBLLGOur6XIy | Status |
| fldyqG9AcucrbXGPX | Priority |
| fld5LMZiISyZTKL0T | Due date |
| fldOEY1wIsL75C79u | Actually Completed Date |
| fldkE6egQcmDBTiiV | Done (checkbox) |
| fldCD9gdIan9M8wmV | Archived (checkbox) |
| fldcBv034WdlpqPrC | Client (lookup from Project) |
| fldSBK8vvP15UMCyi | Project name (lookup) |
| fldA8WINLYYeMcJV2 | Project (link) |

**Status choice IDs.** The hub shares these across tables: Done `sel0PYWt8CwW33uDS`, Cancelled `selmjxxV4n4rLJCow`, Backlog `selAVcMgmMQklSZCa`, Ready to Start `selr8dlfSeLEqYpE3`, In Progress `sele5WlQHUv2YWmkB`, Blocked `selqRQEolk8KKxFgy`.

---

## Step 1: Confirm the client

Never assume a client list. If Rachael named the client, use that name. Otherwise ask her, or list the active client names from the Clients table. The Clients table is `tblVS1aUCNeqtVq5U` and its Status field is `fldkwxVVW7PxsEdQM`. If a named client does not appear in the hub, say so and stop. Do not fall back to a base from memory.

## Step 2: Fetch open tasks

Run one query on the Tasks table with these filters:
- Done (`fldkE6egQcmDBTiiV`) is false.
- Archived (`fldCD9gdIan9M8wmV`) is false.
- Status is none of Done and Cancelled.
- The Client lookup (`fldcBv034WdlpqPrC`) contains the client name.

For a date window, filter on Due date or Actually Completed Date within the range. The Airtable MCP does not support nested OR inside AND. Run two queries and deduplicate by record ID.

Use pageSize 1000. If the response has a nextCursor, keep paging until it does not.

## Step 3: Bucket

- In Progress: Status is "In Progress".
- At Risk: Status is "In Progress" or "Ready to Start" and the Due date is before today.
- Blocked: Status is "Blocked". List these first. Each one is a decision waiting on someone.
- Carried: Status is "Backlog" or "Ready to Start".
- Done and Cancelled: count only, and only when a date window was requested.

## Step 4: Hygiene check

Always run this check. Report the results. Never change a record without approval. Flag:
- Tasks where Status is "Done" and the Done checkbox is false, or the reverse.
- Duplicate task names within the same project.
- Tasks with no name.
- Tasks with no project link.

## Output

State the count for each bucket. List the Blocked and At Risk tasks in full. Summarize the hygiene flags. Pass the raw records to any downstream skill that asks.
