-- Audit log storage contract (PostgreSQL).
--
-- Retention: keep event rows for 30 days after observed_at. Expiry is a future
-- hosted job. Do not cascade-delete history when a workflow or rule changes.
--
-- Write restriction: events and rule_versions are append-only. A correction
-- inserts a corrections row and appends a new event. A behavior change inserts
-- a new rule_versions row. Runs keep the version_id they started with, so an
-- earlier run stays explainable after a rule changes.
--
-- Workspace boundary: every table carries workspace_id. Child rows repeat it
-- and foreign keys include it, so a row cannot point at another workspace.
-- Set app.workspace_id for the row-level security policies below.
--
-- Applied is not verified. A correction status of applied means the write was
-- read back. verified is a later, separate state.
--
-- gen_random_uuid() is built into PostgreSQL 13 and later. On PostgreSQL 12
-- and earlier it is provided by pgcrypto. The extension is safe to create on
-- newer servers as well.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TYPE platform AS ENUM (
  'local_agent',
  'cursor',
  'claude',
  'zapier',
  'airtable',
  'other'
);

CREATE TYPE execution_status AS ENUM (
  'queued',
  'running',
  'waiting',
  'completed',
  'failed',
  'cancelled',
  'unknown'
);

CREATE TYPE business_outcome AS ENUM (
  'verified',
  'not_achieved',
  'unknown'
);

CREATE TYPE telemetry_health AS ENUM (
  'current',
  'delayed',
  'incomplete',
  'unavailable',
  'unknown'
);

CREATE TYPE event_type AS ENUM (
  'run.started',
  'task.started',
  'task.files_changed',
  'verification.ran',
  'task.completed',
  'run.escalated',
  'run.completed',
  'correction.reopened'
);

CREATE TYPE evidence_role AS ENUM (
  'supporting',
  'contradicting',
  'context'
);

CREATE TYPE correction_scope AS ENUM (
  'this_run',
  'future_behavior'
);

CREATE TYPE correction_status AS ENUM (
  'requested',
  'authorized',
  'applied',
  'verified',
  'failed',
  'rejected'
);

CREATE TABLE workflows (
  workflow_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  name TEXT NOT NULL,
  platform platform NOT NULL,
  -- Success predicate for this workflow. The automation run verifier
  -- (audit-log-plugin/scripts/automation_run_verifier.py) reads the audit
  -- diary and applies this predicate.
  outcome_check JSONB NOT NULL,
  UNIQUE (workspace_id, workflow_id)
);

CREATE TABLE rule_versions (
  version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  workflow_id UUID NOT NULL,
  version_number INTEGER NOT NULL CHECK (version_number > 0),
  rules_snapshot JSONB NOT NULL,
  definition_ref TEXT,
  effective_at TIMESTAMPTZ NOT NULL,
  UNIQUE (workspace_id, workflow_id, version_number),
  UNIQUE (workspace_id, version_id),
  FOREIGN KEY (workspace_id, workflow_id)
    REFERENCES workflows (workspace_id, workflow_id)
);

CREATE TABLE runs (
  run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  version_id UUID NOT NULL,
  parent_run_id UUID,
  execution_status execution_status NOT NULL,
  business_outcome business_outcome NOT NULL,
  telemetry_health telemetry_health NOT NULL DEFAULT 'unknown',
  expected_by TIMESTAMPTZ,
  UNIQUE (workspace_id, run_id),
  FOREIGN KEY (workspace_id, version_id)
    REFERENCES rule_versions (workspace_id, version_id),
  FOREIGN KEY (workspace_id, parent_run_id)
    REFERENCES runs (workspace_id, run_id)
);

CREATE TABLE events (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  run_id UUID NOT NULL,
  attempt_id UUID NOT NULL,
  source TEXT NOT NULL,
  source_event_id TEXT NOT NULL,
  occurred_at TIMESTAMPTZ,
  observed_at TIMESTAMPTZ NOT NULL,
  event_type event_type NOT NULL,
  data_redacted JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (workspace_id, event_id),
  UNIQUE (workspace_id, source, source_event_id),
  FOREIGN KEY (workspace_id, run_id)
    REFERENCES runs (workspace_id, run_id)
);

