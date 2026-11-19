# Example: a finished `vision-and-scope.md`

Use this as the bar for tone, detail, and format. The client is made up (Riverside Literacy Project, repo `XRAY-INC/RIVERSIDE-LITERACY`, build `2026-09-build`).

What to copy:
- The problem names whose pain it is and what happens today, with a number where there is one.
- The vision describes what a person sees and does after the build, not "processes are automated."
- Every in-scope and out-of-scope item starts with a verb.
- Each non-goal says why it is out. Non-goals are the section that holds the line when the client asks "can we also...".
- Boundary calls say where the item landed and why.

---

```markdown
# Vision and Scope: 2026-09-build

**Client:** Riverside Literacy Project
**Build:** 2026-09-build
**Last updated:** 2026-09-24

## Problem

The program coordinator spends the last 3 days of every month typing tutoring hours from paper sign-in sheets at 6 school sites into a spreadsheet for the district report. Missing hours aren't found until the report is due, when it's too late to ask tutors about them.

## Vision

Tutors log each session on their phone the day it happens. Every Thursday the coordinator opens one list that shows which tutors have no hours that week, and those tutors have already received a reminder email. On the first of the month, the district report's hours table is already filled in from Airtable, and the coordinator reviews it instead of typing it.

## In scope

- Build a session form tutors fill out on their phones, with students filtered to the tutor's school
- Link each tutor record to their school site from the sign-up form answer
- Send a weekly reminder email to tutors with fewer than 2 logged hours by Thursday 9 a.m.
- Build a Sites interface showing hours per site per month
- Fill the hours table of the monthly district report from the Sessions table

## Out of scope (non-goals)

- Track student reading levels: the district's assessment system already holds them, and copying them would create a second version to keep in sync.
- Schedule tutoring sessions: each school sets its own schedule, and the coordinator asked to leave that with the schools.
- Text-message reminders: the program has no budget for a texting service this year.
- Import sign-in sheets from before September 2026: the district only asks for current-year hours.

## Boundary calls

- **Principal access to the Sites interface:** in (principals read their own site's summary only; no editing)
- **Tutor background-check dates:** out (held by the district HR office; the coordinator checks them there)
```
