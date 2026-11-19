import sqlite3
import uuid

import pytest
from conftest import PLUGIN, load_module

store = load_module("audit_store", PLUGIN / "scripts" / "store.py")

WORKSPACE = "6f0d1c3a-7b2e-4a51-9c8d-0e1f2a3b4c5d"
OTHER_WORKSPACE = "77777777-7777-4777-8777-777777777777"


def _workflow(conn, workspace=WORKSPACE):
    return store.create_workflow(
        conn,
        workspace_id=workspace,
        name="execute",
        platform="local_agent",
        outcome_check={"predicate": "execute pilot success"},
    )


def test_schema_creates_the_seven_tables():
    conn = store.connect()
    names = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    assert set(store.TABLES) <= names


def test_run_reads_back_the_rule_version_it_started_with():
    conn = store.connect()
    workflow_id = _workflow(conn)
    original = {
        "sha256": "aaa",
        "text": "Mark each task in order and log verification before completion.",
        "definition_ref": "execute/SKILL.md",
    }
    rewritten = {
        "sha256": "bbb",
        "text": "A later edit of the skill text.",
        "definition_ref": "execute/SKILL.md",
    }
    version_id = store.add_rule_version(
        conn,
        workspace_id=WORKSPACE,
        workflow_id=workflow_id,
        version_number=1,
        rules_snapshot=original,
        definition_ref="execute/SKILL.md",
        effective_at="2026-10-05T00:00:00Z",
    )
    run_id = store.start_run(
        conn,
        workspace_id=WORKSPACE,
        version_id=version_id,
        expected_by=None,
    )
    store.add_rule_version(
        conn,
        workspace_id=WORKSPACE,
        workflow_id=workflow_id,
        version_number=2,
        rules_snapshot=rewritten,
        definition_ref="execute/SKILL.md",
        effective_at="2026-10-06T00:00:00Z",
    )

    readback = store.rules_for_run(conn, run_id)
    latest = store.latest_rule_version(conn, workflow_id)
    assert readback["version_number"] == 1
    assert readback["rules_snapshot"] == original
    assert readback["definition_ref"] == "execute/SKILL.md"
    assert latest["version_number"] == 2
    assert latest["rules_snapshot"] == rewritten


def test_storage_rejects_duplicate_delivery_key_and_allows_another_workspace():
    conn = store.connect()
    workflow_id = _workflow(conn)
    version_id = store.add_rule_version(
        conn,
        workspace_id=WORKSPACE,
        workflow_id=workflow_id,
        version_number=1,
        rules_snapshot={"text": "v1"},
        effective_at="2026-10-05T00:00:00Z",
    )
    run_id = store.start_run(conn, workspace_id=WORKSPACE, version_id=version_id)
    attempt_id = str(uuid.uuid4())
    store.insert_event(
        conn,
        workspace_id=WORKSPACE,
        run_id=run_id,
        attempt_id=attempt_id,
        source="execute",
        source_event_id="evt-1",
        event_type="run.started",
        observed_at="2026-10-05T00:00:01Z",
        data_redacted={"plan_path": "plan.md", "plan_hash": "abc"},
    )
    with pytest.raises(sqlite3.IntegrityError):
        store.insert_event(
            conn,
            workspace_id=WORKSPACE,
            run_id=run_id,
            attempt_id=attempt_id,
            source="execute",
            source_event_id="evt-1",
            event_type="run.started",
            observed_at="2026-10-05T00:00:02Z",
            data_redacted={"plan_path": "plan.md", "plan_hash": "different"},
        )

    other_workflow = _workflow(conn, OTHER_WORKSPACE)
    other_version = store.add_rule_version(
        conn,
        workspace_id=OTHER_WORKSPACE,
        workflow_id=other_workflow,
        version_number=1,
        rules_snapshot={"text": "other"},
        effective_at="2026-10-05T00:00:00Z",
    )
    other_run = store.start_run(
        conn, workspace_id=OTHER_WORKSPACE, version_id=other_version
    )
    store.insert_event(
        conn,
        workspace_id=OTHER_WORKSPACE,
        run_id=other_run,
        attempt_id=attempt_id,
        source="execute",
        source_event_id="evt-1",
        event_type="run.started",
        observed_at="2026-10-05T00:00:03Z",
        data_redacted={"plan_path": "plan.md", "plan_hash": "other-workspace"},
    )
    count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    assert count == 2
