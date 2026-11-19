# Audit Log Plugin: Implementation Plan

Date: October 4, 2026 (America/Los_Angeles)
Status: Phase 1 pilot is selected. The pilot automation is the `execute` skill (`audit-log-plugin/pilot.md`). This repository has no Automation Observability skill. The hosted collector, connected investigation tools, and database have not been deployed. The first slice records events in a local append-only log. The automation run verifier (`audit-log-plugin/scripts/automation_run_verifier.py`) reads that diary and gives one of three answers: verified, not achieved, or unknown.

## Goal

Let a user ask an automation “Why did you do that?”, inspect the recorded evidence, and request a scoped correction through chat.

Chat is the investigation and correction interface. Durable records provide the evidence. The agent must distinguish recorded facts, inferences, and unknowns rather than invent a retrospective explanation.

## First release

- One workspace and one pilot automation.
- One explicit business success condition.
- One supported correction type.
- Existing chat interface plus the installed investigation skill.
- Connected investigation tools, durable storage, and an always-on collector.
- Separate “fix this run” from “change future behavior.”

Hosting provider, storage provider, and a hosted correction adapter remain to be selected. The pilot workflow is the `execute` skill, specified in `audit-log-plugin/pilot.md`. This plan does not authorize production changes or enable notifications.

## Components

| Component | Responsibility |
| --- | --- |
| Skill | Instructions for evidence-based investigation and correction |
| Plugin | Package the skill with authenticated tool connections |
| Collector | Receive and durably persist background events |
| Database | Preserve runs, events, rule versions, decisions, and corrections |
| Tools | Retrieve evidence and perform narrowly authorized corrections |
| Chat LLM | Explain retrieved records and help scope corrections |
| Jev, optional later | Classify bounded semantic questions such as intent or incident category |

## Build sequence

### 1. Define the pilot

- [x] Select one existing automation.
- [x] Document its trigger, systems, expected result, and evidence proving that result.
- [x] Choose one correction, its scope, and required authorization.
- [x] Define expected schedules or deadlines when applicable.

Acceptance: an explicit success predicate and a concrete correction can be checked against the destination system. Pilot record: `audit-log-plugin/pilot.md`. The execute skill is user-invoked, so there is no schedule or deadline.

### 2. Build durable storage

- [ ] Implement the seven-table schema below.
- [ ] Preserve action-time rules and relevant redacted input snapshots.
- [ ] Separate execution status, business outcome, and telemetry health.
- [ ] Enforce workspace-scoped access and relationship consistency.
- [ ] Define retention and event-history write restrictions.

Acceptance: an earlier run remains explainable after a rule changes. Missing outcome evidence is represented as unknown.

### 3. Connect event collection

- [ ] Standardize event names, IDs, status values, and UTC timestamps.
- [ ] Carry one logical run ID through the workflow; assign separate attempt IDs to real retries.
- [ ] Record starts, handoffs, waits, results, failures, retries, and independently verified outcomes.
- [ ] Redact secrets and unnecessary personal information before storage.
- [ ] Deduplicate redelivery by source and event ID.
- [ ] Acknowledge only after durable persistence.
- [ ] Capture collector health and missing expected runs.

Acceptance: duplicate delivery creates no duplicate canonical event; late events do not regress completed work to running. Resending telemetry never repeats a business action.

### 4. Build investigation tools

- [ ] Find runs using ordinary-language context translated into authorized filters.
- [ ] Retrieve a run timeline, evidence, and the rule version used.
- [ ] List exceptions and inspect collector health.
- [ ] Include pagination, source coverage, and as-of timestamps.
- [ ] Keep read access separate from correction execution permissions.

Proposed tools: append_event, find_runs, get_run, list_exceptions, and get_telemetry_health.

Acceptance: a user can locate a run without knowing its ID and inspect evidence without gaining access to another workspace.

### 5. Connect chat and corrections

- [ ] Support “why,” “what changed,” “did it work,” and “fix this.”
- [ ] Explain using action-time inputs, rules, tool results, and recorded decision summaries when available.
- [ ] Label missing evidence and present-day inference.
- [ ] Prepare a concrete correction with target, scope, expected current state, and proposed value.
- [ ] Honor authorization already given within its scope.
- [ ] Check permissions, current version, prior effects, and idempotency before writing.
- [ ] Read back the result before reporting a verified correction.
- [ ] Preserve the original action and append linked correction events.
- [ ] For future behavior, create and verify a new rule version rather than relying on conversational memory.

Acceptance: one authorized correction is applied exactly once, independently verified, and traceable to its request. A failed or unavailable write remains failed or pending.

### 6. Test, package, and deploy

