# Example: a finished `decisions.md`

Use this as the bar for tone, detail, and format. The client is made up (Riverside Literacy Project, repo `XRAY-INC/RIVERSIDE-LITERACY`, build `2026-09-build`). Each entry states the constraint that forced the choice, so a reader months later can judge whether the decision still holds.

What to copy:
- Newest entry at the bottom (this file is an audit trail, read top to bottom in order).
- Title is verb-first and says what was decided, not the topic.
- "Because" names the specific constraint, incident, or client ask.
- "Alternatives passed on" names the runner-up and the one reason it lost.
- A reversed decision gets a new entry that points to the old one by date. The old entry stays as written.

---

```markdown
# Decisions - 2026-09-build

**Client:** Riverside Literacy Project
**Build:** 2026-09-build

Append-only ADR log. Newest entries at the bottom.

---

## 2026-09-08 - Collect tutoring sessions with a Fillout form, not an Airtable form

**Decided:** Tutors log each session through a Fillout form that writes to the Sessions table.
**Because:** Tutors pick their student from a list filtered to their own school site, and the Airtable form can't filter a linked-record picker by another answer on the same form.
**Alternatives passed on:** Airtable's built-in form, because every tutor would see all 380 students across all sites.

---

## 2026-09-15 - Leave tutors with no matching site unassigned

**Decided:** When a tutor's sign-up answer matches no school site, the record stays unlinked and goes on a list for the coordinator.
**Because:** The coordinator confirmed on 9/15 that a wrong site is worse than no site; a wrong site sends the tutor to the wrong school's schedule.
**Alternatives passed on:** Closest-spelling match, because 3 of the 9 unmatched answers named schools that aren't partner sites.

---

## 2026-09-22 - Send tutor reminders on Thursday instead of Monday

**Decided:** The weekly hours reminder goes out Thursday at 9 a.m.
**Because:** Most sessions happen Tuesday and Wednesday, so a Monday reminder reached tutors before they had anything to log.
**Alternatives passed on:** Friday, because the coordinator closes the weekly report Friday at noon and needs the hours in before then.
```

---

What a weak entry looks like, and why it fails:

```markdown
## 2026-09-22 - Reminder timing

**Decided:** Changed the day.
**Because:** Better for tutors.
```

The title is a topic, not a decision. It doesn't say which day was picked, and "better for tutors" gives a future reader nothing to check against.
