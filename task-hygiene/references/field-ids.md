# Field ID Reference — Projects & Tasks at XRAY

Verified against the live schema 2026-08-22. If a write fails or a name looks off, re-fetch the schema (`list_tables_for_base` / `get_table_schema`) and trust the base over this file; note any drift in the post-run analysis.

## Base

| Thing | ID |
|---|---|
| Base: Projects & Tasks at XRAY | `appExample0000004` |
| Tasks table | `tblExample0000010` |
| Projects table | `tblExample0000023` |
| Objectives table (= "Outcomes" links) | `tblExample0000162` |
| Quarters table | `tblExample0000163` |

## Tasks table — fields this workflow touches

| Field | ID | Type / notes |
|---|---|---|
| Task (name) | `fldExample0000024` | singleLineText |
| Project | `fldExample0000033` | link → Projects |
| Outcomes | `fldExample0000164` | link → Objectives |
| Parent Task | `fldExample0000165` | link → Tasks (single-preferred) |
| Subtask (inverse of Parent) | `fldExample0000166` | link → Tasks |
| Description | `fldExample0000167` | richText |
| Status | `fldExample0000025` | singleSelect: Backlog, Blocked, Ready to Start, In Progress, Done, Cancelled, Someday/Maybe |
| Hours Estimated | `fldExample0000168` | number — the enrichment target |
| Hours Used | `fldExample0000169` | number — do NOT write during enrichment |
| Triage Notes | `fldExample0000170` | multilineText — where cancel/dedupe explanations go |
| Triage Status | `fldExample0000171` | singleSelect |
| Created time | `fldExample0000172` | createdTime |
| Archived | `fldExample0000030` | checkbox |
| Start date / Due date | `fldExample0000173` / `fldExample0000027` | date |
| Priority | `fldExample0000026` | singleSelect (P0–P4) |

## Objectives (Outcomes) table — fields for creating outcomes

| Field | ID | Notes |
|---|---|---|
| Title | `fldExample0000174` | Prefix client work "CC: " etc., matching base style |
| Description | `fldExample0000175` | Trace to source debrief + date |
| Status | `fldExample0000176` | Backlog / Ready to Start / In Progress / In Testing / Blocked / Done |
| Projects | `fldExample0000177` | link → Projects |
| Owner | `fldExample0000178` | singleCollaborator — Rachael = `{"id": "usrExample0000179"}` |
| XRay's Clients | `fldExample0000180` | link; (200) Example Nonprofit = `recExample0000043` |
| Quarter | `fldExample0000181` | link → Quarters. **Gap: no 2026 quarter records exist as of 2026-08-22** — do not invent them without approval |
| Start Date | `fldExample0000182` | date |

## Known records (as of 2026-08-22)

| Record | ID |
|---|---|
| Project: Maintenance of current systems (CC) | `recExample0000183` |
| Outcome: Our Hourly Work | `recExample0000184` |
| Outcome: CC: Transcript & Enrollment Document Overhaul | `recExample0000185` |
| Outcome: CC: Contract Wrap-up & Transition | `recExample0000186` |
| Outcome: Audit Tool: Deliverable Positioning & Beta | `recExample0000187` |
| Outcome: Monitor Student Status Automations → LOA & Graduated | `recExample0000188` |
| Outcome: CC: Proposal follow-up automation health check | `recExample0000189` |
| Collaborator: Rachael Quisel | `usrExample0000179` (person2@example.com) |
| Collaborator: Sky Bennett | `usrExample0000190` (person1@example.com) |

## Gotchas learned the hard way

The API token returns **403 on all deletes** — cancel with a Triage Note instead, and tell Rachael the record is ready for UI deletion. The debrief-extraction automation **double-fires**, creating duplicate tasks seconds apart; every sweep should check whether that root cause has been fixed yet. Done tasks get **archived while their Backlog duplicates stay live** — that is why the dedupe script treats archived Done records as evidence. Update responses echo the union of written field IDs across the whole call with *current* values for records that field was not written on — do not mistake those for your own writes. An Airtable automation appears to auto-link the client on outcomes in client-linked projects.
