# Reliable interactions

## Define the complete save lifecycle

For each mutation, define eligibility, field payload, permissions, pending feedback, acknowledgement, failure and recovery. Recheck current record membership and ownership at action time. Validate the actual SDK, not a remembered Base Extension API when this is an Interface Extension.

Disable duplicate actions while pending. A rejected save must retain the user's context and show a useful error. An uncertain acknowledgement must not permit blind retries that can duplicate work. Use optimistic state only when it helps the interaction; roll it back on failure and retire it when live data acknowledges the change. Handle removal, reassignment and conflicting edits rather than masking them indefinitely.

Saving a record and observing matching saved data are separate evidence. Use a proportionate acknowledgement/timeout strategy. Never substitute success wording for a missing result.

## Completion, uncheck and earned points

Completion may span a Done checkbox, a Status choice and a completion timestamp. Write the complete project-approved payload coherently. Reopen must clear or restore all required metadata while leaving unrelated application phase/status alone.

Confetti, sparkles and success messages must follow confirmed completion, not initial render or clicking the checkbox. A saved action can offer a practical undo. Do not replay celebrations from previously completed records merely because the application was reopened in the UI. Reduced motion should suppress movement/celebrations where appropriate.

Define whether points represent currently completed work, a period total or an immutable ledger. If they derive from saved completed rows, calculate them before view filters and use the same eligibility model across panels. Unchecking reverses that row's points; rechecking restores them without accumulation. Reassignment, deletion or excluded rows can change this total. Do not call it a permanent lifetime reward ledger unless the data supports that claim.

Test repeated clicks, rejection, uncertain acknowledgement, other staff's work, filtered views and reopen/recheck. Keep inconsistent completion metadata visible for review instead of guessing a completed/open state.

## Documents without a setup form

Keep the common interaction simple: choose the document, download its template, choose the relevant person when required, upload the completed file, and see its saved attachment state. Put record construction behind that action rather than exposing every storage field to staff.

Confirm the supported attachment mechanism in the actual SDK. If it cannot accept authenticated binary files directly, use the native Airtable record-detail attachment window. Do not invent a browser uploader that embeds a token, requires unrequested infrastructure or writes an unsupported payload.

Create or reuse the minimal linked record for the document, application and applicant. A single eligible applicant can be preselected; multiple applicants require an intentional choice. Revalidate application membership before writing/opening, preserve valid existing multi-applicant links, and block a missing/outsider person.

Protect existing attachments and notes. Match by verified links, not free-text names. Reuse an existing matching record; when multiple valid duplicates exist, give a choice rather than creating another one. Guard simultaneous or uncertain creation. A task association can be optional: application-level documents must remain usable when the application has no tasks or no task Notes permission.

If the native flow creates the linked record before file selection, say so in the implementation notes. Cancellation may leave an empty record; a retry should reuse it. Opening or creating the record is not evidence that the file was attached. Report File attached only from saved attachment data. An Airtable attachment is not proof of submission to another system.

## Configure native capabilities as well as source

Check required tables/fields in the element's Data settings, creation/edit permission for the destination table, and enabled native record details. Make the correct Attachments field visible, editable and easy to find. An enabled custom Upload button cannot repair a hidden/read-only native field.

Inspect whether native layouts are shared. Duplicate a shared layout before changing it for a versioned interface. Keep templates read-only and avoid enabling deletion merely to support uploads. Removing a broken display element from a copied layout is different from deleting its underlying table/field/record.
