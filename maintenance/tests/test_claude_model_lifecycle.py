from pathlib import Path
import re
import unittest


SHARED = Path(__file__).resolve().parents[2] / "claude-api" / "shared"
# First-party Claude API lifecycle, verified 2026-11-24:
# https://platform.claude.com/docs/en/about-claude/model-deprecations
EXPECTED = {
    "claude-opus-4-5": ("claude-opus-4-5-20251101", "2027-01-22", "claude-opus-5-5"),
    "claude-sonnet-4-5": ("claude-sonnet-4-5-20250929", "2026-11-30", "claude-sonnet-5-5"),
}


def section(doc, heading_prefix):
    return next(
        (part for part in doc.split("\n## ") if part.startswith(heading_prefix)),
        "",
    )


def rows(doc):
    return [line.strip("|").split("|") for line in doc.splitlines() if line.startswith("|")]


def model_ids(cell):
    return re.findall(r"`(claude-[a-z0-9-]+)`", cell)


class ClaudeModelLifecycleTests(unittest.TestCase):
    def test_45_retirements_and_recommendations_agree(self):
        catalog = (SHARED / "models.md").read_text(encoding="utf-8")
        migration = (SHARED / "model-migration.md").read_text(encoding="utf-8")
        active = {
            model
            for row in rows(section(catalog, "Current Models"))
            if row[-1].strip().startswith("Active")
            for model in model_ids(row[1]) + model_ids(row[2])
        }

        for alias, (snapshot, retirement, replacement) in EXPECTED.items():
            with self.subTest(alias=alias):
                self.assertNotIn(alias, active)
                self.assertNotIn(snapshot, active)
                self.assertIn(replacement, active)

            for doc, heading in (
                (catalog, "Deprecated Models"),
                (migration, "Deprecated Models"),
                (migration, "Model-ID Rename Quick Reference"),
                (migration, "Destination Models"),
                (catalog, "Resolving User Requests"),
            ):
                with self.subTest(alias=alias, heading=heading, catalog=doc == catalog):
                    name = alias.removeprefix("claude-").replace("-4-5", " 4.5")
                    matches = [
                        row for row in rows(section(doc, heading))
                        if alias in model_ids(" ".join(row[:-1])) or name in row[0].lower()
                    ]
                    self.assertEqual(len(matches), 1, f"Missing or duplicate row for {alias}")
                    row = " | ".join(matches[0])
                    if heading == "Deprecated Models":
                        self.assertIn(snapshot, model_ids(row))
                        self.assertIn(retirement, row)
                    if heading == "Resolving User Requests":
                        self.assertIn("deprecated", row.lower())
                    self.assertEqual(
                        [model for model in model_ids(row) if model not in {alias, snapshot}],
                        [replacement],
                    )
