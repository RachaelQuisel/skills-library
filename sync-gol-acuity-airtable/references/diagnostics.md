# Diagnostics and evidence

Use sanitized identifiers/reason codes and a timestamp. Inspect raw contact data privately only when needed to resolve identity; no raw contact details, names, exported Notes, credential values, or Zoom passwords belong in a diagnostic report.

## Empty Applicant link

Trace appointment ID → keyed Tracking row → existing Applicant/Schedule links → participant matcher → active pair count. Determine which executable wrote the row before explaining its behavior. Use current code or a read-only pure matcher with protected inputs; do not invoke a writer to diagnose it.

| Reason / symptom | Interpretation and evidence |
| --- | --- |
| `name-no-match` | Nonblank participant name does not match exact/reviewed alias index. Staff contact cannot rescue it in recurring code. Check source name fields, current Applicant IDs, reviewed alias entries, and executable revision privately. |
| `ambiguous-name` | More than one name candidate and no unique compatible contact within candidates. Preserve ambiguity; do not take first candidate. |
| `conflicting-contact`, `ambiguous-contact` | Contact evidence cannot select one defensible ID. Inspect candidate sets without reporting contacts. |
| `duplicate-active-registration` | A different active linked row already represents that Applicant–Schedule pair. Inspect all such rows and registration states; one cancellation must not erase another active row's count. |
| `already-linked` | Link is populated and preserved; a mismatch is a review issue, not authority to replace it. |
| `appointment-unavailable` | Recheck could not retrieve an old keyed unlinked booking (403/404); retain review visibility, do not infer cancellation. |

`APPLICANT MATCH REVIEW` gives Tracking/appointment identifiers and reasons, including unresolved new rows. The documented `Acuity Applicant Match Review` view is intended to show keyed rows without Applicants; verify the current view/filter before relying on its coverage. A green G9 log can still contain unresolved links.

For staff bookings, an exact unique participant name can win over a staff contact. A failed name must remain reviewable. A populated Applicant link is authoritative even if fresh matching differs. Historical backfill's broader contact match is a separate source behavior; inspect its concrete plan for compliance before any apply.

## Missing/duplicate registrations and cancellations

- No mapping: recurring aborts when the mapping is entirely empty; unmapped types are skipped/reported. Backfill rejects duplicate type mappings; recurring overwrites them. Review current Training Module field values.
- Beyond class window or create cap: recurring may fetch the booking but defer it because Pass A did not resolve a Schedule. Increasing `--since` cannot reconstruct all historical classes.
- Old unlinked rows: current local code fetches individually outside the seven-day window. Compare deployed code before concluding why a record was missed.
- Duplicate appointment/source IDs: recurring dictionary indexing can hide duplicate rows; inventory the actual groups. Backfill flags affected keys. Distinct appointment IDs for one participant/session are retained by backfill but may be suppressed by recurring active-pair logic.
- Legacy migration: recurring accepts the first module/date/time-or-blank-start candidate; backfill flags multiple candidates. A classless derived occurrence must not adopt a blank-start migrated Schedule.
- Cancellation: read both active/canceled Acuity sets. Individual cancellation changes Registration Status, not class lifecycle; Attended rows need review. Recurring skips new canceled history while backfill records it. Active backfill snapshots can restore Registered; recurring does not do that automatically.
- `appts_truncated`: recurring cannot page beyond a saturated date and reports incomplete coverage without necessarily failing. Backfill fails closed when range/type splitting cannot establish completeness. A nonempty Acuity month protects against empty-response mass cancellation, not every partial result.

## Zoom and overall outcomes

Inspect source class/booking IDs, Schedule field IDs, seed count, capacity, and full three-fact compatibility. Duplicate placeholders, multiple meeting numbers, conflicting populated fields, incomplete source facts, no slot, and unsaved disagreement notes fail provisioning. A seed cap can defer work without failure. Pass C missing source/no Zoom facts is a count; its `errors` fails the combined outcome. Its numeric class-ID candidate commonly gives 403/404 before trying linked booking IDs.

`combined_run_outcome` checks provisioning failure and Pass C errors. It does not promote every unresolved identity, unmapped type, duplicate, truncation, or deferred booking to failure. Logging errors warn without undoing business writes. A successful ledger run does not validate Acuity or its trigger, and the GitHub job attempts ledger even after core failure.

Manual ledger apply blocks review/data quality; scheduled mode permits only canceled-session attendance warnings while removing invalid credit/reopening completion. Inspect active checkbox source, requirement key/identity, singular evidence links, and remaining plan counts. Ledger does not read Registration Status when deciding credit.

Backfill aggregate summary exposes `review_by_reason`, `match_by_reason`, ignored counts, planned writes, and fingerprint. These counts are insufficient to approve individual contact-based matches. Fingerprint drift means rebuild/review, not copy the new fingerprint into apply. Zero safe writes can coexist with unresolved review cases and an absent automatic trigger.

## Known source/documentation discrepancies

Inspected October 3, 2026 against the local working tree; recheck before reuse:

| Evidence | Discrepancy / operational implication |
| --- | --- |
| README and September 10 HowItWorks | Discuss deployed surname-component/global contact fallback and local safety work not deployed. Current local matcher uses only reviewed aliases, blocks fallback after a nonblank failed name, and rechecks older unlinked rows. Local code alone cannot verify whether that work is deployed now. |
| Recurring top-level docstring | Says rescheduled registrations are relinked. `booking_change_fields` and tests preserve populated Schedule links and report conflicts. |
| Pass C docstring/comments and summary wording | Suggest refreshing changed nonempty Zoom values or replacing a fallback address. Actual `zoom_detail_fields` is conflict-safe fill-empty; Location is fill-empty only. |
| README cutover steps | Put stopping unidentified recurring G9 after real cloud runs. Follow verified single-writer cutover **before** a replacement can write. |
| Historical docs / `_safe_contact_match` tests | Broader unique-phone and contained-name matches are intentional tested backfill behavior, but can conflict with this skill's staff-proxy/exact-name safety boundary. Do not apply incompatible assignments silently. |
| September operational counts/test results | 120 deployed tests and earlier write/link counts are dated evidence. Local offline verification during skill creation passed 180 tests (90 recurring, 54 backfill, 34 ledger, 2 workflow). Workflow tests inspect file text/dependency versions; existing sync/backfill tests do not exercise their complete `main()` flows. Neither count proves current deployment or live target state. |

Read `README.md` and both `GOL-HowItWorks-2026-09-10-Acuity-and-Training-Requirements-Sync.md` and `GOL-HowItWorks-2026-09-21-Acuity-Historical-Training-Backfill.md` for historical operational claims. Refresh current GitHub revision/runs, G9 logs, schedules, identities, and writer ownership before reporting production facts. Do not copy the documents' participant names or private record examples into this skill.
