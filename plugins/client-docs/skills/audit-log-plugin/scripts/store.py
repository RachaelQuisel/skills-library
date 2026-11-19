"""SQLite test double for schema/001_init.sql.

The SQL file is the PostgreSQL storage contract. This module translates the
table definitions far enough to exercise workspace-scoped foreign keys, the
event delivery key, and rule-version readback. workflows.outcome_check stores
the success predicate the automation run verifier applies. Row-level security, enum types,
and append-only triggers stay in the SQL
file for the hosted database.
"""

from __future__ import annotations

import json
import re
import sqlite3
import uuid
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema" / "001_init.sql"

TABLES = (
    "workflows",
    "rule_versions",
    "runs",
    "events",
    "decisions",
    "evidence_links",
    "corrections",
)


def translate(sql: str) -> list[str]:
    without_comments = re.sub(r"/\*.*?\*/", "", sql, flags=re.S)
    without_comments = re.sub(r"--[^\n]*", "", without_comments)
    without_functions = re.sub(
        r"CREATE\s+OR\s+REPLACE\s+FUNCTION\b.*?\$\$.*?\$\$\s*;",
        "",
        without_comments,
        flags=re.I | re.S,
    )
    without_hosted = re.sub(
        r"\b(?:CREATE\s+TRIGGER|CREATE\s+POLICY|CREATE\s+EXTENSION|ALTER\s+TABLE|COMMENT\s+ON)\b.*?;",
        "",
        without_functions,
        flags=re.I | re.S,
    )
    enums: list[str] = []

    def capture_enum(match: re.Match) -> str:
        enums.append(match.group(1))
        return ""

    without_enums = re.sub(
        r"CREATE\s+TYPE\s+(\w+)\s+AS\s+ENUM\s*\((.*?)\)\s*;",
        capture_enum,
        without_hosted,
        flags=re.I | re.S,
    )
    translated = without_enums
    translated = re.sub(r"\bUUID\b", "TEXT", translated)
    translated = re.sub(r"\bTIMESTAMPTZ\b", "TEXT", translated)
    translated = re.sub(r"\bJSONB\b", "TEXT", translated)
    translated = re.sub(r"\bNUMERIC\b", "REAL", translated)
    translated = translated.replace("DEFAULT gen_random_uuid()", "")
    translated = translated.replace("now()", "(datetime('now'))")
    translated = translated.replace("'{}'::jsonb", "'{}'")
    translated = translated.replace("::jsonb", "")
    for name in enums:
        translated = re.sub(
            rf"(\b[A-Za-z_][A-Za-z0-9_]*\b)\s+{name}\b",
            r"\1 TEXT",
            translated,
        )
    statements = []
    for part in translated.split(";"):
        statement = part.strip()
        if statement:
            statements.append(statement)
    return statements


