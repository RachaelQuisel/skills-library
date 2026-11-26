---
name: todays-focus
description: Build a prioritized, time-blocked daily task list by pulling from Notion and Google Calendar, then output a Notion page in the Today's Focus database. Use this skill whenever the user asks about today's tasks, what to work on, planning their day, daily priorities, quick wins, or deep focus time. Trigger phrases include "what tasks for today," "plan my day," "today's tasks," "today quick wins," "what should I work on today," "deep focus," "today's focus," or any request to create a daily task plan. Also trigger when the user mentions prioritizing tasks, time-blocking, or asks "what's on my plate."
---

# Today's Focus

Generate a prioritized, calendar-aware daily task list from Notion data and Google Calendar, then publish it as a page in the user's "Today's Focus" Notion database.

## Why this skill exists

Planning your day from scratch every morning is a tax on your best thinking hours. This skill gathers context from where your work actually lives, scores tasks by category, and maps them onto your real available time — so you start the day with a plan instead of spending 30 minutes making one.

## Three modes

The user's phrasing determines the mode. Default to **full plan** if ambiguous.

| Mode | Trigger phrases | Behavior |
|---|---|---|
| **Full plan** | "plan my day," "what tasks for today," "today's tasks," "today's focus" | All categories, full scoring, time-blocked output |
| **Quick wins** | "today quick wins," "what can I knock out," "short tasks" | Filter to tasks under 30 min only, skip deep work |
| **Deep focus** | "deep focus," "what needs deep work," "focus time" | Filter to tasks needing 60+ min uninterrupted blocks only |

## Workflow

Execute these steps in order. Be disciplined about token budget — pull only what's needed.

### Step 1: Gather data (3 tool calls)

Run these sequentially. Each call has a strict scope to keep context lean.

**1a. Google Calendar — today's events**

