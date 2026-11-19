# Identity and data rules

Read current implementations and named tests before changing these rules. These describe local behavior, not a deployment guarantee.

## Recurring participant matching

`build_applicant_indexes` / `match_applicant` treat Acuity `firstName`/`lastName` as the participant, even when a staff member supplies email/phone.

1. Normalize with NFKD, remove combining marks, casefold, replace non-ASCII-alphanumeric runs with spaces, collapse whitespace; key is normalized `first|last`.
2. A unique exact name wins regardless of a different contact match. Duplicate exact names can use contact evidence restricted to those name candidates.
3. Only aliases in `APPROVED_NAME_ALIASES` are indexed. Read the current reviewed entries in source; do not copy participant names into the skill or generate aliases from surname components. Ambiguous aliases can use contact evidence within their candidates.
4. A nonblank unmatched name yields `name-no-match`. Global contact fallback is available only for a fully blank name (`|`). Email is stripped/lowercased; phone uses the final ten digits only when at least ten exist. Contact intersection must resolve uniquely; conflict or ambiguity remains unlinked.

`existing_applicant_link_change` is fill-empty only. A populated Applicant link returns `already-linked`. For an active unlinked row, an existing active Applicant–Schedule pair blocks filling (`duplicate-active-registration`). Canceled history can gain a safe Applicant link without becoming active. Active counts retain another duplicate when one row cancels; a set-based decrement would lose that distinction.

`fetch_unlinked_appointments` fetches all keyed Tracking rows lacking an Applicant, including bookings older than seven days. Unavailable bookings remain review items; no guessed link or deletion.

## Registration and Schedule behavior

| Case | Recurring sync | Historical backfill |
| --- | --- | --- |
| Keyed Tracking row | Uses appointment ID; fills empty links, preserves populated links | Blocks duplicate keyed IDs; existing single Applicant link is authoritative; fills missing links/raw identity fields |
| New active booking | Requires a resolved Schedule; skips creation when a linked active Applicant–Schedule pair already exists | Retains every distinct appointment ID, including repeats for same Applicant–Schedule |
| New already-canceled booking | Does not create Tracking | Records canceled history with Schedule; does not cancel the whole class |
| Existing canceled booking | Updates Registration Status except an `Attended` row; never rewrites populated Schedule | Same attendance protection for cancellation; can restore blank/Cancelled Registration Status to Registered on an active snapshot |
| Unmatched participant | May create Tracking with Schedule and blank Applicant | Same visibility; review flags do not by themselves block all safe backfill writes |
| Legacy unkeyed Tracking | May suppress a new active pair without stamping an appointment ID | Adopts one unambiguous legacy row; competing incoming IDs or ambiguous legacy rows cause separate keyed creates |

Recurring code indexes keyed Tracking/Schedule records into dictionaries without duplicate-key guards. Audit duplicate appointment/source IDs; do not assume its success validates uniqueness. Backfill explicitly flags duplicate IDs and blocks affected actions.

Recurring `booking_change_fields` never replaces a populated Schedule link; a reschedule conflict needs review. The top-level docstring's “relinks rescheduled registrations” is stale. A cancellation review may coexist with a separate fill-empty Applicant action: “left unchanged” is not necessarily a statement about every field on that row.

Schedule updates may change module, title, language, dates, end/start, signup URL, source system, and lifecycle notes. Modality and Location are fill-empty only. A start move greater than 60 seconds marks `Rescheduled`; a reappearing canceled class returns to `Scheduled`. Missing numeric-source future classes are canceled only inside the scanned window and a month with other returned classes. An empty month gives no cancellation evidence; a nonempty month does not prove completeness. Already-canceled numeric classes can receive a missing `Cancelled —` title prefix even outside the future window.

Recurring migration adoption uses `gol-` source keys, same module/date, start within 30 minutes or a blank migrated start, and first matching candidate. It does not reject every ambiguous migration group. Backfill requires a unique migration candidate; classless derived occurrences require a stored migrated start.

## Historical identity differences and skill boundary

`resolve_applicant` supports a valid client-export Notes ID bridge matched by exact exported client name and contact, and certain appointment form IDs corroborated against the full Applicant population. A supplied record ID is not an authenticated foreign key; conflicts remain review items.

