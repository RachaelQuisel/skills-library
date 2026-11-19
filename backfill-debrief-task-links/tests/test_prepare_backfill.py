import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "prepare_backfill.py"


if SCRIPT_PATH.exists():
    SPEC = importlib.util.spec_from_file_location("prepare_backfill", SCRIPT_PATH)
    prepare_backfill = importlib.util.module_from_spec(SPEC)
    sys.modules[SPEC.name] = prepare_backfill
    SPEC.loader.exec_module(prepare_backfill)
else:
    prepare_backfill = None


CLIENT_ID = "recAAAAAAAAAAAAAA"
TASK_ID = "recBBBBBBBBBBBBBB"
MEETING_ID = "recCCCCCCCCCCCCCC"


def manifest_for(*, target_ids=None, meeting_client_ids=None):
    return {
        "clientRecordId": CLIENT_ID,
        "tasks": [
            {
                "taskRecordId": TASK_ID,
                "sourceMeetingIds": [MEETING_ID],
                "targetMeetingIds": target_ids or [],
                "meetings": [
                    {
                        "recordId": MEETING_ID,
                        "clientRecordIds": (
                            [CLIENT_ID]
                            if meeting_client_ids is None
                            else meeting_client_ids
                        ),
                    }
                ],
            }
        ],
    }


@unittest.skipIf(prepare_backfill is None, "helper script does not exist")
class BuildPlanTests(unittest.TestCase):
    def test_builds_one_record_update_for_eligible_task(self):
        plan = prepare_backfill.build_plan(manifest_for())

        self.assertEqual(plan["eligibleCount"], 1)
        self.assertEqual(plan["excluded"], [])
        self.assertEqual(
            plan["updates"],
            [
                {
                    "baseId": prepare_backfill.BASE_ID,
                    "tableId": prepare_backfill.TASKS_TABLE_ID,
                    "records": [
                        {
                            "id": TASK_ID,
                            "fields": {
                                prepare_backfill.TARGET_FIELD_ID: [MEETING_ID]
                            },
                        }
                    ],
                    "fieldIds": [
                        prepare_backfill.SOURCE_FIELD_ID,
                        prepare_backfill.TARGET_FIELD_ID,
                    ],
                }
            ],
        )

    def test_excludes_task_when_target_is_already_populated(self):
        plan = prepare_backfill.build_plan(
            manifest_for(target_ids=[MEETING_ID])
        )

        self.assertEqual(plan["eligibleCount"], 0)
        self.assertEqual(plan["updates"], [])
        self.assertEqual(plan["excluded"][0]["reason"], "target-not-empty")

    def test_excludes_task_when_meeting_client_is_ambiguous(self):
        plan = prepare_backfill.build_plan(
            manifest_for(meeting_client_ids=[CLIENT_ID, "recDDDDDDDDDDDDDD"])
        )

        self.assertEqual(plan["eligibleCount"], 0)
        self.assertEqual(plan["excluded"][0]["reason"], "ambiguous-client-scope")

    def test_excludes_task_when_meeting_has_no_client_stamp(self):
        plan = prepare_backfill.build_plan(manifest_for(meeting_client_ids=[]))

        self.assertEqual(plan["eligibleCount"], 0)
        self.assertEqual(plan["excluded"][0]["reason"], "ambiguous-client-scope")

    def test_excludes_task_when_meeting_belongs_to_another_client(self):
        plan = prepare_backfill.build_plan(
            manifest_for(meeting_client_ids=["recDDDDDDDDDDDDDD"])
        )

        self.assertEqual(plan["eligibleCount"], 0)
        self.assertEqual(plan["excluded"][0]["reason"], "out-of-scope-client")

    def test_rejects_manifest_when_meeting_evidence_is_missing(self):
        manifest = manifest_for()
        manifest["tasks"][0]["meetings"] = []

        with self.assertRaisesRegex(ValueError, "meeting evidence does not match"):
            prepare_backfill.build_plan(manifest)

    def test_rejects_duplicate_task_ids(self):
        manifest = manifest_for()
        manifest["tasks"].append(dict(manifest["tasks"][0]))

        with self.assertRaisesRegex(ValueError, "duplicate taskRecordId"):
            prepare_backfill.build_plan(manifest)

    def test_rejects_invalid_airtable_ids(self):
        manifest = manifest_for()
        manifest["clientRecordId"] = "not-a-record-id"

        with self.assertRaisesRegex(ValueError, "clientRecordId"):
            prepare_backfill.build_plan(manifest)


class ScriptExistsTests(unittest.TestCase):
    def test_prepare_backfill_script_exists(self):
        self.assertTrue(SCRIPT_PATH.exists(), "prepare_backfill.py is missing")


if __name__ == "__main__":
    unittest.main()
