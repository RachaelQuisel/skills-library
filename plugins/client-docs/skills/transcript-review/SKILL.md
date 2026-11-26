---
name: transcript-review
version: 1.4.8
description: Review a meeting transcript and extract decisions and action items into Rachael's working systems — a dated debrief file plus Airtable tasks in the right client base. Use whenever Rachael says "review this transcript", "transcript landed", "extract decisions and action items", "debrief this meeting", "what did we decide", pastes transcript text, or references a Granola or Wispr Flow meeting that needs processing — even if she doesn't say the word "transcript". Works for any client; it discovers the client's base rather than assuming one.
---

# Transcript Review

## Purpose in plain English

This skill helps you review a meeting transcript to identify the project information and follow-up it supports.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Turn a meeting transcript into two outputs: a debrief file and tracked tasks. This skill is client-agnostic. Never assume which client a meeting belongs to. Never use a base ID from memory or from an old example.

## Step 1: Get the transcript

Use the first of these that applies:
1. Text Rachael pasted, or a file she pointed at.
2. Granola: `get_meetings` for the named meeting, then `get_meeting_transcript` when available.
3. Wispr Flow: `search_meetings` or `get_meeting`.

If several meetings match, list the candidates and ask one question. Then proceed.

## Step 2: Extract

Read the whole transcript before extracting. Pull out three categories:

- **Decisions.** Something was settled. Capture what was decided, who said so, the rejected alternative when one was voiced, and the reason. A deferral counts as a decision.
- **Action items.** Someone committed to doing something. Capture the owner, the deliverable, and any stated deadline. If no owner was stated, mark it `owner: unassigned`. Never guess an owner.
- **Open questions.** Raised but not settled. These seed the next agenda.

Rules:
- Quote or closely paraphrase. Do not embellish. If a point is unclear in the transcript, mark it `[unclear in transcript]`.
- Attribute by speaker name as the transcript has it.
- Resolve relative dates such as "by Friday" against the meeting date, not today.

## Step 3: Identify the client and confirm

Infer the client from the transcript: the attendees, the company names, and the systems discussed. Say the inference out loud for Rachael to confirm. Never act on it silently. If Rachael has a current-clients list in her preferences or project files, check the inference against it. Flag a client that is not on that list. Do not process it.

Then show the extracted lists in compact form. Ask at most two questions, and only about ambiguous owners, ambiguous due dates, or an uncertain client or project.

## Step 4: Write the debrief file

Save to the client repo's `debriefs/` folder as `YYYY-MM-DD_subject.md`. Use the meeting date and a kebab-case subject. Add YAML frontmatter per the repo's convention. Client repos use the `client` and `project` keys. Internal initiative repos use the `program`, `pillar`, and `cohort` keys. Then write the three sections: Decisions, Action items, Open questions.

## Step 5: Create the tasks, with approval

Offer to create one Airtable task per action item. Create tasks only after Rachael approves the list.

Find the right base and tables by discovery, never from memory:
1. `search_bases` with the client's name. If several bases match, prefer the most recently viewed one and confirm with Rachael.
2. `list_tables_for_base` to find the Tasks and Projects tables by name. XRAY client bases follow a shared template. Expect tables named "Tasks" and "Projects" with Task name, Status, Priority, Due date, and a Project link.
3. Resolve field IDs from the schema, not from memory. Give new tasks the Status "Ready to Start".
4. Link each task to its project. Filter the Projects table by the client and match the project name.
5. Before creating, search the existing open tasks for near-duplicate names. Flag duplicates instead of creating them twice.

## Step 6: Route decisions onward

Some decisions are design, scope, or tooling calls worth preserving in the client record. Say so in one line. Offer the `client-doc-decisions` skill to log each one as an ADR in the client's `decisions.md`. ADR means architecture decision record. Do not log it without asking.

## Voice

Write the debrief in Rachael's voice: plain and direct, with no emojis. Say "needs to be fixed", never "needs fixing". Say "main", never "master". Say "complete" for data status, never "clean".
