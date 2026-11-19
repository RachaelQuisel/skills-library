import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/contact-follow-up-tracker/scripts/memory.py'
spec = importlib.util.spec_from_file_location('relationship_memory', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
NOW = '2026-10-04T01:30:00Z'

class LogTests(unittest.TestCase):
    def setUp(self):
        self.log = m.initial('fictional-log', NOW)
        self.snapshots = [self.log]

    def change(self, request, log=None):
        base=log or self.log
        result = m.mutate(base, request, base['snapshot_id'], NOW)
        self.snapshots.append(result)
        return result

    def test_same_name_requires_identity(self):
        self.log=self.change({'op':'contact','contact_id':'a','name':'Alex Fixture','identifying_details':'fictional designer'})
        self.log=self.change({'op':'contact','contact_id':'b','name':'Alex Fixture','identifying_details':'fictional founder'})
        with self.assertRaisesRegex(ValueError,'Ambiguous'):
            m.contact(self.log,'Alex Fixture')
        self.assertEqual(m.contact(self.log,'b')['identifying_details'],'fictional founder')

    def test_encounter_persists_raw_notes_and_unset_date(self):
        self.log=self.change({'op':'contact','contact_id':'a','name':'Alex Fixture','identifying_details':'fictional designer'})
        self.log=self.change({'op':'encounter','encounter_id':'e','contact_id':'a','meeting_date':None,'source_notes':'We might exchange ideas sometime.'})
        self.assertEqual(self.log['encounters'][0]['source_notes'],'We might exchange ideas sometime.')
        self.assertEqual(self.log['commitments'],[])
        self.assertIsNone(self.log['encounters'][0]['meeting_date'])
        self.assertEqual(m.resolve(self.snapshots,'fictional-log'),self.log)

    def test_unconfirmed_extraction_cannot_be_saved(self):
        self.log=self.change({'op':'contact','contact_id':'a','name':'Alex Fixture','identifying_details':'fictional designer'})
        req={'op':'commitment','commitment_id':'p','contact_id':'a','who_owes':'me','action':'send outline','source_ref':'e','deadline':None,'deadline_raw':None,'follow_up_date':None,'time_zone':'America/Los_Angeles'}
        with self.assertRaisesRegex(ValueError,'confirmation'):
            self.change(req)
        req['confirmation']={'kind':'explicit_instruction','user_wording':'Record that I promised Alex the outline; no date was agreed.'}
        self.log=self.change(req)
        self.assertIsNone(self.log['commitments'][0]['deadline'])
        self.assertEqual(self.log['commitments'][0]['status'],'open')
        self.assertEqual(self.log['commitments'][0]['history'][0]['source_wording'],req['confirmation']['user_wording'])

    def test_stale_write_does_not_change_source(self):
        with self.assertRaisesRegex(ValueError,'Stale'):
            m.mutate(self.log,{'op':'contact'},'old-snapshot',NOW)
        self.assertEqual(self.log['contacts'],[])

    def test_resolver_uses_chain_and_rejects_forks_or_missing_parent(self):
        child=self.change({'op':'contact','contact_id':'a','name':'Alex Fixture','identifying_details':'fictional designer'})
        self.assertEqual(m.resolve([child,self.log],'fictional-log')['snapshot_id'],child['snapshot_id'])
        fork=self.change({'op':'contact','contact_id':'b','name':'Alex Fixture','identifying_details':'fictional founder'})
        with self.assertRaisesRegex(ValueError,'Conflicting'):
            m.resolve([self.log,child,fork],'fictional-log')
        with self.assertRaisesRegex(ValueError,'Missing parent'):
            m.resolve([child],'fictional-log')

    def test_malformed_current_record_cannot_fall_back_to_old(self):
        import copy
        broken=copy.deepcopy(self.log);broken['snapshot_id']='broken';broken['revision']=2;broken['parent_snapshot_id']=self.log['snapshot_id'];broken['contacts']=[{'contact_id':'a'}]
        with self.assertRaises(ValueError):m.resolve([self.log,broken],'fictional-log')
        with self.assertRaisesRegex(ValueError,'No snapshots'):m.resolve([],'fictional-log')

    def seeded(self):
        self.log=self.change({'op':'contact','contact_id':'a','name':'Alex Fixture','identifying_details':'fictional designer'})
        self.log=self.change({'op':'encounter','encounter_id':'e','contact_id':'a','meeting_date':None,'source_notes':'Vague note only.'})
        self.log=self.change({'op':'commitment','commitment_id':'p','contact_id':'a','who_owes':'me','action':'send outline','source_ref':'explicit fictional instruction','deadline':'2026-10-03','deadline_raw':'October 3, 2026','follow_up_date':None,'time_zone':'America/Los_Angeles','confirmation':{'kind':'explicit_instruction','user_wording':'Record my outline promise for October 3, 2026.'}})
        return self.log

    def test_query_retains_sources_directions_and_local_date(self):
        self.seeded()
        self.log=self.change({'op':'commitment','commitment_id':'owed','contact_id':'a','who_owes':'contact','action':'send me feedback','source_ref':'fictional encounter','deadline':None,'deadline_raw':None,'follow_up_date':None,'time_zone':'America/Los_Angeles','confirmation':{'kind':'user_confirmation','user_wording':'Yes, Alex promised feedback with no date.'}})
        own=m.query(self.log,NOW)
        self.assertEqual([c['commitment_id'] for c in own['commitments']],['p'])
        self.assertEqual(own['commitments'][0]['current_date'],'2026-10-03')
        self.assertEqual(own['commitments'][0]['due_state'],'today')
        brief=m.query(self.log,NOW,'a')
        self.assertEqual(len(brief['commitments']),2)
        self.assertEqual(brief['encounters'][0]['source_notes'],'Vague note only.')
        self.assertEqual(brief['commitments'][0]['source_ref'],'explicit fictional instruction')

    def test_reschedule_and_status_changes_preserve_prior_history(self):
        self.seeded()
        self.log=self.change({'op':'update','commitment_id':'p','changes':{'deadline':'2026-10-07','deadline_raw':'October 7, 2026','follow_up_date':'2026-10-05'},'confirmation':{'kind':'explicit_instruction','user_wording':'Move the outline deadline to October 7 and follow up October 5.'}})
        c=self.log['commitments'][0]
        self.assertEqual(c['history'][-1]['before']['deadline'],'2026-10-03')
        self.assertEqual(c['history'][-1]['after']['deadline'],'2026-10-07')
        self.assertEqual(c['history'][0]['source_wording'],'Record my outline promise for October 3, 2026.')
        self.log=self.change({'op':'update','commitment_id':'p','changes':{'status':'completed'},'confirmation':{'kind':'explicit_instruction','user_wording':'Mark the outline completed; I say I sent it.'}})
        self.assertEqual(m.query(self.log,NOW,'a')['commitments'][0]['completion_basis'],'user_reported')
        self.log=self.change({'op':'update','commitment_id':'p','changes':{'status':'cancelled'},'confirmation':{'kind':'user_confirmation','user_wording':'Correct that entry to cancelled.'}})
        self.assertEqual(self.log['commitments'][0]['history'][-1]['before']['status'],'completed')
        self.assertEqual(self.log['commitments'][0]['status'],'cancelled')

    def test_updates_require_confirmation_and_new_deadline_wording(self):
        self.seeded()
        req={'op':'update','commitment_id':'p','changes':{'deadline':'2026-10-07'}}
        with self.assertRaisesRegex(ValueError,'confirmation'):self.change(req)
        req['confirmation']={'kind':'explicit_instruction','user_wording':'Move it to October 7, 2026.'}
        with self.assertRaisesRegex(ValueError,'deadline_raw'):self.change(req)
        req['changes']['deadline_raw']='October 7, 2026';req['changes']['deadline']='10/07/26'
        with self.assertRaisesRegex(ValueError,'date'):self.change(req)

    def enable(self):
        self.log=self.change({'op':'reminders','enabled':True,'cadence':'daily at 09:00','lead_days':3,'time_zone':'America/Los_Angeles','confirmation':{'kind':'explicit_instruction','user_wording':'Enable fictional daily reminders at 9am Los Angeles with three days lead time.'}})

    def test_reminders_require_explicit_enable_and_valid_settings(self):
        self.seeded()
        self.assertEqual(m.scan(self.log,NOW)['status'],'disabled')
        with self.assertRaisesRegex(ValueError,'confirmation'):
            self.change({'op':'reminders','enabled':True,'cadence':'daily','lead_days':3,'time_zone':'America/Los_Angeles'})
        self.enable()
        self.assertEqual(self.log['reminders']['time_zone'],'America/Los_Angeles')
        bad={'op':'reminders','enabled':True,'cadence':'','lead_days':3,'time_zone':'UTC','confirmation':{'kind':'explicit_instruction','user_wording':'Enable it.'}}
        with self.assertRaisesRegex(ValueError,'cadence'):self.change(bad)
        bad['cadence']='daily';bad['lead_days']=True
        with self.assertRaisesRegex(ValueError,'lead_days'):self.change(bad)

    def test_scan_uses_local_date_and_latest_reschedule_or_closure(self):
        self.seeded();self.enable()
        item=m.scan(self.log,NOW)['items'][0]
        self.assertEqual(item['due_state'],'today')
        self.assertEqual(item['current_date'],'2026-10-03')
        self.assertEqual(item['source_ref'],'explicit fictional instruction')
        self.log=self.change({'op':'update','commitment_id':'p','changes':{'deadline':'2026-10-07','deadline_raw':'October 7, 2026'},'confirmation':{'kind':'explicit_instruction','user_wording':'Move the promise to October 7, 2026.'}})
        self.assertEqual(m.scan(self.log,NOW)['items'],[])
        self.log=self.change({'op':'update','commitment_id':'p','changes':{'follow_up_date':'2026-10-05'},'confirmation':{'kind':'explicit_instruction','user_wording':'Follow up October 5, 2026.'}})
        self.assertEqual(m.scan(self.log,NOW)['items'][0]['due_state'],'upcoming')
        for status in ('completed','cancelled'):
            self.log=self.change({'op':'update','commitment_id':'p','changes':{'status':status},'confirmation':{'kind':'user_confirmation','user_wording':f'Mark this fictional commitment {status}.'}})
            self.assertEqual(m.scan(self.log,NOW)['items'],[])

    def test_notification_is_not_recorded_by_scan_or_run_success(self):
        self.seeded();self.enable()
        result=m.scan(self.log,NOW)
        self.assertEqual(self.log['notifications'],[])
        req={'op':'observed','notification_tokens':[result['items'][0]['notification_token']],'output_ref':'fictional-run','observed':False,'confirmation':{'kind':'user_confirmation','user_wording':'The task status says succeeded.'}}
        with self.assertRaisesRegex(ValueError,'observed'):self.change(req)
        req['observed']=True;req.pop('confirmation')
        with self.assertRaisesRegex(ValueError,'confirmation'):self.change(req)

    def test_observed_output_suppresses_unchanged_but_changed_date_nudges(self):
        self.seeded();self.enable()
        token=m.scan(self.log,NOW)['items'][0]['notification_token']
        self.log=self.change({'op':'observed','notification_tokens':[token],'output_ref':'fictional-visible-output','observed':True,'confirmation':{'kind':'user_confirmation','user_wording':'I saw the outline reminder in the fictional task output.'}})
        self.assertEqual(self.log['notifications'][0]['receipt_basis'],'user_acknowledged_output')
        self.assertEqual(m.scan(self.log,'2026-10-05T01:30:00Z')['items'],[])
        self.log=self.change({'op':'update','commitment_id':'p','changes':{'deadline':'2026-10-05','deadline_raw':'October 5, 2026'},'confirmation':{'kind':'explicit_instruction','user_wording':'Move the outline to October 5, 2026.'}})
        self.assertEqual(len(m.scan(self.log,NOW)['items']),1)
        wrong={'op':'observed','notification_tokens':[token],'output_ref':'another-run','observed':True,'confirmation':{'kind':'user_confirmation','user_wording':'I saw the old reminder.'}}
        with self.assertRaisesRegex(ValueError,'current'):self.change(wrong)

    def test_inaccessible_or_invalid_log_is_not_a_successful_scan(self):
        with self.assertRaises(ValueError):m.scan(None,NOW)
        self.seeded();self.enable()
        self.log['notifications']=[{'notification_token':'invented'}]
        with self.assertRaisesRegex(ValueError,'notification'):m.scan(self.log,NOW)

if __name__=='__main__':unittest.main()
