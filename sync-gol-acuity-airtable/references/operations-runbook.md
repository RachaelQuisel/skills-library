# Operations runbook

## Audit

Establish requested scope and mode. Record canonical realpath, relevant file hashes/local diff, base/table IDs, evidence time, and whether inspecting local or deployed code. Read applicable instructions without resetting unrelated changes.

Run `scripts/verify_local.py` from this skill. It reads canonical code/tests/workflow, captures test output, and emits counts, failing test identifiers, blocked-access counts, and source hashes. It removes service credential environment variables, denies network/subprocess/credential-file access, disables bytecode output, and checks inspected-file content for changes. It is a test harness with safeguards, not a general security sandbox. A blocked access is a failed verification even if a test catches the exception. For a relocated canonical checkout, pass `--automation-dir <verified-path>`.

To investigate a registration, collect only necessary fields privately: appointment ID/type/class/date/state; Tracking ID, Applicant/Schedule links, Registration Status and active attendance status; relevant Applicant identities; module mapping. Use the exact local matcher and deployed version independently when they differ. Trace the appointment's identity, Schedule resolution, duplicate state, and writer processing evidence. Return IDs/reasons, not names/contact dumps.

For live reads, discover the available connector or documented CLI read operations. Verify credentials without displaying them. Refresh schema and deployed consumers before proposing field changes. Do not start the sync merely to observe a log; dry runs do not write one.

## Find the actual writer and trigger

Inventory separately: G9 Automation Inventory/deployed settings and recent Automation Logs; GitHub workflow at the deployed revision and queued/running/completed runs; known local launchd/cron and running processes; external cloud routines or Codex automations relevant to this exact Acuity writer. Read only relevant definitions; sanitize command arguments and environment. A local process check cannot exclude a writer on another host.

Record for each candidate: target base, host/service, trigger, exact program/revision, state, observation time, and supporting run/process/log IDs. A writer can exist without a current running process. Log cadence supports activity but does not identify the host/source. A configured timer is not proof of execution. Missing access is unknown.

The inspected local workflow is dispatch-only. Dated September docs report a recurring external G9 writer with unverified host/source and no verified cloud timer. These are historical claims. Verify current runtime before reporting “running,” “stopped,” or “every 15 minutes.” Do not dispatch to test a trigger, create a replacement routine, or disable a timer during Audit.

## Preview existing paths

Use a fresh private directory **outside the repository and skill**, permission `0700`, with a restrictive umask. Core dry-run creation messages include participant names; ledger full plan includes display names. Capture raw output privately, produce only aggregate/ID/field-level sanitized findings, and never attach those files to public output. Backfill stdout is aggregate-only, but its in-memory plan and client CSV are sensitive. A local dry run can create/take an advisory lock; that does not write Acuity/Airtable.

From the canonical automation directory:

```sh
umask 077
gol_private_dir=$(mktemp -d)

# Recurring preview, matching the current workflow's Zoom-enabled preview
python3 acuity_new_base_sync.py --provision-zoom --zoom-seed-limit 5 >"$gol_private_dir/sync-preview.log" 2>&1

# Ledger preview: choose the private output path first
python3 applicant_training_requirement_ledger.py --output-dir "$gol_private_dir/ledger-preview" >"$gol_private_dir/ledger-preview.log" 2>&1

# Historical preview: supply approved dates and a current private client CSV
python3 acuity_historical_backfill.py --since "$gol_since" --through "$gol_through" --clients-csv "$gol_clients_csv" --summary-json "$gol_private_dir/backfill-summary.json"
```

Define task-specific date/CSV variables from verified inputs; do not use sample dates/paths as authorization. Keep core/ledger raw stdout/stderr private instead of streaming participant names or CLI errors into chat. Track each preview's exit status; executing the next command does not establish the previous one's success. Do not use apply flags, `--scheduled-apply`, live tool runners with `apply_plan`, or GitHub dispatch in Preview. Offline fixtures may call pure planners and mocked apply functions, with external I/O blocked.

Core `--limit` caps creates per pass, not all updates, link repairs, cancellations, logs, or Zoom actions. `--since` overrides only booking minDate. `--zoom-seed-limit 0` is uncapped. These are not general write-safety limits. The ledger's default output is a dated folder inside the repository; always override it for privacy and workspace preservation.

A two-program preview reads the current base twice: ledger preview does not simulate core's future writes. Describe dependent changes that require a subsequent fresh ledger plan. Backfill needs CSV headers `First Name`, `Last Name`, `Email`, `Phone`, `Notes`; uses Notes record IDs only if present in the current Applicant population; includes canceled history and approved mapped types. Saturated results split date ranges, then types; an unresolved saturated day/type aborts. Do not raise the saturation setting just to suppress incompleteness.

### Inspect individual backfill assignments

The CLI has no full-plan export option; `--summary-json` contains aggregates only. For a read-only assignment audit, import the canonical backfill module and instrument `build_backfill_plan` in a private local harness: retain its returned plan and input arguments while calling `main` with the reviewed preview arguments and **no `--apply`**. The existing CLI performs the read/normalization sequence; do not copy that sequence into a new production program. Keep captured inputs only in private memory. Make `_create_record`, `_update_record`, and `apply_plan` raise if called; this preview must never call them.

