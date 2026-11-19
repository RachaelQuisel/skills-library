# Example: a finished `interface-prompts.md`

Use this as the bar for tone, detail, and format. The client is made up (Riverside Literacy Project, repo `XRAY-INC/RIVERSIDE-LITERACY`, build `2026-09-build`). The base ID and table IDs below are placeholders, not a real base.

What to copy:
- Intent, Aesthetic, and Behavior rules are plain English a client can read.
- The Prompt block is the exact text pasted into Canvas, so the app can be regenerated later.
- Tables in an existing base are named by name and ID inside the prompt.
- Iteration notes are dated and include any Canvas error text that was pasted back in.

---

````markdown
# Interface Prompts: 2026-09-build

**Client:** Riverside Literacy Project
**Build:** 2026-09-build

Canvas prompts used to build custom Airtable apps for this build. One section per app, newest at the bottom. See `client-doc-interface-prompts` skill for how these get drafted.

---

## 2026-09-19: Weekly Tutor Hours board

**Base:** Existing: Riverside Tutoring (appEXAMPLE00000001)
**Tabs:** This Week, Sites
**Status:** Live

### Intent
Gives the program coordinator one screen for the Thursday check: which tutors have logged hours this week, which haven't, and whether a reminder already went out. The Sites tab shows monthly hours per school for principals.

### Data model
Reads the Tutors, Sessions, and Sites tables. No new tables. The prompt needed one new field on Tutors, "Reminder sent on" (date), which the reminder automation fills in.

### Aesthetic
Light, quiet, and easy to read on a school laptop: one sans-serif font, white cards with thin gray borders, green and amber status pills, no animation. Dark mode follows the computer's setting.

### Behavior rules
- Everything is read-only except the "Assign site" button on unassigned tutors.
- The This Week tab refreshes when opened and shows a loading state while it reads.
- Principals see only their own site on the Sites tab.

### Prompt (as pasted into Canvas)
```
Build an app called "Weekly Tutor Hours" with two tabs: This Week and Sites. Use the existing base appEXAMPLE00000001 with tables Tutors (tblEXAMPLETUTORS1), Sessions (tblEXAMPLESESSN01), and Sites (tblEXAMPLESITES01).

This Week shows one card per active tutor with name, school site, hours logged since Monday, and the "Reminder sent on" date; group cards into "Has hours" and "No hours yet"; sort "No hours yet" by site; add a filter by site; show tutors with no site linked in a separate "Needs a site" group with an "Assign site" button that opens a site picker.

Sites shows one row per school site with total tutoring hours and number of active tutors for the selected month, with a month picker defaulting to the current month.

Use a light, quiet style: Source Sans 3 only, white cards with 1px gray borders, 6px corner radius, green pill for "Has hours" and amber pill for "No hours yet", no animation. Support dark mode by following the operating system setting.

Keep the app read-only except the "Assign site" action. Show a loading state while records load and an error message with a retry button if the read fails. Refresh data each time a tab is opened.
```

### Iteration notes
- 2026-09-18: First run grouped by session instead of tutor. Changed the This Week line to "one card per active tutor."
- 2026-09-19: Canvas error "Field 'Reminder sent on' not found in tblEXAMPLETUTORS1" pasted back in after adding the field; the second run built the board.

### Known limits and scope calls
Canvas couldn't limit principals to their own site inside the app, so principals open the Sites tab through a separate interface page filtered by the logged-in user's site.

---
````