After the recurring matcher fails, `_safe_contact_match` can select a unique phone even with a different nonblank name, or email plus contained first and last Applicant name phrases. Tests explicitly accept these broader behaviors (`test_unique_normalized_phone_is_a_safe_match_even_when_name_differs`, `test_email_plus_contained_first_and_last_name_is_a_safe_match`). This is not the recurring sync's exact-name gate, and a unique phone is not proof that the contact belongs to the participant.

**Under this skill, never apply an identity link based on staff contact after a nonblank name failed.** Examine the concrete planned Applicant assignments privately, not aggregate reason counts alone. Flag contact-only or unreviewed partial-name assignments for human review. If the executable plan violates the requested boundary, stop before apply and prepare a scoped canonical-code correction or reviewed alias/identity evidence; do not hand-edit a plan/fingerprint or silently broaden identity rules. Existing links remain authoritative, even where fresh name matching differs.

## Backfill occurrence identity

Use classID when available. A missing classID can reuse a unique real occurrence signature: module, parsed start, calendar, language, modality. Otherwise `_derived_source_key` uses `acuity-derived-v1:<type>:<ISO-start>:<calendar-or-no-calendar>`.

The plan rejects inconsistent snapshots, duplicate source keys, module/time conflicts, and ambiguous classless or migrated groups. An already-keyed occurrence can be reused within 60 seconds with compatible stored language/modality. Do not equate a participant cancellation with class cancellation. Backfill creates neutral `Scheduled` classes even if all observed registrations canceled.

## Attendance and ledger

Core `NEVER_WRITE_FIELDS` is **PATCH-only**: active attendance/event status, legacy attendance status, Attendance Source, Attendance, and archived Status are protected after creation. Creates initialize active status `Pending` and archived Status `RSVP`. Do not extend the deny-list to creates without redesigning those initializers. Link repairs never change attendance decisions.

Ledger current scope is strictly `Application Active is True` and every linked Applicant, with the five `INITIAL_MODULE_IDS` in source. Requirement identity/key is `<application>:<applicant>:<module>:Initial`. Historical requirements and Tracking without Applicants are preserved. Do not substitute an inferred case status or different active field.

Evidence needs one Applicant, one Schedule, one module, and a defensible active Application context. Duplicate/mismatched requirements, conflicting existing requirement links, missing Schedule/module, or multiple active Applications cause review. Missing Applicant display name is data quality and blocks apply.

Completion requires event status exactly `Attended` and Schedule status other than `Cancelled`; Registration Status is not loaded by this planner. Never add a registration-state credit gate silently. One qualifying attendance gets unique module credit: retain an already-credited valid occurrence when possible, otherwise select earliest Schedule date and then Tracking ID. Clear credit on other matching occurrences. Existing requirement updates contain only completion result; evidence links and credit are separate writes. New requirement creates can include safe Tracking evidence via the reciprocal link.

Manual ledger apply rejects every review/data-quality item. Scheduled reconciliation treats only `cancelled_session_attendance_conflict` as a warning, permits safe credit removal/result reopening, and checks fresh remaining actions. Attendance itself stays intact. Do not generalize that exception to other review items.

## Zoom

Future virtual Scheduled/Rescheduled classes may use real active bookings or exactly one internal seed. The seed has no email/phone, a deterministic class marker, `smsOptIn: false`, and admin/no-email creation. It is excluded from participant processing; no appointment deletion is performed.

Preview can count would-seed/would-fill without writing. Apply rechecks active bookings before a single non-retried seed POST and rereads Airtable before provisioning fields. The default CLI cap is five **attempts**, including uncertain responses; zero removes the cap and is not an innocuous option.

Guarded updates to an existing Schedule are compatible and complete across meeting ID/URL/readable password, using already populated compatible values where needed. Conflicts or missing facts prevent those fills. New Schedule creates instead use `build_schedule_fields`, which includes each available Zoom fact independently; initial metadata may be partial. Do not extend the update guarantee to create-time metadata. Disagreements can add Source Notes during apply. Duplicate seeds, differing meeting IDs, capacity blocks, incomplete results, errors, and unsaved notes fail provisioning; seed-cap deferral alone does not fail it. Pass C also uses conflict-safe fills despite stale comments claiming refresh/overwrite. Never reproduce Zoom passwords or credentialed links in diagnostics.
