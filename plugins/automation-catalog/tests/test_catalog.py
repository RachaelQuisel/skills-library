import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'automation-catalog'
SPEC = importlib.util.spec_from_file_location('catalog', SKILL / 'scripts' / 'catalog.py')
CAT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CAT)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((SKILL / 'assets' / 'example-inventory.json').read_text())
        self.w = self.data['workflows'][0]
        self.route = {'business_id': self.w['business_id'], 'workspace_id': 'workspace-one',
                      'channel_id': 'channel-one', 'posting_authorized': True,
                      'destination_verified': True, 'audience_reviewed': True,
                      'existing_messages_checked': True}

    def authorize(self):
        self.w['shareable_to_route'] = True
        self.data['routes'][self.w['business_id']] = self.route

    def plan(self):
        return CAT.prepare(self.data)[1]['items'][0]

    def prior(self):
        item = self.plan()
        self.data['previous_publications'][item['identity']] = {
            **item, 'workspace_id': 'workspace-one', 'channel_id': 'channel-one',
            'message_id': '100.001', 'receipt_verified': True}

    def test_default_does_not_publish(self):
        self.assertEqual(self.plan()['action'], 'hold')
        self.assertFalse(CAT.prepare(self.data)[1]['publication_performed'])

    def test_checked_route_allows_create_plan(self):
        self.authorize()
        self.assertEqual(self.plan()['action'], 'create')
        self.assertFalse(self.plan()['posted'])

    def test_other_business_same_channel_is_held(self):
        self.authorize()
        self.route['business_id'] = 'another-business'
        self.assertEqual(self.plan()['action'], 'hold')

    def test_unchecked_audience_is_held(self):
        self.authorize()
        self.route['audience_reviewed'] = False
        self.assertEqual(self.plan()['action'], 'hold')

    def test_unchecked_existing_messages_is_held(self):
        self.authorize()
        self.route['existing_messages_checked'] = False
        self.assertEqual(self.plan()['action'], 'hold')

    def test_rerun_skips_same_content(self):
        self.authorize()
        self.prior()
        self.assertEqual(self.plan()['action'], 'skip')

    def test_rename_edits_same_identity(self):
        self.authorize()
        self.prior()
        old = CAT.identity(self.w)
        self.w['title'] = 'Renamed reminder'
        self.assertEqual(CAT.identity(self.w), old)
        self.assertEqual(self.plan()['action'], 'edit')

    def test_timeout_requires_readback(self):
        self.authorize()
        self.prior()
        self.data['previous_publications'][CAT.identity(self.w)]['receipt_verified'] = False
        self.assertEqual(self.plan()['action'], 'hold')

    def test_changed_workspace_is_held(self):
        self.authorize()
        self.prior()
        self.route['workspace_id'] = 'workspace-two'
        self.assertEqual(self.plan()['action'], 'hold')

    def test_duplicate_identity_fails(self):
        self.data['workflows'].append(copy.deepcopy(self.w))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            CAT.prepare(self.data)

    def test_cloud_claim_needs_evidence(self):
        self.w['run'] = 'cloud-verified'
        with self.assertRaisesRegex(ValueError, 'evidence'):
            CAT.prepare(self.data)

    def test_denied_source_remains_gap(self):
        self.data['coverage'][0].update(result='denied', pagination_complete=False)
        guides, plan = CAT.prepare(self.data)
        self.assertTrue(plan['coverage_has_gaps'])
        self.assertIn('denied', next(v for k, v in guides.items() if k.endswith('index.md')))

    def test_incomplete_pagination_cannot_claim_checked(self):
        self.data['coverage'][0]['pagination_complete'] = False
        with self.assertRaisesRegex(ValueError, 'pagination'):
            CAT.prepare(self.data)

    def test_combined_private_register_requires_approval(self):
        other = copy.deepcopy(self.w)
        other['business_id'] = 'other'
        self.data['workflows'].append(other)
        coverage = copy.deepcopy(self.data['coverage'][0])
        coverage['business_id'] = 'other'
        self.data['coverage'].append(coverage)
        with self.assertRaisesRegex(ValueError, 'separately'):
            CAT.prepare(self.data)
        self.data['combined_private_register_approved'] = True
        guides, _ = CAT.prepare(self.data)
        self.assertEqual(sum(k.endswith('index.md') for k in guides), 2)

    def test_four_sections_required(self):
        self.w['sections']['Summary'] = ['An extra section.']
        with self.assertRaisesRegex(ValueError, 'four'):
            CAT.prepare(self.data)

    def test_generated_paths_ignore_title_path_traversal(self):
        self.w['title'] = '../../outside'
        guides, _ = CAT.prepare(self.data)
        self.assertTrue(all('..' not in Path(p).parts for p in guides))

    def test_cli_writes_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'output'
            cmd = [sys.executable, str(SKILL / 'scripts' / 'catalog.py'),
                   str(SKILL / 'assets' / 'example-inventory.json'), '--output', str(target)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Nothing was posted', result.stdout)
            self.assertTrue((target / 'publication-plan.json').exists())
            self.assertNotEqual(subprocess.run(cmd, capture_output=True).returncode, 0)

    def test_manifest_and_skill_paths(self):
        portable = json.loads((ROOT / 'plugin.json').read_text())
        compat = json.loads((ROOT / '.codex-plugin' / 'plugin.json').read_text())
        self.assertEqual(portable['name'], compat['name'])
        self.assertEqual(portable['version'], compat['version'])
        self.assertTrue((ROOT / compat['skills'] / 'automation-catalog' / 'SKILL.md').is_file())


if __name__ == '__main__':
    unittest.main()
