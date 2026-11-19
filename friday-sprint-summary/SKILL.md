---
name: friday-sprint-summary
version: 1.0.1
description: >
  Generate and auto-post a weekly Sprint Summary to each active client's Slack huddle channel every Friday afternoon. Covers Coding Clarified, Guardians of Love, and CCRES. Uses Rachael's canonical Sprint Summary format from her July 30-31 CC exemplar (Sprint Summary header, Completed / In Progress / Carried buckets, Velocity + Completion rate line). If a fresh working-session transcript from the last 7 days exists locally, also generates a KPI report, attaches it as a Slack Canvas, and links it from the post. Trigger phrases include: "Friday sprint summary", "post the sprint updates", "run the weekly client posts", "/friday-sprint-summary". Also invoked on a schedule (launchd job `com.rachael.friday-sprint-summary`) every Friday at 1:00 PM Pacific.
tags:
  - skill
  - scheduled
---

# Friday Sprint Summary

## Purpose in plain English

This skill helps you prepare each active client's weekly progress summary and send it to the designated Slack channel when authorized.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Weekly client-facing sprint update. Fires every Friday at 1:00 PM Pacific via launchd. Auto-posts to each client's Slack huddle channel with no pre-post review.

Rachael explicitly overrode the standing "confirm before sending to external" rule for this recurring job on 2026-08-03. If the generated post is wrong AFTER it lands, post a correction as a thread reply to the parent using `mcp__claude_ai_Slack__slack_send_message` with `thread_ts` set to the parent's `message_ts`. Do NOT delete the parent.

---

## Client roster (locked)

| Client | Client ID | Channel | Channel ID | Client folder |
|---|---|---|---|---|
| Coding Clarified | `recqM967hUDP0JohY` | `#huddle_coding-clarified` | `C0AGHQ4E7D5` | `~/Claude-Work/CLIENTS/Coding_Clarified_Janine_Mothershed/` |
| Guardians of Love | `recvBGhUXAIcYBaNa` | `#huddle_guardians_of_love` | `C0B0BPCRVL0` | `~/Claude-Work/CLIENTS/Guardians_of_Love_Jessica_Peoples/` |
| CCRES | `reccKW1RROpUVx5qt` | `#huddle_ccres` | `C09CZ718GFJ` | (no local folder yet; skip transcript + KPI step for CCRES until one exists) |

THFH is intentionally not on the list.

---

## Format (locked to the July 30-31 CC exemplar)

The post shape is not up for reinterpretation. Do not swap emojis, rename buckets, or add / remove buckets.

```
Sprint Summary: <sprint_start_YYYY-MM-DD> – <sprint_end_YYYY-MM-DD> | <Client Name>

:white_check_mark: Completed (<N>):
• <concrete outcome with numbers> · <Project name verbatim from API>
• ...

:arrows_counterclockwise: In Progress (<N>):
• <open item with concrete numbers and status detail> · <Project name>
• ...

:clipboard: Carried (<N>):
• <item owed by us or by the client — no project tag>
• ...

:bar_chart: Velocity: <completed_count> tasks | Completion rate: <pct>%
```

### Format rules

- Emojis are Slack shortcodes (`:white_check_mark:`, `:arrows_counterclockwise:`, `:clipboard:`, `:bar_chart:`), not Unicode glyphs.
- Bucket order: Completed → In Progress → Carried → Velocity. Fixed.
- Count in the bucket header, e.g. `:clipboard: Carried (3):`.
- Bullet character is `•`, followed by one space.
- Bullet tag separator on Completed and In Progress: space + `·` + space + Project name. Carried bullets have no tag.
- No `⚠️` risk marker. No `BLOCKED / RISK / OVERDUE` labels. No `**bold**` inside bullets.
- No user tags. No `@channel`. No `@here`.
- Total post under 40 lines. If a bucket exceeds 5 bullets, show top 5 and add `...and <N> more.` as the last bullet.

### Velocity math

`Completion rate = round( completed / (completed + in_progress) * 100 )`.
Carried does not enter the math. If `completed + in_progress` is zero, the whole line becomes `:bar_chart: No task activity recorded this week.`

### Sprint window

