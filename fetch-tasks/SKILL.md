---
name: fetch-tasks
version: 1.4.8
description: "Fetch tasks from the XRAY task hub (base appExample0000004), scoped to a client and an optional date window. Use when Rachael asks for her tasks, a client's open tasks, a sprint window, \"what's open for [client]\", or when a downstream skill such as build-sprint-summary or todays-focus needs task data. Client-agnostic: it confirms the client and never assumes a client list."
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

- Base: `appExample0000004`
- Tasks table: `tblExample0000010`
- Projects table: `tblExample0000023`
- Clients table: `tblExample0000012`

**Task fields:**

| Field ID | Name |
|---|---|
| fldExample0000024 | Task (name) |
| fldExample0000025 | Status |
| fldExample0000026 | Priority |
| fldExample0000027 | Due date |
| fldExample0000028 | Actually Completed Date |
| fldExample0000029 | Done (checkbox) |
| fldExample0000030 | Archived (checkbox) |
| fldExample0000031 | Client (lookup from Project) |
| fldExample0000032 | Project name (lookup) |
| fldExample0000033 | Project (link) |

**Status choice IDs.** The hub shares these across tables: Done `selExample0000034`, Cancelled `selExample0000035`, Backlog `selExample0000036`, Ready to Start `selExample0000037`, In Progress `selExample0000038`, Blocked `selExample0000039`.

---

## Step 1: Confirm the client

Never assume a client list. If Rachael named the client, use that name. Otherwise ask her, or list the active client names from the Clients table. The Clients table is `tblExample0000012` and its Status field is `fldExample0000040`. If a named client does not appear in the hub, say so and stop. Do not fall back to a base from memory.

## Step 2: Fetch open tasks

Run one query on the Tasks table with these filters:
- Done (`fldExample0000029`) is false.
- Archived (`fldExample0000030`) is false.
- Status is none of Done and Cancelled.
- The Client lookup (`fldExample0000031`) contains the client name.

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
