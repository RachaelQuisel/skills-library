---
name: meeting-prep
version: 1.0.2
description: >
  Build a meeting-prep brief for every client meeting on Rachael's calendar today (or a
  specified date). For each meeting, the skill identifies which client it belongs to,
  reads that client's project build status, running updates log, recent transcripts, and
  recent task activity in the XRAY planning base, then writes a brief covering where you
  left off, talking points, task updates, open questions, and watch-outs. Falls back to
  external web research for prospect/discovery meetings where no client folder matches.
  Use whenever Rachael says "prep me for today", "meeting prep", "prep me for [client]",
  "what should I know before [meeting]", "I have a call with [name]", or any morning
  ritual where she's about to step into client calls. Trigger even when she doesn't say
  "prep" — phrases like "what's on the docket today", "remind me where we left off with
  [client]", or "what do I owe [client]" also belong here.
tags:
  - skill
---

# Meeting Prep

## Purpose in plain English

This skill helps you prepare a brief for a client meeting using the relevant project and conversation context.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Produce a scannable pre-meeting brief — readable in under 5 minutes per meeting — for
every client meeting on Rachael's calendar.

## Two modes

The skill chooses per meeting based on whether the attendee maps to an existing client:

| Mode | When | Source of context |
|---|---|---|
| **Client prep** (primary) | Attendee or event title matches a folder under `~/Claude-Work/CLIENTS/` | Client folder docs + XRAY planning base + recent transcripts + recent debriefs |
| **Prospect prep** (fallback) | No client folder matches | WebSearch + WebFetch on attendee/company |

Both modes produce the same brief shape so the morning batch is uniform.

---

## Phase 1 — Get today's calendar events

Default to today in Rachael's timezone (America/Chicago / America/Los_Angeles — confirm
from the calendar response). If she names a date or "tomorrow" / "this week", use that
instead.

```
mcp__claude_ai_Google_Calendar__list_events
```

Filter to:
- Events with at least one external attendee (skip internal-only blocks like focus
  time, "deep work," "lunch")
- Events that aren't all-day blocks unless they're explicitly client-tagged

If no events found for the requested day, say so and stop.

---

## Phase 2 — Identify the client for each event

For each event, try to map it to a client folder under `~/Claude-Work/CLIENTS/`:

1. **List client folders** (one-time per run): `ls -d ~/Claude-Work/CLIENTS/*/`
2. **For each event**, check (in order):
   - Attendee email domains (e.g., `@examplenonprofit.com` → Example Nonprofit)
   - Attendee names against folder names (e.g., "Dana Whitfield" → `Coding_Clarified_Janine_Whitfield`)
   - Event title keywords (e.g., "AYMG sync" → `AY Media_Jay_Danzy`)
3. **Handle alias folders** — some clients have multiple folders (e.g., `EA/` and
   `Guardians_of_Love_Jessica_Peoples/` are the same client). Prefer the folder with the
   most recent activity (newest file modification times under `Project Documentation/`
   or `Transcripts/`).
4. **If no match**, mark the event as `prospect` and route to Phase 4.

If matching is ambiguous (two folders look equally plausible), ask Rachael which one.
Don't guess.

---

## Phase 3 — Gather context for client meetings

For each matched client meeting, read these sources. Don't read everything — read the
most recent / most relevant entries:

### 3a. Client folder docs — discover, don't hardcode

Client folders vary in structure. Don't assume canonical paths exist; discover what's
actually present, prioritized by recency and signal-strength.

Look for these patterns (in order). Read the ones that exist:

| Pattern | Why it matters |
|---|---|
| `session_handoff*.md` (root) | Most recent session-end summary — decisions made, outstanding tasks, interrupt points. Usually the single highest-signal file when present. |
| `*project-status*-YYYY-MM-DD.md`, `*status*-YYYY-MM-DD.md` (root + `Project Documentation/`) | Dated sprint snapshots — workstream state, decisions locked, sprint window |
| `Project Documentation/running-updates-and-questions.md` | Rolling decisions log — when it exists |
| `Project Documentation/schema-dependencies.md` | Recent edits (compare mtime vs last meeting date) |
| `tasks/active-followups.md`, `tasks/todo.md` | Open commitments and in-flight work |
| Any `**/lessons.md` under the client folder | Recurring patterns; clients sometimes have one per subproject, not just one at root |

Discovery command shape (portable across macOS BSD find and GNU find — uses `stat` for
mtime so this works on a stock Mac without homebrew findutils):

