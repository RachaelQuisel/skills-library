# Identity comparison rules

## Preserve what is being counted

- Keep one source occurrence per file, application row, and applicant/co-applicant role.
- Keep application, household, applicant-record, client-record, and distinct-person counts separate.
- Prefer verified stable person IDs for deduplication. Exact repeated source occurrences can be collapsed only with a retained membership list. Never merge people solely because they share a phone, email, or name.
- Report per-group totals and a deduplicated combined total only when the deduplication basis is defensible. Otherwise say “records” or “applicant/co-applicant entries.”

## Normalize without changing source data

- Retain raw values. Normalize case, whitespace, Unicode accents, punctuation, and name components only in comparison fields. Consider known middle-name/suffix variants; do not guess nicknames as confirmed identities.
- Trim valid emails and compare without case. Treat blanks and invalid addresses as missing, not match keys. Do not silently remove plus tags or otherwise rewrite email addresses.
- HTML-decode phone strings before removing punctuation. A leading `&#039;` is a garbled apostrophe, not country code `039`.
- Normalize supported national/international phone formats consistently. Do not drop extensions or truncate an unfamiliar number to force a match. Unsupported/invalid numbers need review when they are the only contact evidence.
- Index all nonblank normalized emails, phone numbers, names, and verified saved Applicant IDs. Retain every candidate, including duplicates, staff, test records, and shared household numbers.

## Binti to Airtable

1. Match the application using a unique Binti application ID; check RFA consistency when populated.
2. A unique RFA match can identify a candidate case when Binti IDs differ, but does not resolve the episode difference. Inspect current case/history evidence and the dedicated sync policy before declaring the application matched. Keep the discrepancy separate from person matching.
3. Resolve each person by a verified person ID or the uniquely linked application and household role, then check name/contact consistency. Do not declare a person present merely because the application exists.
4. When no linked person is found, search the whole Applicants table for stable IDs and compatible contact/name evidence before claiming an Airtable gap. Multiple candidates, conflicting roles, or mismatched IDs mean `Needs review`.
5. Retain a direct Binti-to-Acuity comparison even if Airtable has no matching person. Lack of an Airtable record does not imply lack of an Acuity client.

## Applicant to Acuity

Classify each person using the full candidate set:

| Evidence | Outcome |
| --- | --- |
| Unique saved Airtable Applicant ID on an Acuity client, compatible name, and no contradictory identity evidence | `Matched`; separately flag changed contact details |
| Compatible name plus a unique matching email or phone, with no conflicting contact, duplicate identity, or shared-key ambiguity | `Matched` |
| A saved ID points to another person's name, several clients, or a shared/duplicate Applicant record | `Needs review` |
| Email and phone point to different clients, or a shared family contact points to several people | `Needs review` |
| Exact name alone, a similar spelling, missing middle names, or a possible nickname without confirming evidence | `Needs review` |
| No credible candidate after ID/contact/name checks, sufficient source identity/contact information, and a complete current client list | `Not found in the checked source` |
| Incomplete export, wrong/unknown account, no usable identifying details, or conflicting source details | `Needs review` or source unavailable; never a confirmed absence |

Use fuzzy names only to surface review candidates. Never use a fuzzy score to authorize an addition, link two different people, or merge records. Where a Binti contact differs from Airtable, evaluate both against Acuity and keep disagreements visible; do not reuse the Airtable-only result without checking the newer source.

## Jev for unclear matches

- Use Jev (TypeSafe's decision model) only for people already marked `Needs review`. Exact Applicant ID, email, and phone checks still decide every clear match.
- Ask Jev one question per person: which Acuity client, if any, is this Applicant? Give up to 5 candidates, plus "none" and "unsure."
- Send Jev only what it needs to compare: names, role, and whether the email and phone match (yes or no). Never send the actual email address, phone number, or case details.
- If Jev picks one existing client with probability at least 0.90 and confidence at least 0.60, mark the person `Matched (Jev)`: they are already in Acuity, so do not create a client for them. Record Jev's pick, probability, and confidence in the comparison file, and list every `Matched (Jev)` person in the summary so it can be spot-checked.
- Anything lower, "unsure," or "none" stays `Needs review`. Jev's "none" never makes someone eligible for a new client, and a Jev match never edits or merges an Acuity client.
- If Jev isn't available, there's no key, or it returns an error, the person stays `Needs review`. Nothing is guessed.


After tentative matching, check many-to-one and one-to-many assignments. If several different Applicant IDs claim one Acuity client, return those identities for review. Do not “resolve” this by taking the first record.

Keep the confidence of identity separate from the accuracy of contact details. A verified ID/name pair can identify a person while their email still needs confirmation. Do not overwrite either source's nonblank contact information without authorization and evidence.

## Review and creation decisions

For each unresolved person, state the exact problem in plain English, list candidate names/links, and ask Pat to confirm the correct person, current details, and whether a new client is actually needed. Avoid “duplicate” unless duplication is verified.

A no-match becomes an eligible creation only after the source identity, required fields, live duplicate check, user authorization, and any requested Pat review are satisfied. Do not substitute an application match, an activity flag, or an aggregate number for these checks.