Call `gcal_list_events` with:
- `timeMin`: today at 00:00:00 (user's local timezone, America/Los_Angeles)
- `timeMax`: today at 23:59:59
- `condenseEventDetails`: true
- `timeZone`: "America/Los_Angeles"

This gives you the day's meeting load.

**1b. Google Calendar — free time slots**

Call `gcal_find_my_free_time` with:
- `calendarIds`: ["primary"]
- `timeMin`: current time (don't include past hours)
- `timeMax`: today at 23:59:59
- `timeZone`: "America/Los_Angeles"
- `minDuration`: 15

This gives you the actual available work blocks.

**1c. Notion — recent notes, tasks, and context**

Call `notion-search` with:
- `query`: "tasks action items work" (adjust if user specifies a project)
- Look for pages updated in the last 3 days

Then, if rollover is relevant, search for yesterday's Today's Focus page:
- `query`: "Today's Focus" + yesterday's date
- Check for any uncompleted tasks (items without checkmarks)

Limit: pull at most 10 Notion results. Skim titles and highlights — only fetch full page content for the 2-3 most relevant pages.

### Step 2: Analyze and extract tasks

From the gathered data, extract actionable tasks. A task is actionable if it has a clear next step (not "think about X" but "draft the X proposal").

For each potential task, capture:
- **What**: one-sentence description of the deliverable
- **Project**: which client/project it belongs to (use memory for context — EMG, Example Nonprofit, XRAY internal, personal, etc.)
- **Source**: where you found it (Notion page title, calendar event, etc.)
- **Effort estimate**: in minutes (15, 30, 60, 90, 120, 180)
- **Deadline signal**: is there an explicit deadline? how soon?

If the user pasted notes or context in their message, treat those as the highest-signal source.

### Step 3: Categorize each task

Assign exactly one primary category per task:

| Category | Criteria | Icon |
|---|---|---|
| **Deadline-driven** | Has a hard due date within 48 hours, or someone is waiting on it | 🔴 |
| **Quick win** | Can be completed in under 30 minutes, low complexity | ⚡ |
| **Deep work** | Requires 60+ min of focused, uninterrupted time | 🧠 |
| **Long-term** | Important but no immediate deadline, building toward a bigger goal | 🌱 |

A task can only be one category. If it's both deadline-driven and deep work, deadline-driven wins (urgency trumps mode).

### Step 4: Score and rank

Score each task on a 0-100 scale using these weighted factors:

| Factor | Weight | How to assess |
|---|---|---|
| Urgency | 35% | Deadline proximity: today = 100, tomorrow = 70, this week = 40, no deadline = 10 |
| Impact | 25% | Client-facing or revenue-connected = 80-100, internal = 40-60, personal = 20-40 |
| Effort fit | 25% | How well does the effort estimate match available calendar slots? Perfect fit = 100, poor fit = 30 |
| Momentum | 15% | Is this a continuation of yesterday's work or a fresh start? Continuation = 80, fresh = 50 |

**Mode filtering** happens after scoring:
- **Quick wins mode**: drop any task with effort > 30 min
- **Deep focus mode**: drop any task with effort < 60 min
- **Full plan mode**: keep all tasks

Sort by total score descending.

### Step 5: Select top N and time-block

Default to **3 tasks** unless the user specifies a number (valid range: 2-5).

For each selected task, assign it to a specific free time block from Step 1b:
- Deep work tasks get the longest uninterrupted blocks
- Quick wins get slotted into gaps between meetings (30 min or less)
- If a task doesn't fit any remaining free block, flag it with "⚠️ may need to move a meeting or defer"

**Calendar math:**
- Sum the total available free time from Step 1b
- Sum the effort estimates of selected tasks
- If tasks exceed available time, reduce task count and note it: "You have X hours free today. I've selected Y tasks totaling Z hours."
- On heavy meeting days (< 2 hours free), proactively suggest fewer tasks and acknowledge the constraint

### Step 6: Create the Notion page

Create a page in the **Today's Focus** database using `notion-create-pages`.

**Page properties:**
- `Daily Plan`: "[Day of week], [Month] [Day], [Year]" (e.g., "Friday, March 6, 2026")
- `Date`: today's date
- `Mode`: whichever mode was used
- `Task Count`: number of tasks
- `Total Hours`: sum of effort estimates in hours
- `Status`: "Planned"

**Page content structure** (use Notion-flavored markdown):

```
## Overview
[1-2 sentences: what mode, how many tasks, how much free time, any rollover context]

## Tasks

### 1. 🔴 [Task name] — [effort estimate]
**Time block:** [start] – [end]
**Project:** [project name]
**Source:** [where this came from]
[1 sentence: what "done" looks like for this task]

### 2. ⚡ [Task name] — [effort estimate]
**Time block:** [start] – [end]
**Project:** [project name]
**Source:** [where this came from]
[1 sentence: what "done" looks like for this task]

### 3. 🧠 [Task name] — [effort estimate]
**Time block:** [start] – [end]
**Project:** [project name]
**Source:** [where this came from]
[1 sentence: what "done" looks like for this task]

---

## Parking lot
[Tasks that scored well but didn't make the cut. 2-4 bullets, one line each. These are candidates for tomorrow.]

## Today's calendar
[Condensed view: meeting name — time — duration. Just so everything is in one place.]
```

### Step 7: Respond to the user

After creating the Notion page, respond in chat with:
1. A brief summary: "Your Today's Focus page is ready — [N] tasks, [X] hours of work mapped to your free time."
2. Link to the Notion page
3. If any tasks couldn't be time-blocked, mention it
4. If rollover tasks were found, mention what carried over

Keep the chat response concise. The Notion page is the artifact; don't duplicate it in chat.

## Important guidelines

**Token budget discipline:**
- Google Calendar calls are cheap — the data is structured and small
- Notion search can be expensive if you fetch full page contents. Skim first, fetch only what's needed.
- Target: complete the entire workflow in under 12 tool calls

**When data is thin:**
- If Notion search returns nothing useful, don't fabricate tasks
- Acknowledge it: "I didn't find much in Notion today. Here's what I built from your calendar and any context you shared."
- The user can paste Apple Notes or other context directly into chat — treat that as primary input

**Active project context from memory:**
- EMG (Example Media Group): Lee Tran, ad operations migration, Fillout → Airtable → QuickBooks pipeline
- Example Nonprofit: Dana Whitfield, student lifecycle, Phase 5, Zapier/Airtable debugging
- XRAY internal: templates, office hours, skills, documentation
- Personal: La Maison property, fitness goals, community projects

Use these to contextualize and label tasks by project. Memory provides the project registry that makes task categorization meaningful.

**Rollover behavior (optional):**
- Search for yesterday's Today's Focus page
- If found, look for tasks that weren't marked complete
- Include them in today's scoring with a +20 momentum bonus (they're continuations)
- If yesterday's page doesn't exist, skip silently — no error, no mention

## Expansion roadmap (not for v1)

These are planned additions for future versions. Do not implement them now.

- **Gmail integration**: scan recent actionable emails (unread, starred, from key contacts) for tasks
- **Slack integration**: scan recent DMs and mentions for action items
- **Apple Notes**: pending a cloud-accessible MCP connector
- **Task completion tracking**: update the Notion page status when user says "done with task 2"
- **Weekly review mode**: aggregate the week's Today's Focus pages into a summary