- [ ] Validate the scenarios in the release checklist.
- [ ] Package the skill and real tool connections using the host's supported plugin format.
- [ ] Deploy the collector and storage to a persistent hosted environment.
- [ ] Verify operation while the user's computer is offline.
- [ ] Verify collector freshness and delivery-failure reporting.
- [ ] Enable notifications only when requested and configured.

Acceptance: one real workflow can be traced, explained with evidence, corrected, and independently verified through chat.

## Data model

All tables carry workspace_id and created_at. IDs use UUIDs in the proposed relational model; timestamps use TIMESTAMPTZ. Enums have explicit allowed values. JSONB stores structured, redacted data. Actor identities and chat references use existing identity and conversation systems.

| Table | Key fields and data types | Relationships |
| --- | --- | --- |
| Workflows | workflow_id UUID PK; name TEXT; platform ENUM; outcome_check JSONB (success predicate the automation run verifier applies) | One workflow has many rule versions |
| Rule Versions | version_id UUID PK; workflow_id UUID FK; version_number INTEGER; rules_snapshot JSONB; definition_ref TEXT; effective_at TIMESTAMPTZ | One version has many runs |
| Runs | run_id UUID PK; version_id UUID FK; parent_run_id UUID nullable FK; execution_status ENUM; business_outcome ENUM; expected_by TIMESTAMPTZ nullable | One run has many events and decisions; optional parent-child runs |
| Events | event_id UUID PK; run_id UUID FK; source TEXT; source_event_id TEXT; occurred_at TIMESTAMPTZ nullable; observed_at TIMESTAMPTZ; event_type ENUM; data_redacted JSONB | Events can support decisions and be targeted by corrections |
| Decisions | decision_id UUID PK; run_id UUID FK; model_id TEXT; question_snapshot JSONB; state_snapshot_ref TEXT; answer JSONB; probabilities JSONB nullable; confidence NUMERIC nullable; gate_snapshot JSONB | Decisions link to supporting events through Evidence Links |
| Evidence Links | evidence_link_id UUID PK; decision_id UUID FK; event_id UUID FK; role ENUM | Many-to-many join between decisions and events |
| Corrections | correction_id UUID PK; target_event_id UUID FK; requested_by TEXT; chat_ref TEXT; scope ENUM; proposed_change JSONB; status ENUM; verification_event_id UUID nullable FK; new_version_id UUID nullable FK | Links a request to the original action, verification evidence, and an optional new rule version |

Database constraints must enforce workspace boundaries, unique event delivery keys, and valid references. An editable Airtable table is not inherently immutable; an Airtable implementation needs equivalent validation and an explicit enforcement policy.

### Important states

- Execution: queued, running, waiting, completed, failed, cancelled, unknown.
- Business outcome: verified, not_achieved, unknown.
- Telemetry health: current, delayed, incomplete, unavailable, unknown.
- Correction: requested, authorized, applied, verified, failed, rejected.

Applied is not the same as verified. A timeout does not prove that the remote action failed.

## Jev: later evaluation

Start with deterministic checks and the existing chat model. Once collection works, test Jev on narrow decisions such as user intent or incident classification.

Retain the question, input snapshot, model identity, typed response, probabilities, and the actual gate used. Keep permission checks, exact deadlines, version checks, and duplicate prevention in code. Test thresholds against representative labeled cases before automating actions. Confidence is not authorization or proof of correctness.

Jev's Choice and Score responses include confidence; Noul returns a probability without a separate confidence field.

Reference: https://docs.typesafe.ai/introduction
Reference: https://docs.typesafe.ai/confidence

## Release checklist

- [ ] Normal run reaches a verified business outcome.
- [ ] Duplicate event delivery is deduplicated.
- [ ] Real retries remain separate attempts under the same logical run.
- [ ] Out-of-order events preserve the correct state.
- [ ] A timeout followed by a successful remote save does not cause a blind replay.
- [ ] Partial completion identifies the unfinished step.
- [ ] Missing logs and collector outages are visible as telemetry gaps.
- [ ] A scheduled run that never starts is detectable from an independent expectation.
- [ ] Another workspace's records remain inaccessible.
- [ ] A changed policy does not rewrite an earlier explanation.
- [ ] Missing decision evidence produces an honest unknown.
- [ ] An authorized correction is applied once and read back.
- [ ] A failed correction is never reported as successful.
- [ ] A future-rule correction creates a new version and verifies that it is used.

## Next action

Phase 1 is complete. The success predicate and the reopen correction are in `audit-log-plugin/pilot.md`. Next, back the schema with a hosted database and connect a collector that uses the same event contract.
