---
name: write-artifact
description: >
  Write a summary, report, or document to the XRAY Artifacts table in Airtable. Use this skill any time a finished piece of content needs to be saved as an Artifact record — sprint summaries, weekly reports, project notes, or any structured output. Trigger on: "save this to Artifacts", "write this to Airtable", "log this as an artifact", "record this summary", "save it", or any workflow that produces a document and needs it persisted. Always confirm content before writing. Never overwrite existing records.
---

# Write Artifact

Save a formatted document to the Artifacts table in the correct XRAY Airtable base.

---

## Reference Data

| Client           | Base ID           |
|------------------|-------------------|
| Coding Clarified | app6Fzai5bYEsgpA2 |
| AY Media         | appkqflDisG7M8qnp |

**Artifacts table:** `tblBzmL56e6ol8TIW`

---

## Inputs Required

- Client name (determines which base to write to)
- Document name / title
- Body content (formatted text)
- Type (e.g. "Sprint Summary", "Weekly Report")
- Period (e.g. "Weekly", "Bi-Weekly")
- Start date and end date (YYYY-MM-DD)
- Optional: project record ID(s) to link

---

## Step 1 — Confirm Before Writing

Show the record that will be created. Ask for confirmation. Never write without explicit approval.

---

## Step 2 — Create the Record

Write to `tblBzmL56e6ol8TIW`.

⚠️ Always use `typecast: true` — the Artifacts table may have no existing select options.

| Field ID          | Value                                          |
|-------------------|------------------------------------------------|
| fldget1GIXGucO7vT | Name / title (singleLineText)                  |
| flddXxQrNYPDB3QKT | Body content (richText)                        |
| fldpoToICirP5FitW | Type (singleSelect — use typecast)             |
| fldKUrNgjV20pHftR | Period (singleSelect — use typecast)           |
| fld71XzUEYHY1reQ2 | Start date (YYYY-MM-DD)                        |
| fld95Ic9Qqw2yz5xI | End date (YYYY-MM-DD)                          |
| fldfyVIifaChImlG9 | Status → "Draft" (singleSelect — use typecast) |
| fldd1EKxpE9r5GH9Q | Projects (multipleRecordLinks — optional)      |

---

## Guardrails

- Additive only — never update or overwrite existing records
- Always use `typecast: true`
- Confirm with user before every write
