import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.parse
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills' / 'cited-research-assistant' / 'scripts' / 'research.py'
LAUNCHER = ROOT / 'scripts' / 'research.py'
spec = importlib.util.spec_from_file_location('research', SCRIPT)
research = importlib.util.module_from_spec(spec)
spec.loader.exec_module(research)


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.assertEqual(
            Path(research.__file__).resolve(),
            ROOT / 'skills' / 'cited-research-assistant' / 'scripts' / 'research.py')

    def test_arxiv_preserves_version_dates_and_access_scope(self):
        feed = '''<feed xmlns="http://www.w3.org/2005/Atom"><entry>
        <id>http://arxiv.org/abs/1706.03762v7</id><title>Attention Is All You Need</title>
        <published>2017-06-12T00:00:00Z</published><updated>2023-08-02T00:00:00Z</updated>
        <author><name>Ashish Vaswani</name></author><summary>The model uses attention.</summary>
        </entry></feed>'''
        with patch.object(research, 'request', return_value=feed):
            result = research.search_arxiv('attention', '2017-01-01', '2017-12-31')
        source = result['sources'][0]
        self.assertEqual(source['identifier'], '1706.03762v7')
        self.assertEqual(source['submitted_date'], '2017-06-12T00:00:00Z')
        self.assertEqual(source['updated_date'], '2023-08-02T00:00:00Z')
        self.assertIsNone(source['publication_date'])
        self.assertEqual(source['scope'], 'abstract')
        self.assertEqual(source['publication_status'], 'preprint')
        self.assertEqual(source['content'], 'The model uses attention.')

    def arxiv_query(self, query, start=None, end=None):
        seen = {}
        def capture(url, headers=None):
            seen['url'] = url
            return '<feed xmlns="http://www.w3.org/2005/Atom"></feed>'
        with patch.object(research, 'request', side_effect=capture):
            result = research.search_arxiv(query, start, end)
        self.assertEqual(result['sources'], [])
        self.assertIsNone(result['unavailable'])
        parsed = urllib.parse.parse_qs(urllib.parse.urlsplit(seen['url']).query)
        return parsed['search_query'][0]

    def test_multiword_date_query_groups_every_word_before_the_date_filter(self):
        self.assertEqual(
            self.arxiv_query('graph neural network', '2024-01-01', '2025-12-31'),
            'all:(graph AND neural AND network) AND submittedDate:[202401010000 TO 202512312359]')

    def test_multiword_query_without_a_date_is_still_a_conjunction(self):
        self.assertEqual(self.arxiv_query('graph neural network'), 'all:(graph AND neural AND network)')

    def test_single_word_date_query_stays_one_field_term(self):
        self.assertEqual(
            self.arxiv_query('attention', '2017-01-01', '2017-12-31'),
            'all:attention AND submittedDate:[201701010000 TO 201712312359]')

    def test_semantic_scholar_absent_abstract_is_metadata_only(self):
        response = {'data':[{'paperId':'abc', 'title':'A paper', 'url':'https://www.semanticscholar.org/paper/abc',
                             'abstract':None, 'authors':[], 'externalIds':{'ArXiv':'1706.03762'}, 'publicationDate':None}]}
        with patch.object(research, 'request', return_value=json.dumps(response)):
            source = research.search_scholar('attention')['sources'][0]
        self.assertEqual(source['scope'], 'metadata')
        self.assertEqual(source['content'], 'A paper')
        self.assertIsNone(source['publication_date'])
        self.assertEqual(source['publication_status'], 'unknown')

    def test_unavailable_source_never_becomes_empty_success(self):
        with patch.object(research, 'request', side_effect=OSError('HTTP 429')):
            result = research.search_scholar('attention')
        self.assertEqual(result['sources'], [])
        self.assertIn('429', result['unavailable'])
        self.assertIn('WebSearch', result['fallback'])

    def test_date_filter_rejects_unknown_publication_date(self):
        response = {'data':[{'paperId':'abc','title':'A paper','abstract':None,'externalIds':{}}]}
        with patch.object(research, 'request', return_value=json.dumps(response)):
            result = research.search_scholar('attention', '2017-01-01', '2017-12-31')
        self.assertEqual(result['sources'], [])
        self.assertEqual(result['unknown_date_count'], 1)

    def test_duplicates_identify_same_work_without_losing_versions(self):
        sources = [{'source_id':'a', 'external_ids':{'arxiv':'1706.03762v1'}},
                   {'source_id':'b', 'external_ids':{'arxiv':'1706.03762v7'}},
                   {'source_id':'c', 'external_ids':{'arxiv':'2001.00001v1'}}]
        self.assertEqual(research.duplicate_groups(sources), [['a','b']])
        self.assertEqual(sources[1]['external_ids']['arxiv'], '1706.03762v7')

    def test_cross_provider_identifier_capitalization_does_not_hide_duplicates(self):
        sources = [{'source_id':'a', 'external_ids':{'arxiv':'1706.03762v1'}},
                   {'source_id':'b', 'external_ids':{'ArXiv':'1706.03762v7'}}]
        self.assertEqual(research.duplicate_groups(sources), [['a','b']])