Inspect every `tracking_creates` action's `appointment_id`/`applicant_id`, and every `tracking_updates` action whose `fields` contains `core.TT_APPLICANT` (use `source_id`, `record_id`, and the proposed IDs). Compare current links in captured `tracking_records`; do not re-resolve an authoritative populated link. For each proposed new link, find its source appointment and run `resolve_applicant` with `build_identity_context` from captured `applicant_records`/`client_rows`; separately run `core.match_applicant` against that context's index. Keep the raw name/contact inputs private. Report only appointment/Tracking/Applicant IDs, reason, whether the name is blank, and whether exact/reviewed-name evidence supports the assignment. Treat broader contact/partial-name assignments as review items under the identity boundary. If the planner cannot be inspected this way, report assignment review incomplete and stop before apply; aggregate `review: 0` is insufficient.

## Apply gates and scope

Before any live write: confirm explicit user authorization already covers it; verify exact target, executable revision, fresh plan, identity/attendance invariants, and current single-writer ownership. If a writer cannot be excluded, stop before apply and report the evidence needed. Do not manufacture a machine-enforced writer gate: these programs have none across hosts.

| Path | Executable gate | Limitation |
| --- | --- | --- |
| Core `--apply` | Shared host-local advisory lock; dry-run default | No fingerprint, distributed lock, record-only selector, or whole-run transaction; broad changes including logs, potentially Acuity seeds |
| Manual ledger `--apply` | `--expected-fingerprint` equals fresh `action_fingerprint`; `--approved-active-source` equals `fld5G3LCJtl6wCvp6`; no review/data quality | Does not verify external writers or roll back partial writes |
| Ledger `--scheduled-apply` | Fresh internal plan/fingerprint; narrow canceled-attendance warning exception; fresh verification | Immediately writes without a supplied reviewed fingerprint; workflow authorization is not authorization for ad hoc use |
| Backfill CLI `--apply` | `--confirm-fingerprint` equals fresh target-bound plan; shared lock | Review flags can coexist with safe writes; `apply_plan` itself is not the CLI fingerprint guard; no cross-host exclusion |

Backfill confirmation uses the same reviewed date range/client CSV and a freshly rebuilt plan. Inspect concrete assignments for the stricter identity boundary in `identity-and-data-rules.md`. Never replace the supplied fingerprint with the new one just to pass a gate. The backfill fingerprint includes target/actions/review/Schedule resolution; it is not proof that every read field, mapping, or source file is unchanged.

For a narrow Applicant-link repair, review exact existing IDs and a patch limited to the empty Applicant field. Core has no record-only repair switch. Do not run its whole `--apply` under permission for one link; prepare a scoped canonical change or use a verified, explicitly authorized field-level write after rereading the target and duplicate state. Preserve attendance and populated links.

Perform one authorized execution, wait for its outcome, and inspect partial-write evidence before retrying. Do not automatically retry whole production runs, uncertain creates, or GitHub dispatch. Backfill retries reads/idempotent updates for selected transient failures, up to three attempts; creates retry only an explicit rate-limit rejection. Core's generic HTTP helper can retry on network failures, including Airtable creates; inspect current live keys before repeating an uncertain action. Seed POST retries are always disabled.

## Verify and recover

Record completed actions by table/source/record/field ID. Re-read the affected live records, confirming links, distinct appointment IDs, preserved attendance, cancellation handling, and ledger evidence. Replay no-apply plans against fresh data. Keep unresolved cases visible even when safe actions reach zero.

Core writes Automation Log/Inventory only in apply; logging failure warns without reversing changes. Its result is driven by Zoom and Pass C errors, not every identity/mapping/pagination issue. Ledger and backfill reread after apply and fail when safe work remains. Backfill checkpoint states distinguish `in_progress`, `failed`, `writes_complete`, `verified`, and `verification_failed`; `writes_complete` alone is not verification. Checkpoints are receipts, not an automatic resume/rollback system.

Keep private before-values and change IDs when planning an apply. After partial failure, stop further writes, inspect acknowledged actions and current source/target, then prepare a fresh preview. No program supplies transactional rollback. Restoring data, changing a timer/deployment, canceling seeds, or deleting history needs separately scoped explicit authorization. Preserve attendance and history during recovery.

To prove an automatic sync repair, also verify the authorized deployed revision, actual trigger/writer, and relevant live execution/records. Do not invent a test registration or send a notification without authorization.

## Single-writer production cutover

Prepare code/diff/tests/previews and a concrete rollback plan first. Identify all writers to this base and the exact writer to retain. Obtain only missing explicit permissions for commit/push/merge/dispatch/deployment/schedule actions.

Before starting the replacement, disable authorized old triggers, let in-flight work finish, and verify no old or queued competing run can write. Core/backfill share `/tmp/gol-acuity-new-base-sync.lock` by default (or `GOL_ACUITY_SYNC_LOCK_PATH`); this excludes only processes sharing that lock on one host. GitHub's concurrency group excludes only its own grouped runs. Neither excludes G9 elsewhere or an independently started ledger.

Start one authorized replacement run and verify both programs and live records before enabling a requested timer. An authorized read-only replay can establish idempotency without another production dispatch. For rollback, stop/drain the replacement before restoring an authorized former writer. Never leave two writers active to improve availability, and do not assume a presumed Mac timer is the unknown external G9 process.
