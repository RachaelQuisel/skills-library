# Example: a finished `build-plan.md`

Use this as the bar for tone, detail, and format. The client is made up (Riverside Literacy Project, repo `XRAY-INC/RIVERSIDE-LITERACY`, build `2026-09-build`), drafted from meetings because the project had no outcomes or tasks in the tasks system yet.

What to copy:
- The "How this plan was made" paragraph names the sources and says the tasks are candidates until Rachael approves them.
- One section per outcome, named in words the client would use.
- Every task has an Owner, a Status, and a Source: the date of the session it came from.
- Unknowns are TODO lines with the specific question, never guesses.
- A "Not in this plan" section holds the line, the same way non-goals do in vision-and-scope.

---

```markdown
# Build Plan: 2026-09-build

**Client:** Riverside Literacy Project
**Build:** 2026-09-build
**Last updated:** 2026-09-24

How this plan was made: the Riverside project in the tasks system has no outcomes or tasks recorded yet. This plan is drafted from the three meetings between XRAY and Riverside (2026-09-02 discovery, 2026-09-09 working session, 2026-09-16 kickoff), with each item verified against the session recordings. Once Rachael approves it, these become the project's outcomes and tasks in the system.

Terms used below: the MVP is the minimum viable product, the first working build.

---

## Outcome 1: Tutors log sessions from their phones

Agreed 9/16: the first build is the session form, because the paper sign-in sheets are where the month-end crunch starts.

| Task | Owner | Status | Source |
|---|---|---|---|
| Build the session form with students filtered to the tutor's school | Rachael | Open | 9/16 |
| Confirm the list of 6 school sites and their student rosters | Coordinator | Open | 9/09 |
| Test the form with 3 tutors at one site before opening it to all 6 | Coordinator with Rachael | Open | 9/16 |

## Outcome 2: The coordinator sees missing hours before the report closes

| Task | Owner | Status | Source |
|---|---|---|---|
| Build the weekly view of tutors with no logged hours | Rachael | Open | 9/09 |
| Send the Thursday 9 a.m. reminder email to tutors under 2 hours | Rachael | Open | 9/16 |

> TODO: Who receives a copy of the reminder email besides the tutor? The 9/16 session did not say.

---

## Not in this plan

- Importing sign-in sheets from before September 2026: the district only asks for current-year hours (9/02).
- Text-message reminders: no budget for a texting service this year (9/09).
```
