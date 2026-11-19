"""Offline checks for the inventory helper; use synthetic records only."""
import csv
from datetime import date
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('inventory', Path(__file__).with_name('inspect_exports.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def source(self, name='source.csv', **overrides):
        row = {'Binti application id': 'case-1', 'CBOs': 'Guardians Of Love, FFA',
               'Status': 'Applying', 'Application template': 'LA County RFA Application',
               'Applicant name': 'Example Applicant', 'Co-applicant name': '',
               'Date of inquiry': '2026-09-01', 'Number of applicants': '1'}
        row.update(overrides)
        path = self.root / name
        with path.open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(row))
            writer.writeheader()
            writer.writerow(row)
        return path

    def test_four_groups_keep_missing_renewals_pending(self):
        gol = self.source()
        diup = self.source('diup.csv', **{'CBOs': 'Dangerfield Institute', 'Binti application id': 'case-2'})
        renewal = self.source('renewal.csv', **{'CBOs': 'Dangerfield Institute', 'Status': 'In Renewal',
                                             'Application template': 'RFA Renewal', 'Binti application id': 'case-3',
                                             'Date of inquiry': '2020-01-01'})
        result = m.build_inventory([gol, diup, renewal], None, date(2026, 9, 30), 30, list(m.GROUPS))
        self.assertEqual(result['group_status']['gol-renewals'], 'pending')
        self.assertEqual(result['group_status']['diup-renewals'], 'received')
        self.assertIsNone(result['binti_files'][2]['groups']['diup-renewals']['recent_inquiry_occurrences'])
        self.assertFalse(result['writes_authorized'])

    def test_recent_window_and_bom(self):
        path = self.source(**{'Co-applicant name': 'Example Coapplicant', 'Number of applicants': '2'})
        result = m.inspect_binti(path, date(2026, 9, 30), 30)
        self.assertEqual(result['applicant_occurrences'], 2)
        self.assertEqual(result['groups']['gol-applications']['recent_inquiry_occurrences'], 2)
        outside = self.source('outside.csv', **{'Date of inquiry': '2026-08-31'})
        self.assertEqual(m.inspect_binti(outside, date(2026, 9, 30), 30)['groups']['gol-applications']['recent_inquiry_occurrences'], 0)

    def test_unknown_date_is_not_classified_as_old(self):
        result = m.inspect_binti(self.source(**{'Date of inquiry': 'unknown'}), date(2026, 9, 30), 30)
        self.assertEqual(result['groups']['gol-applications']['inquiry_date_unknown_occurrences'], 1)

    def test_status_template_conflict_does_not_assign_group(self):
        result = m.inspect_binti(self.source(**{'Status': 'In Renewal'}), date(2026, 9, 30), 30)
        self.assertEqual(result['groups'], {})
        self.assertTrue(result['warnings'])

    def test_mixed_organizations_do_not_double_total(self):
        source = self.source(**{'CBOs': 'Guardians Of Love, FFA, Dangerfield Institute'})
        result = m.inspect_binti(source, date(2026, 9, 30), 30)
        self.assertEqual(result['applicant_occurrences'], 1)
        self.assertEqual(len(result['groups']), 2)

    def test_identical_export_is_counted_once(self):
        source = self.source()
        copy = self.root / 'same-export.csv'
        copy.write_bytes(source.read_bytes())
        result = m.build_inventory([source, copy, source], None, date(2026, 9, 30), 30, ['gol-applications'])
        self.assertEqual(len(result['binti_files']), 1)
        self.assertEqual(len(result['errors']), 2)
        self.assertEqual(result['group_status']['diup-applications'], 'out of scope')

    def test_phone_decoding_shared_counts_and_blanks(self):
        path = self.root / 'clients.csv'
        with path.open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['First Name', 'Last Name', 'Email', 'Phone'])
            writer.writerow(['Example', 'One', '', '&#039;202-555-0100'])
            writer.writerow(['Example', 'Two', 'two@example.invalid', '+1 (202) 555-0100'])
            writer.writerow(['Example', 'Three', '', ''])
        result = m.inspect_acuity(path)
        self.assertEqual(result['client_records'], 3)
        self.assertEqual(result['phone_numbers_used_by_multiple_clients'], 1)
        self.assertEqual(result['client_records_sharing_phone_numbers'], 2)
        self.assertEqual(result['garbled_apostrophe_phone_records'], 1)
        self.assertEqual(result['blank_email_records'], 2)
        self.assertEqual(result['blank_phone_records'], 1)
        self.assertFalse(result['account_verified'])
        self.assertEqual(m.canonical_phone('202-555-0100 ext 2'), '')

    def test_airtable_csv_is_not_mislabeled_binti(self):
        path = self.root / 'wrong.csv'
        path.write_text('Name,Active\nExample,1\n')
        result = m.build_inventory([path], None, date(2026, 9, 30), 30, ['gol-applications'])
        self.assertTrue(result['errors'])
        self.assertEqual(result['group_status']['gol-applications'], 'pending')

    def test_duplicate_headers_and_malformed_rows_are_rejected(self):
        for content in ['First Name,Last Name,Email,Phone,Email\na,b,c,d,e\n',
                        'First Name,Last Name,Email,Phone\na,b,c,d,extra\n']:
            path = self.root / 'malformed.csv'
            path.write_text(content)
            with self.assertRaises(ValueError):
                m.inspect_acuity(path)


if __name__ == '__main__':
    unittest.main()
