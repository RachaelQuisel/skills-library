#!/usr/bin/env python3
"""Reproducible check for the gem-miner local-date filter.

An 8:30pm America/Los_Angeles message is already the next UTC date
(after 5pm PT, or 4pm PT in winter). Matching the UTC timestamp prefix
drops it. The inverse also matters: 8:30pm the previous evening shares
today's UTC date and used to be kept.
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract_todays_messages as ext


def _line(timestamp, text, type_="user"):
    return json.dumps({
        "type": type_,
        "timestamp": timestamp,
        "message": {"content": text},
    })


class ExtractTodaysMessagesTest(unittest.TestCase):
    def setUp(self):
        self._saved_tz = os.environ.get(ext.TIMEZONE_ENV)
        os.environ.pop(ext.TIMEZONE_ENV, None)

    def tearDown(self):
        if self._saved_tz is None:
            os.environ.pop(ext.TIMEZONE_ENV, None)
        else:
            os.environ[ext.TIMEZONE_ENV] = self._saved_tz

    def _write_fixture(self, root: Path):
        home = root / "-Users-rachaelquisel"
        project = root / "-Users-rachaelquisel-clients-acme"
        home.mkdir()
        project.mkdir()
        # 8:30pm PDT on 2026-10-06 is 03:30 UTC on 2026-10-07.
        # 8:30pm PDT on 2026-10-05 is 03:30 UTC on 2026-10-06 (old filter kept this).
        (home / "session.jsonl").write_text("\n".join([
            _line("2026-10-07T03:30:00.000Z", "evening gem from the home folder"),
            _line("2026-10-06T17:00:00.000Z", "morning gem from the home folder"),
            _line("2026-10-06T03:30:00.000Z", "yesterday evening should be dropped"),
            _line("2026-01-16T00:30:00.000Z", "winter evening after 4pm PT"),
        ]) + "\n")
        (home / "agent-skip.jsonl").write_text(
            _line("2026-10-06T17:00:00.000Z", "agent transcript should be skipped") + "\n"
        )
        (project / "session.jsonl").write_text(
            _line("2026-10-06T18:00:00.000Z", "gem from a project folder session") + "\n"
        )

    def test_evening_pacific_messages_stay_on_the_local_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write_fixture(Path(tmp))
            msgs = ext.extract_messages("2026-10-06", projects_dir=tmp)
            texts = [m["text"] for m in msgs]
            self.assertIn("evening gem from the home folder", texts)
            self.assertIn("morning gem from the home folder", texts)
            self.assertIn("gem from a project folder session", texts)
            self.assertNotIn("yesterday evening should be dropped", texts)
            self.assertNotIn("agent transcript should be skipped", texts)
            self.assertNotIn("winter evening after 4pm PT", texts)

    def test_winter_evening_after_4pm_pt_counts_as_that_local_day(self):
        # 4:30pm PST on 2026-01-15 is 00:30 UTC on 2026-01-16.
        with tempfile.TemporaryDirectory() as tmp:
            self._write_fixture(Path(tmp))
            msgs = ext.extract_messages("2026-01-15", projects_dir=tmp)
            texts = [m["text"] for m in msgs]
            self.assertEqual(texts, ["winter evening after 4pm PT"])

    def test_default_today_uses_pacific_even_if_the_clock_is_utc(self):
        # 03:30 UTC on Oct 7 is still Oct 6 in Los Angeles. A UTC "today"
        # would ask for Oct 7 and miss the evening message.
        with tempfile.TemporaryDirectory() as tmp:
            self._write_fixture(Path(tmp))
            now = datetime(2026, 10, 7, 3, 30, tzinfo=timezone.utc)
            msgs = ext.extract_messages(projects_dir=tmp, now=now)
            texts = [m["text"] for m in msgs]
            self.assertIn("evening gem from the home folder", texts)
            self.assertNotIn("yesterday evening should be dropped", texts)
            self.assertEqual(
                ext.resolve_date(None, ext.get_timezone(), now=now),
                "2026-10-06",
            )

    def test_timezone_override(self):
        os.environ[ext.TIMEZONE_ENV] = "UTC"
        with tempfile.TemporaryDirectory() as tmp:
            self._write_fixture(Path(tmp))
            msgs = ext.extract_messages("2026-10-07", projects_dir=tmp)
            texts = [m["text"] for m in msgs]
            self.assertEqual(texts, ["evening gem from the home folder"])
            self.assertEqual(ext.get_timezone().key, "UTC")


if __name__ == "__main__":
    unittest.main()