Sunday of this week through Saturday of this week (the seven days ending the day after the post). Header format: `Sprint Summary: 2026-08-03 – 2026-08-09 | Coding Clarified`.

If the exemplar's dates suggest a different window (e.g. the 2026-07-30–07-31 CC post was mid-sprint), match this rule; do not literally replicate the exemplar's 2-day range.

---

## Bullet tag map (locked with Rachael 2026-08-04)

Tags are Rachael's short-form workstream labels — NOT the tasks.xray.tech project names. The API's project names are longer and different. When drafting a bullet, pick the tag whose description best fits the item; if nothing fits, drop the tag and log it so a new tag can be added next week.

To add or rename a tag: edit this table. No code change.

### Coding Clarified

| Tag | Covers |
|---|---|
| `Build plan` | Planning, task board organization, project scaffolding, orphaned task clean-up |
| `WIOA data quality` | WIOA regions, zip codes, region-instructions coverage, region-zip audits |
| `Proposals` | Zaite proposal flow, state PDFs, proposal-created email, region-assignment email |
| `Status engine` | Day-7 / day-14 / day-21 / day-30 email cascade, three-strike inactivity rule, ISP handoff, enrollment start date coverage, Do Not Contact suppression |
| `Grade sync` | Blackboard grade pull (browser scrape and manual CSV), grade attempts migration, transcript layer |
| `Caseworker linking` | Find-or-create caseworker at proposal, retroactive daily caseworker sweep, caseworker email delivery log |

### Guardians of Love

| Tag | Covers |
|---|---|
| `Status architecture` | Controlled vocabulary, status field definitions, record status value migration |
| `Compliance tracking` | QPI 1 through 20, training requirements, deadline obligations, contractual vs internal clocks, junction tables |
| `Acuity sync` | Booking sync, cancellation path, timezone verification, sign-in flow, Acuity-to-training-tracking bridge |
| `A-7 reporting` | Monthly RHAS Completion Report, entry form, timing distribution, source-flag disagreement handling |
| `Certificate handling` | Certificate generation, staff review queue, historical SharePoint ingest |
| `Paraprofessional tools` | Paraprofessional dashboards, Jessica view, task assignment, reassignment tracking |
| `Procurement` | Procurement, purchase, delivery, set-up, inventory, equipment loans, vendor billing |
| `Administrative dashboard` | Cross-workstream dashboards, org-wide interface pages, KPI review pages |

### CCRES

CCRES is a new engagement (started 2026-08-02). Expect this table to shift as the scope firms up.

| Tag | Covers |
|---|---|
| `Hiring & onboarding` | Hiring & Onboarding System project — applicant intake, onboarding workflow, new-hire task generation |
| `Grants & funding` | Grantpoint Phase 2 and Grants and Funding System projects — grant application tracking, funding pipeline |
| `Consultant matching` | Consultant matching system — matching logic, MVP follow-on work |
| `Systems integrations` | Cross-tool plumbing between CCRES's existing SaaS stack |
| `Discovery` | Anything still in scoping / Phase 1 / requirements-gathering mode |
| `Quickbooks` | Quickbooks-side automation, invoicing, expense tracking, journal entries |

---

## Data sources per client

### Tasks (mandatory)

- Auth: `X-Api-Key` header from `~/.config/xray/tasks-api-key`.
- Endpoint: `GET https://tasks.xray.tech/api/tasks?client=<clientId>&updated_since=<sprint_start_iso>`.
- Bucket tasks by their returned status field:
  - `Done` and `updated >= sprint_start` → **Completed**
  - `In Progress` → **In Progress**
  - `Blocked` OR (`Not Started` AND owed by external / awaiting decision) → **Carried**

### Bullet tags (mandatory, for Completed and In Progress bullets)

- The tag comes from the per-client tag map above, NOT from the tasks.xray.tech project name.
- For each Completed or In Progress bullet, pick the tag whose description best fits the outcome. Use the tag verbatim from the table.
- If nothing in the tag map fits the item: drop the tag on that bullet and log the item + a proposed new tag in the run log. Rachael reviews the run log and decides whether to add the tag.
- Never invent a tag not in the map. Never use the API's project name as a tag.
- The tasks.xray.tech API is still called for TASK content and status; the response's `projectId` and `project.name` fields are used only for the run log's hygiene section, not for the bullet tag.