def connect(db_path: str | Path = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    apply_schema(conn)
    return conn


def apply_schema(conn: sqlite3.Connection, schema_path: Path = SCHEMA_PATH) -> None:
    sql = Path(schema_path).read_text(encoding="utf-8")
    for statement in translate(sql):
        try:
            conn.execute(statement)
        except sqlite3.Error as exc:
            raise RuntimeError(f"{exc}\nSQL:\n{statement}") from exc
    conn.commit()


def _id(value: str | None) -> str:
    return str(uuid.UUID(value)) if value else str(uuid.uuid4())


def _dump(value) -> str:
    return json.dumps(value, sort_keys=True)


def create_workflow(
    conn: sqlite3.Connection,
    *,
    workspace_id: str,
    name: str,
    platform: str,
    outcome_check: dict,
    workflow_id: str | None = None,
) -> str:
    workflow_id = _id(workflow_id)
    conn.execute(
        """
        INSERT INTO workflows (workflow_id, workspace_id, name, platform, outcome_check)
        VALUES (?, ?, ?, ?, ?)
        """,
        (workflow_id, _id(workspace_id), name, platform, _dump(outcome_check)),
    )
    conn.commit()
    return workflow_id


def add_rule_version(
    conn: sqlite3.Connection,
    *,
    workspace_id: str,
    workflow_id: str,
    version_number: int,
    rules_snapshot: dict,
    effective_at: str,
    definition_ref: str | None = None,
    version_id: str | None = None,
) -> str:
    version_id = _id(version_id)
    conn.execute(
        """
        INSERT INTO rule_versions (
          version_id, workspace_id, workflow_id, version_number,
          rules_snapshot, definition_ref, effective_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            version_id,
            _id(workspace_id),
            _id(workflow_id),
            version_number,
            _dump(rules_snapshot),
            definition_ref,
            effective_at,
        ),
    )
    conn.commit()
    return version_id


def start_run(
    conn: sqlite3.Connection,
    *,
    workspace_id: str,
    version_id: str,
    execution_status: str = "running",
    business_outcome: str = "unknown",
    telemetry_health: str = "unknown",
    run_id: str | None = None,
    parent_run_id: str | None = None,
    expected_by: str | None = None,
) -> str:
    run_id = _id(run_id)
    conn.execute(
        """
        INSERT INTO runs (
          run_id, workspace_id, version_id, parent_run_id,
          execution_status, business_outcome, telemetry_health, expected_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            _id(workspace_id),
            _id(version_id),
            _id(parent_run_id) if parent_run_id else None,
            execution_status,
            business_outcome,
            telemetry_health,
            expected_by,
        ),
    )
    conn.commit()
    return run_id


def insert_event(
    conn: sqlite3.Connection,
    *,
    workspace_id: str,
    run_id: str,
    attempt_id: str,
    source: str,
    source_event_id: str,
    event_type: str,
    observed_at: str,
    data_redacted: dict | None = None,
    occurred_at: str | None = None,
    event_id: str | None = None,
) -> str:
    event_id = _id(event_id)
    conn.execute(
        """
        INSERT INTO events (
          event_id, workspace_id, run_id, attempt_id, source, source_event_id,
          occurred_at, observed_at, event_type, data_redacted
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            _id(workspace_id),
            _id(run_id),
            _id(attempt_id),
            source,
            source_event_id,
            occurred_at,
            observed_at,
            event_type,
            _dump(data_redacted or {}),
        ),
    )
    conn.commit()
    return event_id


def _parse_snapshot(raw: str | dict) -> dict:
    if isinstance(raw, dict):
        return raw
    return json.loads(raw)


def rules_for_run(conn: sqlite3.Connection, run_id: str) -> dict:
    """Return the rule version the run started with, not the newest version."""
    row = conn.execute(
        """
        SELECT rv.version_id, rv.version_number, rv.rules_snapshot, rv.definition_ref
        FROM runs AS r
        JOIN rule_versions AS rv
          ON rv.workspace_id = r.workspace_id
         AND rv.version_id = r.version_id
        WHERE r.run_id = ?
        """,
        (_id(run_id),),
    ).fetchone()
    if row is None:
        raise LookupError(f"no rule version stored for run {run_id}")
    return {
        "version_id": row["version_id"],
        "version_number": row["version_number"],
        "rules_snapshot": _parse_snapshot(row["rules_snapshot"]),
        "definition_ref": row["definition_ref"],
    }


def latest_rule_version(conn: sqlite3.Connection, workflow_id: str) -> dict:
    row = conn.execute(
        """
        SELECT version_id, version_number, rules_snapshot, definition_ref
        FROM rule_versions
        WHERE workflow_id = ?
        ORDER BY version_number DESC
        LIMIT 1
        """,
        (_id(workflow_id),),
    ).fetchone()
    if row is None:
        raise LookupError(f"no rule versions for workflow {workflow_id}")
    return {
        "version_id": row["version_id"],
        "version_number": row["version_number"],
        "rules_snapshot": _parse_snapshot(row["rules_snapshot"]),
        "definition_ref": row["definition_ref"],
    }