CREATE TABLE decisions (
  decision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  run_id UUID NOT NULL,
  model_id TEXT,
  question_snapshot JSONB NOT NULL,
  state_snapshot_ref TEXT,
  answer JSONB NOT NULL,
  probabilities JSONB,
  confidence NUMERIC,
  gate_snapshot JSONB,
  UNIQUE (workspace_id, decision_id),
  FOREIGN KEY (workspace_id, run_id)
    REFERENCES runs (workspace_id, run_id)
);

CREATE TABLE evidence_links (
  evidence_link_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  decision_id UUID NOT NULL,
  event_id UUID NOT NULL,
  role evidence_role NOT NULL,
  UNIQUE (workspace_id, decision_id, event_id, role),
  FOREIGN KEY (workspace_id, decision_id)
    REFERENCES decisions (workspace_id, decision_id),
  FOREIGN KEY (workspace_id, event_id)
    REFERENCES events (workspace_id, event_id)
);

CREATE TABLE corrections (
  correction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  target_event_id UUID NOT NULL,
  requested_by TEXT NOT NULL,
  chat_ref TEXT,
  scope correction_scope NOT NULL,
  proposed_change JSONB NOT NULL,
  status correction_status NOT NULL,
  verification_event_id UUID,
  new_version_id UUID,
  FOREIGN KEY (workspace_id, target_event_id)
    REFERENCES events (workspace_id, event_id),
  FOREIGN KEY (workspace_id, verification_event_id)
    REFERENCES events (workspace_id, event_id),
  FOREIGN KEY (workspace_id, new_version_id)
    REFERENCES rule_versions (workspace_id, version_id)
);

COMMENT ON TABLE events IS
  'Append-only. Pilot retention is 30 days from observed_at. Dedupe key is (workspace_id, source, source_event_id).';

COMMENT ON TABLE rule_versions IS
  'Append-only action-time rule snapshot. A later version does not rewrite runs that point at an earlier version_id.';

CREATE OR REPLACE FUNCTION reject_append_only_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  RAISE EXCEPTION 'append-only table; insert a new row instead of changing history';
END;
$$;

CREATE TRIGGER events_append_only
  BEFORE UPDATE OR DELETE ON events
  FOR EACH ROW
  EXECUTE PROCEDURE reject_append_only_mutation();

CREATE TRIGGER rule_versions_append_only
  BEFORE UPDATE OR DELETE ON rule_versions
  FOR EACH ROW
  EXECUTE PROCEDURE reject_append_only_mutation();

ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflows FORCE ROW LEVEL SECURITY;
CREATE POLICY workflows_workspace_isolation ON workflows
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid)
  WITH CHECK (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);

ALTER TABLE rule_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE rule_versions FORCE ROW LEVEL SECURITY;
CREATE POLICY rule_versions_workspace_isolation ON rule_versions
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid)
  WITH CHECK (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);

ALTER TABLE runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE runs FORCE ROW LEVEL SECURITY;
CREATE POLICY runs_workspace_isolation ON runs
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid)
  WITH CHECK (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);

ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE events FORCE ROW LEVEL SECURITY;
CREATE POLICY events_workspace_isolation ON events
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid)
  WITH CHECK (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);

ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisions FORCE ROW LEVEL SECURITY;
CREATE POLICY decisions_workspace_isolation ON decisions
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid)
  WITH CHECK (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);

ALTER TABLE evidence_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_links FORCE ROW LEVEL SECURITY;
CREATE POLICY evidence_links_workspace_isolation ON evidence_links
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid)
  WITH CHECK (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);

ALTER TABLE corrections ENABLE ROW LEVEL SECURITY;
ALTER TABLE corrections FORCE ROW LEVEL SECURITY;
CREATE POLICY corrections_workspace_isolation ON corrections
  USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid)
  WITH CHECK (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid);
