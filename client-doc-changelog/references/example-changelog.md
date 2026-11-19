# Example: a finished `changelog.md`

Use this as the bar for tone, detail, and format. The client is made up (Riverside Literacy Project, repo `XRAY-INC/RIVERSIDE-LITERACY`, build `2026-09-build`). Each bullet names the thing that shipped and what is different for the client now.

What to copy:
- Newest date at the top.
- One bullet per shipped item; several items on one day share one date header.
- Past tense, verb first, then what changed for the client in their words.
- Counts carry units ("412 tutor records", not "412").
- Nothing that is still in progress. That goes in `running-updates-and-questions.md`.

---

```markdown
# Changelog - 2026-09-build

**Client:** Riverside Literacy Project
**Build:** 2026-09-build

Newest entries at the top.

---

## 2026-09-24

- **Shipped:** Turned on the weekly tutor-hours reminder email - every tutor with fewer than 2 logged hours by Thursday at 9 a.m. now gets a reminder, so the coordinator no longer sends these by hand.
- **Shipped:** Added a "Reminder sent on" date field to the Tutors table - the coordinator can see who was reminded this week without opening the email account.

---

## 2026-09-17

- **Shipped:** Linked 412 tutor records to their school site from the sign-up form's site answer - every tutor now shows under the right school in the Sites interface, and 9 tutors whose answer matched no site are listed for the coordinator to assign.

---

## 2026-09-10

- **Shipped:** Replaced the paper sign-in sheet with a tutoring session form - sessions land in Airtable the same day instead of being typed in at the end of the month.
```

---

What a weak entry looks like, and why it fails:

```markdown
- **Shipped:** Reminder automation - improved tutor engagement.
```

It has no verb, it doesn't say what the reminder does or who gets it, and "improved engagement" is a claim nobody verified.