### Latest transcript (optional, local only)

- Glob `<client_folder>/Transcripts/*` for the most recent file by name-embedded date.
- If newer than 7 days: load the `kpi-report` skill, generate a KPI report, write it to `<client_folder>/Documents/kpi-report/<YYYY-MM-DD>-weekly-snapshot/kpi-report.md`, then create a Slack Canvas via `mcp__claude_ai_Slack__slack_create_canvas`.
- Append this line to the sprint post as the final line, BEFORE the Velocity line: `Full KPI report: <canvas_url>`.
- If older or missing: no Canvas, no link.

### Recent local artifacts (optional supplement)

- Scan `<client_folder>/Project Documentation/` and `<client_folder>/Automations/` for files created or modified since sprint_start.
- Cross-check against the Completed list; if a shipped artifact is not represented in the tasks API, add it as a Completed bullet with its project tag (best-effort match) and log the reconciliation gap.

---

## Voice rules

Bullets are complete thoughts with concrete numbers. Every Completed and In Progress bullet names the outcome, not the artifact.

- Bad: `Weekly KPI report filed (13 measurements, 7 recommendations, 14 gaps) · Reporting`
- Good: `Weekly KPI report filed from the July 29 working session; established baseline measurements for the three go-live blockers Janine named (30 approved WIOA regions missing instructions, 40 candidates without zip codes, ~50 students without an enrollment start date) · Build plan`

Banned words: ensure, utilize, leverage, streamline, robust, scalable, clean, heal, drift, smoke, amazing, incredible, fantastic, "needs fixing" (say "needs to be fixed").

Em dashes: banned everywhere in the post. Tags come from the local tag map above and none contain em dashes.

No throat clearing. No summary sentences. No "just" or "quick" as filler.

---

## Execution sequence

1. Compute sprint window: `sprint_end = today`; `sprint_start = today - 6 days`.
2. For each client in the roster (parallel-safe):
   a. Fetch tasks from the tasks.xray.tech API for the sprint window.
   b. Resolve every referenced project's name via the projects endpoint. Apply `(unassigned)` where applicable.
   c. Scan for the latest local transcript. If newer than 7 days, generate the KPI report and create the Canvas.
   d. Draft the post using the format block above. Compute Velocity.
   e. Send via `mcp__claude_ai_Slack__slack_send_message` to the channel_id from the roster.
3. Write `~/Claude-Work/PROJECTS/friday-sprint-summary/logs/log-<YYYY-MM-DD>.md` with:
   - Per-client: message permalink, Canvas URL (if any), task counts by bucket, hygiene issues found (null clientId / duplicate names / cancelled or done projects referenced).
   - Any client that failed to post, with the exception message.

---

## Dry-run mode

Trigger phrase: `run /friday-sprint-summary --dryrun` or arg `--dryrun`.

- Skip step 2e (Slack send) and Canvas creation.
- Print each drafted post to stdout, one per client, separated by `--- <Client Name> ---` headers.
- Still write the run log.

Use this before enabling the launchd plist and any time the format or data source changes.

---

## Failure modes

| Failure | What to do |
|---|---|
| tasks.xray.tech API non-200 for a client | Post `Sprint Summary: <dates> | <Client>` header and the `:bar_chart: No task activity recorded this week.` line. Log the API error. Do not retry mid-run. |
| Projects endpoint 404 for a specific projectId | Use `(project not found)` as the tag. Log the ID. |
| Canvas creation fails | Post the sprint summary without the `Full KPI report:` line. Log the Canvas error. |
| Slack post fails on one client | Continue with the other clients. Log which client failed and the error. |
| Missing local client folder (e.g. CCRES) | Skip transcript + KPI step for that client; post the sprint summary from tasks activity only. |
| All three posts fail | Write the run log with the errors. Do NOT swallow silently. |

---

## Overrides Rachael has made for this skill

- **Rule #18** (never send external without asking first): overridden 2026-08-03 for this recurring job only. `Auto-post Friday afternoon, no review.`
- **feedback_confirm_before_sending**: superseded by the same override.
- **Em dash ban**: NOT overridden. Tags come from the local tag map, none of which contain em dashes.

Overrides apply ONLY to this skill.