```
find ~/Claude-Work/CLIENTS/<client> -maxdepth 4 \
  \( -name 'session_handoff*.md' -o -name '*-status-*.md' -o -name '*project-status*.md' \
     -o -name 'running-updates-and-questions.md' -o -name 'schema-dependencies.md' \
     -o -name 'active-followups.md' -o -name 'todo.md' -o -name 'lessons.md' \) \
  -exec stat -f "%m %N" {} \; 2>/dev/null | sort -rn | head -10
```

If you have GNU find (homebrew `findutils`), `-printf "%T@ %p\n"` is faster but
optional — the `-exec stat` form is the safe default.

Read the top 3-5 by mtime. If a client folder has nothing matching, note "no project
docs found" in the brief — don't fail the run.

### 3b. Recent transcripts — handle any folder naming and any format

Transcripts may live in `Transcripts/`, `Transcripts_<ClientCode>/`, `transcripts/`, or
similar. Discover the folder by glob, not by exact name. Files may be `.md`, `.txt`, or
`.docx`.

```
find ~/Claude-Work/CLIENTS/<client> -maxdepth 3 -type d -iname 'transcript*'
```

Within the discovered folder(s), find the newest 2 files of any supported format:
```
find <transcripts_dir> -type f \( -name '*.md' -o -name '*.txt' -o -name '*.docx' \) \
  -exec stat -f "%m %N" {} \; 2>/dev/null | sort -rn | head -2
```

**For .md and .txt**, Read directly. If the file is over ~5000 lines, read the last 500.

**For .docx**, extract text first:
- Try `pandoc <file> -o /tmp/<basename>.txt` if pandoc is installed
- Fallback to `python3 -c "from docx import Document; print('\n'.join(p.text for p in Document('<file>').paragraphs))"` if python-docx is installed
- If neither tool is available, note "transcript is .docx and couldn't be extracted — skill needs pandoc or python-docx" and skip content extraction for that file

Extract from the transcripts:
- Specific commitments Rachael made ("I'll send you X by Friday")
- Open questions the client raised
- Topics the client was emotional about (frustration / excitement / concern)
- Recurring themes across the call

### 3c. XRAY planning base — recent task activity

Recent tasks and outcomes for this client live in the XRAY upstream base
(`appExample0000004`). Use the PAT at `~/.config/xray/airtable-tasks-pat`.

For each client:
- Find their Project record(s) in the Projects table (a client can have multiple — at
  least a billing project + outcome-level projects)
- Pull Outcomes linked to those Projects, filter to ones updated in the last 14 days
- Pull Tasks linked to those Outcomes, filter to ones modified in the last 14 days
- Surface: tasks completed, tasks newly blocked, tasks where status changed

This is the "task updates" section of the brief.

### 3d. Recent debrief

XRAY debriefs live in `appExample0000004` table `tblExample0000011`, filtered by
`XRay's Client` linked record. Use the Debrief PAT at the path noted in memory
(`reference_debrief_airtable.md`).

Pull the **most recent debrief** for this client (1 record). Use it as a watch-out
source — anything flagged as a concern or sensitive topic last time should be on
Rachael's radar.

---

## Phase 4 — Prospect mode (fallback for unmatched meetings)

When no client folder matches, fall back to external research. This is the prior
behavior of the skill, kept for new-business discovery calls.

Use WebSearch + WebFetch to find:
- Recent (last 90 days) public activity for attendees — posts, podcasts, talks, hires, raises
- Company news, product launches, funding, leadership changes
- Apparent strategic priorities (from job postings, marketing copy, exec interviews)
- Tooling stack signals (case studies, integration partners, careers page tech mentions) — relevant for automation/schema scoping

For deep multi-source research, dispatch parallel subagents (Agent tool, `general-purpose`
or `Explore`) rather than serial fetches.

Tune toward Rachael's discovery work:
- Process surface area — what manual workflows likely exist given team size, stack, stage
- Data they probably already have — CRMs, billing systems, spreadsheets hinting at schema needs
- Integration gaps — where their stated tools don't naturally talk
- Questions that surface budget + decision-maker without sounding salesy

---

## Phase 5 — Generate the brief

### Where to save

| Mode | Output path |
|---|---|
| Client | `~/Claude-Work/CLIENTS/<client>/Meeting-Prep/<YYYY-MM-DD>-<event-slug>.md` |
| Prospect | `~/Claude-Work/MEETING-PREP-INBOX/<YYYY-MM-DD>-<event-slug>.md` |

