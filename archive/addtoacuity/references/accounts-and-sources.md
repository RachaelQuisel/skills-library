# Accounts and source evidence

Use these as navigation hints for this private EA workflow. Verify current account identity, tables, fields, and permissions before use. Never reuse historical counts, dates, names, source filenames, or approvals as current facts.

## Acuity

- Expected account: **Example Agency - PROGRAM Training Team**.
- Expected public scheduling page: `https://exampleagencyrfatraining.as.me/`.
- Admin client list: `https://secure.acuityscheduling.com/admin/clients`.
- Import/export page: `https://secure.acuityscheduling.com/clients.php?action=importexport`.
- Verify the business name and scheduling-page URL in the signed-in browser. These admin URLs open whichever account is signed in; they are not account-specific links.
- Export **All clients** and record the actual filename and acquisition time. Generic names such as `list.csv` do not prove provenance. Avoid printing signed download URLs, credentials, or entire client pages.
- Inspect actual export headers. Typical client fields are `First Name`, `Last Name`, `Phone`, `Email`, and `Notes`. Client IDs may be unavailable in CSV; do not invent them.
- Treat booking history as separate evidence. A client directory entry does not establish a class registration, attendance, or a linked Airtable training record.

## Airtable

Discover and verify the EA Base (`appExample0000001`) through the installed Airtable CLI skill. The base contains both EA and PARTNER records.

| Table | Known ID | Read for this workflow |
| --- | --- | --- |
| `<Rachael>Applicant` | `tblExample0000002` | Record ID, name components, email, phone, Active, household role, Applications links, current person identifiers if present |
| `<Review>Application` | `tblExample0000003` | Record ID, Binti application ID, RFA ID, Applicants links, Client Type, Phase, Case Status, relevant source dates |

Resolve field IDs from the live schema. Retain raw field values and normalized comparison values. If live reads are unavailable, identify the supplied snapshot and date, and limit claims accordingly. Do not silently fall back to an old Applicants export.

Link verified records as `https://airtable.com/<base-id>/<table-id>/<record-id>`. A link on an Acuity client can be stale or point to the wrong person; it is evidence to verify, not unconditional proof.

## Four Binti groups

| Group key | Organization evidence | Stage evidence |
| --- | --- | --- |
| `ea-applications` | `CBOs` identifies Example Agency, including FFA variants | Application template and status indicate an application |
| `ea-renewals` | `CBOs` identifies Example Agency | Renewal template and/or `In Renewal` status |
| `partner-applications` | `CBOs` identifies Partner Agency Institute | Application template and status indicate an application |
| `partner-renewals` | `CBOs` identifies Partner Agency Institute | Renewal template and/or `In Renewal` status |

Read every row. Preserve mixed CBO memberships and flag unknown organizations or contradictory stage evidence. A `Renewal due date` column alone does not make a file a renewals export. Multiple organizations on one row may contribute to multiple group views; do not double-count that row in a combined total.

Keep application IDs, RFA IDs, row numbers, applicant/co-applicant roles, names, source dates, and source membership. A family-level Binti file is enough to extract the primary applicant and co-applicant; do not demand a separate Binti people export.

Preserve the exact source filename and SHA-256. Use user-supplied paths for Binti; do not scan Downloads, retrieve unprovided exports, or use modification time as an export date. Use a private run folder with restricted permissions. Never place private source data in the skill folder, a public report, or a Git commit.
