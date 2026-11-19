import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'skills' / 'humanize-output' / 'scripts' / 'deslop.py'


class DeSlopTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), '--data-dir', str(self.root / 'data'), *args],
            capture_output=True, text=True, timeout=10,
        )

    def write_json(self, name, value):
        p = self.root / name
        p.write_text(json.dumps(value), encoding='utf-8')
        return str(p)

    def profile(self, **changes):
        return dict(profile_id='direct', rules=['Use short sentences.'],
                    disliked_phrases=['game changer'], exceptions=['deep dive'],
                    reviewed=True, **changes)

    def test_reviewed_profile_survives_a_new_process(self):
        expected = self.profile()
        saved = self.run_cli('profile-save', '--input', self.write_json('profile.json', expected))
        self.assertEqual(saved.returncode, 0, saved.stderr)
        retrieved = self.run_cli('profile-get', '--id', 'direct')
        self.assertEqual(retrieved.returncode, 0, retrieved.stderr)
        self.assertEqual(json.loads(retrieved.stdout)['profile'], expected)

    def test_unreviewed_profile_is_not_saved(self):
        p = self.profile()
        p['reviewed'] = False
        result = self.run_cli('profile-save', '--input', self.write_json('profile.json', p))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('reviewed', result.stderr)
        self.assertFalse((self.root / 'data' / 'profiles' / 'direct.json').exists())

    def test_profile_identifier_cannot_escape_storage(self):
        p = self.profile()
        p['profile_id'] = '../outside'
        result = self.run_cli('profile-save', '--input', self.write_json('profile.json', p))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('profile_id', result.stderr)

    def test_missing_profile_is_reported_without_a_default(self):
        result = self.run_cli('profile-get', '--id', 'missing')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('missing', result.stderr)

    def test_scan_returns_exact_spans_and_personal_phrase_flags(self):
        self.run_cli('profile-save', '--input', self.write_json('profile.json', self.profile()))
        draft = self.root / 'draft.txt'
        draft.write_text("It's worth noting that Alex's 12-page outline is a game changer.", encoding='utf-8')
        result = self.run_cli('scan', '--draft', str(draft), '--profile', 'direct')
        self.assertEqual(result.returncode, 0, result.stderr)
        flags = json.loads(result.stdout)['flags']
        self.assertEqual({f['original'].lower() for f in flags}, {"it's worth noting", 'game changer'})
        for flag in flags:
            self.assertEqual(draft.read_text()[flag['start']:flag['end']], flag['original'])
            self.assertTrue(flag['explanation'])
            self.assertIn('suggestion', flag)

    def test_exception_suppresses_only_its_matching_flag(self):
        self.run_cli('profile-save', '--input', self.write_json('profile.json', self.profile()))
        draft = self.root / 'draft.txt'
        draft.write_text('A deep dive can leverage the notes.', encoding='utf-8')
        result = self.run_cli('scan', '--draft', str(draft), '--profile', 'direct')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([f['original'] for f in json.loads(result.stdout)['flags']], ['leverage'])

    def test_clear_draft_gets_no_flags_and_labeled_default(self):
        draft = self.root / 'draft.txt'
        draft.write_text('Alex will send the outline on Friday.', encoding='utf-8')
        result = self.run_cli('scan', '--draft', str(draft))
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['flags'], [])
        self.assertEqual(data['style_label'], 'default plain writing')

    def edit(self, draft, old, new, accepted=True):
        start = draft.index(old)
        return {'start': start, 'end': start + len(old), 'original': old,
                'replacement': new, 'accepted': accepted}

    def apply(self, text, edits, protected=None, output=None):
        draft = self.root / 'draft.txt'
        draft.write_text(text, encoding='utf-8')
        changes = self.write_json('edits.json', {'edits': edits, 'protected_phrases': protected or []})
        destination = output or self.root / 'revised.txt'
        result = self.run_cli('apply', '--draft', str(draft), '--edits', changes, '--output', str(destination))
        return result, destination

    def test_only_accepted_edits_are_applied_and_diff_is_returned(self):
        text = "It's worth noting that Alex will leverage 12 pages. He said, \"Keep the quote.\""
        edits = [self.edit(text, "It's worth noting that ", ''),
                 self.edit(text, 'leverage', 'use', accepted=False)]
        result, output = self.apply(text, edits, protected=['Alex'])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output.read_text(), 'Alex will leverage 12 pages. He said, "Keep the quote."')
        self.assertIn('diff', json.loads(result.stdout))
        self.assertEqual((self.root / 'draft.txt').read_text(), text)

    def test_stale_original_span_is_rejected_without_output(self):
        text = 'Use the outline.'
        edit = self.edit(text, 'Use', 'Read')
        edit['original'] = 'Old'
        result, output = self.apply(text, [edit])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('changed', result.stderr)
        self.assertFalse(output.exists())

    def test_overlapping_accepted_edits_are_rejected(self):
        text = 'Read the outline.'
        result, output = self.apply(text, [self.edit(text, 'Read the', 'Examine'), self.edit(text, 'the outline', 'the notes')])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('overlap', result.stderr)
        self.assertFalse(output.exists())

    def test_protected_name_number_and_quote_changes_are_rejected(self):
        text = 'Alex sent 12 pages and said "Ready".'
        for original, replacement, protected in [('Alex', 'Sam', ['Alex']), ('12', '13', []), ('Ready', 'Done', [])]:
            with self.subTest(original=original):
                result, output = self.apply(text, [self.edit(text, original, replacement)], protected)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('protected', result.stderr)
                self.assertFalse(output.exists())

    def test_source_and_existing_output_are_never_overwritten(self):
        text = 'Use the outline.'
        for path in [self.root / 'draft.txt', self.root / 'existing.txt']:
            with self.subTest(path=path.name):
                path.write_text(text)
                result, _ = self.apply(text, [self.edit(text, 'Use', 'Read')], output=path)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('overwrite', result.stderr)
                self.assertEqual(path.read_text(), text)


if __name__ == '__main__':
    unittest.main()
