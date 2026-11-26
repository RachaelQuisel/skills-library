# Evidence, review lists, and communication

Save private outputs in a single run folder. Use empty/header-only lists when a category is empty, so zero and “not checked” remain distinguishable.

## Required artifacts

| Output | Required contents |
| --- | --- |
| `source-inventory.json` | Requested scope; groups received/pending/out of scope; exact paths/fingerprints; organizations/statuses; CSV row and applicant occurrence counts; export/acquisition dates and timezone; account evidence; completeness and warnings |
| `comparison.csv` | All scoped source people, organization and application/renewal stage, source file/row/role, Binti/RFA identifiers, Airtable application and Applicant IDs/links, raw Binti status, Active checkbox, recent date/definition, separate Airtable and Acuity outcomes, candidate links, match evidence, review reason |
| `review-for-pat.csv` | Potentially missing and uncertain people; source group, active/recent priority, possible matches, the precise question to resolve, and where to open the relevant records |
| `proposed-additions.csv` | Candidate name, verified proposed fields, source and account, current match evidence, approval/review state and provenance; never label this file as already imported |
| `write-receipt.csv` | Run key; approved source person; before-state; action attempted; timestamp; persisted client ID/URL or search reference; readback evidence; final state; any failure or unknown save outcome |
| `summary.md` | Dated estimates with exact denominators available in evidence; scoped coverage; verified writes; unresolved questions; missing inputs; links to review/addition/receipt files |

Keep contact details only in private working outputs needed for matching/review. Do not include case histories or unnecessary sensitive fields. Escape spreadsheet formula-leading values in human-facing CSVs without altering the original source or the canonical matching data. Document that display escaping so it is never copied into Acuity fields.

## Count checks

- Ensure `matched + not found + needs review` equals each checked group's denominator; keep “source unavailable/not checked” separate.
- Ensure all source occurrences remain represented, including people who could not be linked to Airtable.
- Verify both primary and co-applicant roles. Flag mismatches against `Number of applicants`.
- Disclose cross-group overlaps before presenting a combined unique-person total.
- Show applications and renewals separately for EA and PARTNER. Clearly distinguish a whole-base comparison from a Binti-export subset.
- Describe unchecked Active records as “not marked Active,” not proven inactive. Do not drop current Binti applications from follow-up because the Airtable flag disagrees.
- Keep uncertain matches out of the no-match count. Keep unverified saves out of the confirmed-created count.

## Suggested concise report

State the verified Acuity account, export filename/date, and scoped Binti files first. If totals are requested, give rounded counts for Airtable applicants, Acuity clients (including test records), potential gaps, and unresolved matches. Break gaps down by organization and applications/renewals. For recent/active coverage, give matched versus no-match versus unresolved for the same clearly defined subset.

Round appropriately (for example, to the nearest 10, 50, or 100 depending on scale); do not obscure a small named list with a false estimate. Preserve exact counts privately. Avoid implying rounded figures add up exactly or that records are all distinct people.

## Pat email

Default to the current user's narrow email scope: recent Binti applicants with a `Not found in the checked source` result in Airtable or Acuity. Exclude people whose only unresolved result is `Needs review`, even when the broader assignment asks for a full comparison and review list. Include uncertain matches in the email only when the user explicitly requests that email scope. Do not copy old names, old dates, account totals, or renewal counts into a new email.

Use this structure, filling only verified facts:

> Subject: Recent [organization] applicants to review in [system]
>
> Hi Pat,
>
> [Describe the specific verified updates already made, naming the source export. Omit this sentence when no business records were changed.]
>
> [Identify the exact Binti export and recent date window. State which system the people already appear in and which source did not show a match. Include the Acuity account name and a verified link to its client list when relevant.]
>
> [List only recent potential gaps. Put uncertain possible matches in the separate review attachment; do not list their names here unless explicitly requested. If there are no recent potential gaps, state that instead.]
>
> Please confirm their contact details and check whether they already have records under another name. These records need your review before we add or change them.
>
> Thanks,
> Rachael

Show the actual email text when asked. State “draft saved, not sent” outside the email. Link only artifacts that exist. Do not describe a local file as attached to an email unless it was actually attached. Keep tool failures, Voice Align receipts, and Teams setup details outside Pat's applicant email.

## Completion and retries

For a comparison-only request, finish with verified scoped outputs and remaining gaps. For an authorized addition request, finish only after persisted clients are checked and unresolved saves are identified. If an external service is unavailable, preserve completed work and explain the specific remaining action; do not rerun successful creates to regenerate a report.

An optional user-requested Automation Log should describe the current run and evidence without row-level personal data. It is not a default requirement of this skill. Never create a Teams automation or send a message as an incidental side effect of reconciling clients.