class ClaimTests(unittest.TestCase):
    def records(self):
        return {'sources':[{'source_id':'s1', 'identifier':'fixture-v1', 'title':'Fictional study',
                            'url':'https://example.org/study', 'scope':'abstract',
                            'content':'The fixture sample contained 12 participants.',
                            'publication_status':'preprint','retrieved_at':'2026-10-03T00:00:00Z'}],
                'claims':[{'claim_id':'c1', 'text':'The fixture sample contained 12 participants.',
                           'status':'supported', 'kind':'substantive', 'inference':False,
                           'support_review':'The abstract explicitly states this sample size.',
                           'evidence':[{'source_id':'s1','passage':'sample contained 12 participants',
                                        'relationship':'supports'}]}]}

    def test_cited_output_exposes_scope_preprint_and_supporting_passage(self):
        output = research.render(self.records())
        self.assertIn('[s1:', output)
        self.assertIn('https://example.org/study', output)
        self.assertIn('abstract', output)
        self.assertIn('preprint', output)
        self.assertIn('sample contained 12 participants', output)

    def test_fabricated_reference_cannot_become_supported(self):
        records = self.records()
        records['claims'][0]['evidence'][0]['source_id'] = 'nonexistent'
        with self.assertRaisesRegex(ValueError, 'source'):
            research.render(records)

    def test_real_reference_with_absent_passage_is_rejected(self):
        records = self.records()
        records['claims'][0]['evidence'][0]['passage'] = 'The model cures cancer.'
        with self.assertRaisesRegex(ValueError, 'passage'):
            research.render(records)

    def test_metadata_cannot_support_a_substantive_claim(self):
        records = self.records()
        records['sources'][0]['scope'] = 'metadata'
        with self.assertRaisesRegex(ValueError, 'metadata'):
            research.render(records)

    def test_absent_abstract_detail_and_missing_paper_are_declined(self):
        records = self.records()
        records['claims'] = [{'claim_id':'c2','text':'The fixture used randomized allocation.',
                              'status':'unverifiable','reason':'The abstract does not report allocation.', 'evidence':[]},
                             {'claim_id':'c3','text':'A nonexistent paper confirms the finding.',
                              'status':'unverifiable','reason':'No matching paper was retrieved.', 'evidence':[]}]
        output = research.render(records)
        self.assertEqual(output.count("I can't verify this"), 2)
        self.assertNotIn('## Verified claims\n- ', output)

    def test_gap_explanation_has_its_own_source_citation(self):
        records = self.records()
        records['claims'] = [{'claim_id':'c2','text':'The fixture randomized allocation.',
                              'status':'unverifiable','reason':'The available abstract reports the sample only.',
                              'reason_source_ids':['s1'],'evidence':[]}]
        output = research.render(records)
        gap_line = next(line for line in output.splitlines() if "I can't verify this" in line)
        self.assertIn('[s1:', gap_line)
        records['claims'][0]['reason_source_ids'] = ['nonexistent']
        with self.assertRaisesRegex(ValueError, 'source'):
            research.render(records)

    def test_inference_is_explicit_and_disagreement_cannot_be_hidden(self):
        records = self.records()
        records['claims'][0]['inference'] = True
        self.assertIn('Inference:', research.render(records))
        contrary = dict(records['sources'][0], source_id='s2', title='Fictional conflicting study',
                        identifier='conflicting-fixture-v1', url='https://example.org/other-study',
                        content='The fixture sample contained 14 participants.')
        records['sources'].append(contrary)
        records['claims'][0]['evidence'].append({'source_id':'s2','passage':'14 participants','relationship':'contradicts'})
        with self.assertRaisesRegex(ValueError, 'disagreement'):
            research.render(records)
        records['claims'][0]['status'] = 'unverifiable'
        records['claims'][0]['reason'] = 'Retrieved sources disagree.'
        output = research.render(records)
        self.assertIn('contradicts', output)
        self.assertIn("I can't verify this", output)

    def test_final_hook_detects_actual_uncited_addition_then_accepts_exact_reply(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            research.begin(data, 'session-test')
            expected = research.prepare(data, 'session-test', self.records())
            result = research.final_check(data, {'session_id':'session-test','last_assistant_message':expected+'\nThe model is always accurate.'})
            self.assertEqual(result['decision'], 'block')
            result = research.final_check(data, {'session_id':'session-test','stop_hook_active':True,'last_assistant_message':expected})
            self.assertEqual(result, {})
            audits = [json.loads(s) for s in (data/'audits/session-test.jsonl').read_text().splitlines()]
            self.assertEqual([a['coverage_pass'] for a in audits], [False,True])
            self.assertEqual(research.final_check(data, {'session_id':'session-test','last_assistant_message':'An unrelated later reply.'}), {})

    def test_repeated_bad_response_stops_with_failure_without_claiming_success(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            research.begin(data, 'session-test')
            result = research.final_check(data, {'session_id':'session-test','stop_hook_active':True,'last_assistant_message':'Uncited.'})
            self.assertFalse(result['continue'])
            self.assertIn('failed', result['stopReason'])
            self.assertFalse(json.loads((data/'sessions/session-test.json').read_text())['completed'])


class StandaloneSkillTests(unittest.TestCase):
    def records(self):
        return ClaimTests().records()

    def hook_command(self):
        front = (ROOT / 'skills' / 'cited-research-assistant' / 'SKILL.md').read_text().split('---', 2)[1]
        match = re.search(r"^          command: '(.*)'$", front, re.M)
        self.assertIsNotNone(match)
        return match.group(1)

    def run_checked(self, script, env, directory):
        root = Path(directory)
        root.mkdir(parents=True, exist_ok=True)
        records = root / 'records.json'
        records.write_text(json.dumps(self.records()))
        output = root / 'brief.md'
        begin = subprocess.run([sys.executable, str(script), 'begin', '--session-id', 'session-test'],
                               env=env, capture_output=True, text=True)
        self.assertEqual(begin.returncode, 0, begin.stderr)
        prepared = subprocess.run([sys.executable, str(script), 'prepare', '--session-id', 'session-test',
                                   '--input', str(records), '--output', str(output)],
                                  env=env, capture_output=True, text=True)
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        payload = json.dumps({'session_id':'session-test', 'last_assistant_message':output.read_text().strip()})
        return payload, output.read_text()

    def test_launcher_is_not_a_second_copy_of_the_helper(self):
        text = LAUNCHER.read_text()
        self.assertNotIn('def search_arxiv', text)
        self.assertIn("'skills'", text)
        self.assertIn("'cited-research-assistant'", text)
        self.assertIn("'research.py'", text)
        self.assertIn('def search_arxiv', SCRIPT.read_text())

    def test_plugin_root_launcher_matches_the_skill_script(self):
        with tempfile.TemporaryDirectory() as directory:
            env = os.environ.copy()
            env['HOME'] = directory
            env.pop('CLAUDE_PLUGIN_ROOT', None)
            env.pop('CLAUDE_SKILL_DIR', None)
            via_launcher, brief = self.run_checked(LAUNCHER, env, directory)
            direct = subprocess.run([sys.executable, str(SCRIPT), 'final-check'],
                                    input=via_launcher, env=env, capture_output=True, text=True)
            # The launcher already stored the brief; a second begin would reset it.
            # Compare a fresh direct prepare against the launcher brief instead.
            other = Path(directory) / 'direct'
            other.mkdir()
            env['HOME'] = str(other)
            _, direct_brief = self.run_checked(SCRIPT, env, other)
        self.assertEqual(brief, direct_brief)
        self.assertEqual(direct.returncode, 0, direct.stderr)
        self.assertEqual(direct.stdout.strip(), '{}')

    def test_stop_hook_prefers_the_plugin_and_also_runs_a_copied_skill(self):
        command = self.hook_command()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / 'home'
            env = os.environ.copy()
            env['HOME'] = str(home)
            env['CLAUDE_PLUGIN_ROOT'] = str(ROOT)
            env.pop('CLAUDE_SKILL_DIR', None)
            env.pop('CLAUDE_PROJECT_DIR', None)
            poison = home / '.claude' / 'skills' / 'cited-research-assistant' / 'scripts'
            poison.mkdir(parents=True)
            (poison / 'research.py').write_text('import sys\nsys.stderr.write("poison\\n")\nraise SystemExit(9)\n')
            payload, _ = self.run_checked(LAUNCHER, env, root / 'plugin-run')
            hook = subprocess.run(['sh', '-c', command], input=payload, env=env, capture_output=True, text=True)
            self.assertEqual(hook.returncode, 0, hook.stderr)
            self.assertEqual(hook.stdout.strip(), '{}')
            self.assertNotIn('poison', hook.stderr)

            standalone_home = root / 'standalone-home'
            copied = standalone_home / '.claude' / 'skills' / 'cited-research-assistant'
            shutil.copytree(ROOT / 'skills' / 'cited-research-assistant', copied)
            self.assertFalse((standalone_home / 'scripts' / 'research.py').exists())
            env = os.environ.copy()
            env['HOME'] = str(standalone_home)
            env.pop('CLAUDE_PLUGIN_ROOT', None)
            env.pop('CLAUDE_SKILL_DIR', None)
            env.pop('CLAUDE_PROJECT_DIR', None)
            payload, _ = self.run_checked(copied / 'scripts' / 'research.py', env, root / 'standalone-run')
            hook = subprocess.run(['sh', '-c', command], input=payload, env=env, capture_output=True, text=True)
            self.assertEqual(hook.returncode, 0, hook.stderr)
            self.assertEqual(hook.stdout.strip(), '{}')


if __name__ == '__main__':
    unittest.main()
