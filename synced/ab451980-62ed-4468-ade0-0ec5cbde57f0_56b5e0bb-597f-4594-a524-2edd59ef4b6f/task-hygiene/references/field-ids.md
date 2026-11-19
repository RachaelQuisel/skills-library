# Field ID Reference — Projects & Tasks at XRAY

Verified against the live schema 2026-08-22. If a write fails or a name looks off, re-fetch the schema (`list_tables_for_base` / `get_table_schema`) and trust the base over this file; note any drift in the post-run analysis.

## Base

| Thing | ID |
|---|---|
| Base: Projects & Tasks at XRAY | `appQAdxI2hDNJj1g5` |
| Tasks table | `tblvlJq7I2GvIQEyP` |
| Projects table | `tblOaFlYpPXlHrT2c` |
| Objectives table (= "Outcomes" links) | `tblyZxi1nYrGICXrf` |
| Quarters table | `tblxO7vrTZq2gUtgq` |

## Tasks table — fields this workflow touches

| Field | ID | Type / notes |
|---|---|---|
| Task (name) | `fld1AkoHwZc1n9ynS` | singleLineText |
| Project | `fldA8WINLYYeMcJV2` | link → Projects |
| Outcomes | `fldxDjgnu1i9jp4jl` | link → Objectives |
| Parent Task | `fldBH3Rfbgsk17Py2` | link → Tasks (single-preferred) |
| Subtask (inverse of Parent) | `fldyEGvMRUqe2OgtI` | link → Tasks |
| Description | `fldvvDWMcV9g5gzPE` | richText |
| Status | `fldxcjBLLGOur6XIy` | singleSelect: Backlog, Blocked, Ready to Start, In Progress, Done, Cancelled, Someday/Maybe |
| Hours Estimated | `fld88Zg1liE6QHLNj` | number — the enrichment target |
| Hours Used | `fldouI8QvQhkjrpnx` | number — do NOT write during enrichment |
| Triage Notes | `flddo6Tc1mJoAt0qA` | multilineText — where cancel/dedupe explanations go |
| Triage Status | `fldMzsKOwaaGNEtBX` | singleSelect |
| Created time | `fldbh690V32q6BEDK` | createdTime |
| Archived | `fldCD9gdIan9M8wmV` | checkbox |
| Start date / Due date | `fldfHSCwqt7aB5va9` / `fld5LMZiISyZTKL0T` | date |
| Priority | `fldyqG9AcucrbXGPX` | singleSelect (P0–P4) |

## Objectives (Outcomes) table — fields for creating outcomes

| Field | ID | Notes |
|---|---|---|
| Title | `fldDDVTmTVQJIWK6w` | Prefix client work "CC: " etc., matching base style |
| Description | `fld7ngkZfcNCf6R0x` | Trace to source debrief + date |
| Status | `fldGtFG7NT82xMmY3` | Backlog / Ready to Start / In Progress / In Testing / Blocked / Done |
| Projects | `fldkd7ckyeFMwCuKs` | link → Projects |
| Owner | `fldOTG0XJsfgURuze` | singleCollaborator — Rachael = `{"id": "usr5vnH7D87XIP57C"}` |
| XRay's Clients | `fldGxQoN3SgbpQBG2` | link; (200) Coding Clarified = `recqM967hUDP0JohY` |
| Quarter | `fldI0uGigTNdgecG7` | link → Quarters. **Gap: no 2026 quarter records exist as of 2026-08-22** — do not invent them without approval |
| Start Date | `fldQfOtJSRrsBqZaf` | date |

## Known records (as of 2026-08-22)

| Record | ID |
|---|---|
| Project: Maintenance of current systems (CC) | `recOIaph0UwFYxlsB` |
| Outcome: Our Hourly Work | `recSy05yToaBpEfbt` |
| Outcome: CC: Transcript & Enrollment Document Overhaul | `recLn3QUK13yVfor7` |
| Outcome: CC: Contract Wrap-up & Transition | `rec0ukDR8n2u9j5Zf` |
| Outcome: Audit Tool: Deliverable Positioning & Beta | `recQ8SnMhBjh6zbfX` |
| Outcome: Monitor Student Status Automations → LOA & Graduated | `rec2RRAKmofRAx1u0` |
| Outcome: CC: Proposal follow-up automation health check | `recLU2u8YnZYKgcZw` |
| Collaborator: Rachael Quisel | `usr5vnH7D87XIP57C` (rachael@xray.tech) |
| Collaborator: Mark Campos | `usrN3p91dYDrHIz93` (mark@xray.tech) |

## Gotchas learned the hard way

The API token returns **403 on all deletes** — cancel with a Triage Note instead, and tell Rachael the record is ready for UI deletion. The debrief-extraction automation **double-fires**, creating duplicate tasks seconds apart; every sweep should check whether that root cause has been fixed yet. Done tasks get **archived while their Backlog duplicates stay live** — that is why the dedupe script treats archived Done records as evidence. Update responses echo the union of written field IDs across the whole call with *current* values for records that field was not written on — do not mistake those for your own writes. An Airtable automation appears to auto-link the client on outcomes in client-linked projects.