Create the directory if it doesn't exist. The event-slug is the meeting title
lowercased and hyphenated.

### Brief format — client mode

Include the `**What's at stake:**` line ONLY when there's a concrete answer from the
calendar description, the project status snapshot, or a known milestone (e.g., "last
1:1 before the June 3 Core Team Review"). If you don't have a real answer, omit the
line — don't invent one or fill it with generic framing.

```
# Meeting prep: [Client] — [event title]
**When:** [date, time, duration]
**Attendees:** [names + titles]
**What's at stake:** [milestone, deadline, or scope-locking moment — only if concrete]

## Where we left off
[2-4 sentences pulled from the most recent transcript + running-updates log: what
was discussed last time, what Rachael committed to, what the client raised]

## Task updates since last meeting
- Completed: [task name] — [one-line context]
- Blocked: [task name] — [why blocked, who can unblock]
- Status changed: [task name] — [old status] → [new status]
(omit any line that has no entries)

## Talking points (3)
1. **[Point]** — [why this lands given their context / specific to project state]
2. ...
3. ...

## Open questions to surface
1. [Question from running-updates-and-questions that's still open]
2. [Question Rachael needs answered to unblock work]
3. ...

## Watch-outs
- [Sensitive topics from last debrief]
- [Things to sidestep — recent layoffs, internal politics, blocked decisions]
- [Anything the client was emotional about last call]
```

### Brief format — prospect mode

```
# Meeting prep: [Name] @ [Company] — [date/time]
**Goal:** [restate Rachael's goal in one line]

## Attendees
- **[Name], [Title]** — [1-2 sentence background]. Recent: [signal from last 90 days].
  Conversation starter: [specific, not generic]

## Company snapshot
[2-3 sentences: what they do, recent news, apparent priorities]

## Talking points (3)
1. **[Point]** — [why this lands]
2. ...
3. ...

## Questions to ask (3)
1. [Question that demonstrates prep + advances the goal]
2. ...
3. ...

## Watch-outs
- [Sensitive topics, recent layoffs, competitor relationships, anything to sidestep]
```

### After saving each brief

Print the path to the brief in the chat so Rachael can open it. After all briefs are
written, print a one-line summary like:

```
Prepped 3 meetings for 2026-05-31:
  - 9:00 AM Janine (CC) → ~/Claude-Work/CLIENTS/Coding_Clarified.../Meeting-Prep/2026-05-31-weekly-sync.md
  - 11:00 AM Jay (AYMG) → ~/Claude-Work/CLIENTS/AY Media_Jay_Danzy/Meeting-Prep/2026-05-31-pricing-discussion.md
  - 2:00 PM Sarah (prospect) → ~/Claude-Work/MEETING-PREP-INBOX/2026-05-31-discovery-call.md
```

---

## Constraints

- **Recent + specific beats comprehensive + generic.** If the client folder is sparse,
  say so rather than padding.
- **Cite sources inline** (file path, transcript filename, debrief record) for any
  claim that isn't common knowledge — Rachael may want to re-read the source.
- **Keep each brief under ~500 words.** If she wants deeper, she'll ask.
- **Do not invent activity, quotes, or roles.** If a fact can't be verified, leave it
  out or flag as unverified.
- **Read `~/.claude/skills/humanizing/SKILL.md` before composing the brief** and apply
  its rules to talking-point and watch-out phrasing. These briefs read like Rachael's
  notes to herself, not Claude exposition. Cross-skill rules don't auto-load — the
  brief writer has to intentionally pull humanizing's content in.

---

## What to skip

- Don't summarize the entire transcript — only what's relevant to the upcoming meeting
- Don't pad watch-outs ("be respectful," "listen well") — only specific, situational items
- Don't include attendee bios for people Rachael already knows; recent activity only
- Don't repeat what's in the calendar invite (Rachael already has the invite)

---

## References

- Memory `reference_xray_planning_base_architecture.md` — XRAY upstream base ID, sync model
- Memory `reference_xray_tasks_pat_path.md` — PAT path for the planning base
- Memory `reference_debrief_airtable.md` — Debrief base + table + PAT
- Memory `feedback_client_transcripts_soap_folders.md` — Transcripts/ folder convention
- Memory `feedback_xray_client_multi_project_structure.md` — Multiple Project records per client
