"""Contact log operations. Cloud storage and delivery use the host connector.

No network, credentials, persistent home-directory state, or account mutations.
Every result is a new JSON snapshot. Existing input/output files stay intact.
"""
import argparse
import copy
import hashlib
import json
import re
import sys
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


def text(value, label):
    if not isinstance(value,str) or not value.strip():
        raise ValueError(f'{label} must be nonempty text')
    return value


def ident(value, label):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,95}',value):
        raise ValueError(f'{label} is an invalid ID')
    return value


def moment(value):
    value=text(value,'timestamp')
    result=datetime.fromisoformat(value.replace('Z','+00:00'))
    if result.tzinfo is None:raise ValueError('timestamp must include a timezone')
    return result


def day(value):
    if value is None:return None
    if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):
        raise ValueError('date must be YYYY-MM-DD or null; clarify ambiguous dates')
    return date.fromisoformat(value)


def zone(value):
    text(value,'time_zone')
    try:return ZoneInfo(value)
    except (KeyError,ValueError):raise ValueError('Unknown IANA time_zone') from None


def initial(log_id, now):
    ident(log_id,'log_id');moment(now)
    return {'schema_version':1,'log_id':log_id,'snapshot_id':str(uuid.uuid4()),'revision':1,
            'parent_snapshot_id':None,'saved_at':now,'contacts':[],'encounters':[],
            'commitments':[],'reminders':{'enabled':False,'cadence':None,'lead_days':0,'time_zone':'UTC'},
            'notifications':[]}


def unique(items,key):
    if not isinstance(items,list):raise ValueError(f'{key} records must be an array')
    found=set()
    for item in items:
        if not isinstance(item,dict):raise ValueError(f'{key} record must be an object')
        value=ident(item.get(key),key)
        if value in found:raise ValueError(f'Duplicate {key}')
        found.add(value)
    return found


def validate(log):
    if not isinstance(log,dict) or log.get('schema_version')!=1:raise ValueError('Unsupported snapshot schema')
    for key in ('log_id','snapshot_id'):ident(log.get(key),key)
    if type(log.get('revision')) is not int or log['revision']<1:raise ValueError('Invalid revision')
    if log.get('parent_snapshot_id') is not None:ident(log['parent_snapshot_id'],'parent_snapshot_id')
    if (log['revision']==1)!=(log.get('parent_snapshot_id') is None):raise ValueError('Invalid root revision')
    moment(log.get('saved_at'))
    contacts=unique(log.get('contacts'),'contact_id')
    for c in log['contacts']:
        text(c.get('name'),'name');text(c.get('identifying_details'),'identifying_details')
    unique(log.get('encounters'),'encounter_id')
    for e in log['encounters']:
        if e.get('contact_id') not in contacts:raise ValueError('Unknown encounter contact')
        day(e.get('meeting_date'));text(e.get('source_notes'),'source_notes')
    unique(log.get('commitments'),'commitment_id')
    for c in log['commitments']:
        if c.get('contact_id') not in contacts:raise ValueError('Unknown commitment contact')
        if c.get('who_owes') not in ('me','contact'):raise ValueError('who_owes must be me or contact')
        text(c.get('action'),'action');text(c.get('source_ref'),'source_ref')
        for key in ('deadline','follow_up_date'):day(c.get(key))
        if c.get('deadline_raw') is not None:text(c['deadline_raw'],'deadline_raw')
        if c.get('deadline') is not None and c.get('deadline_raw') is None:raise ValueError('A normalized deadline needs its source wording')
        zone(c.get('time_zone'))
        if c.get('status') not in ('open','completed','cancelled'):raise ValueError('Invalid status')
        if not isinstance(c.get('history'),list) or not c['history']:raise ValueError('Commitment needs status history')
        for h in c['history']:
            moment(h.get('at'));text(h.get('event'),'history event');text(h.get('source_wording'),'source_wording')
    r=log.get('reminders')
    if not isinstance(r,dict) or type(r.get('enabled')) is not bool:raise ValueError('Invalid reminder settings')
    if type(r.get('lead_days')) is not int or r['lead_days']<0:raise ValueError('lead_days must be a nonnegative integer')
    zone(r.get('time_zone'))
    if r['enabled']:text(r.get('cadence'),'Enabled reminder cadence')
    if not isinstance(log.get('notifications'),list):raise ValueError('Invalid notification history')
    receipt_tokens=set()
    for receipt in log['notifications']:
        if not isinstance(receipt,dict):raise ValueError('Invalid notification receipt')
        token=receipt.get('notification_token')
        if not isinstance(token,str) or not re.fullmatch(r'[0-9a-f]{64}',token) or token in receipt_tokens:
            raise ValueError('Invalid or duplicate notification token')
        receipt_tokens.add(token)
        if receipt.get('commitment_id') not in {c['commitment_id'] for c in log['commitments']}:
            raise ValueError('Invalid notification commitment')
        if receipt.get('receipt_basis')!='user_acknowledged_output':raise ValueError('Invalid notification receipt basis')
        moment(receipt.get('observed_at'));text(receipt.get('output_ref'),'notification output_ref')
        text(receipt.get('source_wording'),'notification source_wording')
    return log


def resolve(snapshots, log_id):
    ident(log_id,'log_id')
    if not isinstance(snapshots,list) or not snapshots:raise ValueError('No snapshots; do not report a successful scan')
    nodes={}
    for record in snapshots:
        validate(record)
        if record['log_id']!=log_id:raise ValueError('Unexpected log_id in selected snapshot set')
        key=record['snapshot_id']
        if key in nodes and nodes[key]!=record:raise ValueError('Conflicting contents for one snapshot ID')
        nodes[key]=record
    parents=set()
    for node in nodes.values():
        parent=node['parent_snapshot_id']
        if parent is not None:
            if parent not in nodes:raise ValueError('Missing parent snapshot; current log unresolved')
            if node['revision']!=nodes[parent]['revision']+1:raise ValueError('Broken revision chain')
            parents.add(parent)
    heads=set(nodes)-parents
    roots=[n for n in nodes.values() if n['parent_snapshot_id'] is None]
    if len(heads)!=1 or len(roots)!=1:raise ValueError('Conflicting snapshot branches; resolve with user before writing')
    return copy.deepcopy(nodes[heads.pop()])


def contact(log, selector):
    exact=[c for c in log['contacts'] if c['contact_id']==selector]
    if exact:return exact[0]
    matches=[c for c in log['contacts'] if c['name'].casefold()==selector.casefold()]
    if len(matches)>1:raise ValueError('Ambiguous contact name; choose contact_id and identifying details')
    if not matches:raise ValueError('Contact not found')
    return matches[0]


def confirmed(req):
    c=req.get('confirmation')
    if not isinstance(c,dict) or c.get('kind') not in ('explicit_instruction','user_confirmation'):
        raise ValueError('User confirmation is required for a commitment or update')
    return text(c.get('user_wording'),'confirmation user_wording')


def mutate(base, req, expected_snapshot_id, now):
    validate(base);moment(now)
    if base['snapshot_id']!=expected_snapshot_id:raise ValueError('Stale snapshot; reload current log before saving')
    out=copy.deepcopy(base)
    op=req.get('op')
    if op=='contact':
        item={k:req.get(k) for k in ('contact_id','name','identifying_details')}
        if any(c['contact_id']==item['contact_id'] for c in out['contacts']):raise ValueError('Contact ID already exists')
        out['contacts'].append(item)
    elif op=='encounter':
        contact(out,req.get('contact_id',''))
        item={k:req.get(k) for k in ('encounter_id','contact_id','meeting_date','source_notes')}
        out['encounters'].append(item)
    elif op=='commitment':
        wording=confirmed(req)
        contact(out,req.get('contact_id',''))
        item={k:req.get(k) for k in ('commitment_id','contact_id','who_owes','action','source_ref','deadline_raw','deadline','follow_up_date','time_zone')}
        item['status']='open';item['history']=[{'at':now,'event':'recorded','source_wording':wording,'status':'open','deadline':item['deadline'],'deadline_raw':item['deadline_raw'],'follow_up_date':item['follow_up_date']}]
        out['commitments'].append(item)
    elif op=='update':
        wording=confirmed(req)
        matches=[c for c in out['commitments'] if c['commitment_id']==req.get('commitment_id')]
        if not matches:raise ValueError('Commitment not found')
        item=matches[0];changes=req.get('changes')
        allowed={'status','action','deadline_raw','deadline','follow_up_date','time_zone'}
        if not isinstance(changes,dict) or not changes or set(changes)-allowed:raise ValueError('Invalid commitment changes')
        if 'deadline' in changes and changes['deadline']!=item['deadline'] and 'deadline_raw' not in changes:
            raise ValueError('Changed deadline requires new deadline_raw source wording')
        before={k:item.get(k) for k in allowed}
        item.update(changes)
        after={k:item.get(k) for k in allowed}
        item['history'].append({'at':now,'event':'rescheduled' if any(k in changes for k in ('deadline','follow_up_date')) else 'updated',
                                'source_wording':wording,'before':before,'after':after})
    elif op=='reminders':
        confirmed(req)
        out['reminders']={k:req.get(k) for k in ('enabled','cadence','lead_days','time_zone')}
    elif op=='observed':
        wording=confirmed(req)
        if req.get('observed') is not True:raise ValueError('Output must have been observed; run success is not a receipt')
        output_ref=text(req.get('output_ref'),'output_ref')
        tokens=req.get('notification_tokens')
        if not isinstance(tokens,list) or not tokens or any(not isinstance(t,str) for t in tokens) or len(set(tokens))!=len(tokens):
            raise ValueError('Choose unique notification tokens from the observed current output')
        candidates={item['notification_token']:item for item in scan(base,now)['items']}
        if any(t not in candidates for t in tokens):raise ValueError('Notification does not match an unacknowledged current commitment')
        for token in tokens:
            out['notifications'].append({'notification_token':token,'commitment_id':candidates[token]['commitment_id'],
                                         'observed_at':now,'output_ref':output_ref,'receipt_basis':'user_acknowledged_output',
                                         'source_wording':wording})
    else:raise ValueError('Unknown mutation operation')
    out.update(snapshot_id=str(uuid.uuid4()),parent_snapshot_id=base['snapshot_id'],revision=base['revision']+1,saved_at=now)
    return validate(out)


def query(log, now, selector=None):
    validate(log);instant=moment(now)
    selected=[contact(log,selector)] if selector else log['contacts']
    ids={c['contact_id'] for c in selected};items=[]
    for original in log['commitments']:
        if original['contact_id'] not in ids or (selector is None and original['who_owes']!='me'):continue
        item=copy.deepcopy(original)
        local_date=instant.astimezone(zone(item['time_zone'])).date()
        dates=[day(item[k]) for k in ('deadline','follow_up_date') if item.get(k) is not None]
        nearest=min(dates) if dates else None
        item['current_date']=local_date.isoformat()
        item['due_state']='closed' if item['status']!='open' else 'undated' if nearest is None else 'overdue' if nearest<local_date else 'today' if nearest==local_date else 'upcoming'
        item['completion_basis']='user_reported' if item['status']=='completed' else None
        item['contact_name']=contact(log,item['contact_id'])['name']
        item['identifying_details']=contact(log,item['contact_id'])['identifying_details']
        items.append(item)
    return {'log_id':log['log_id'],'snapshot_id':log['snapshot_id'],'revision':log['revision'],
            'contacts':copy.deepcopy(selected),'encounters':[copy.deepcopy(e) for e in log['encounters'] if e['contact_id'] in ids],
            'commitments':items,'queried_at':now}


def scan(log, now):
    validate(log);instant=moment(now);settings=log['reminders']
    result={'log_id':log['log_id'],'snapshot_id':log['snapshot_id'],'revision':log['revision'],
            'checked_at':now,'scan_date':instant.astimezone(zone(settings['time_zone'])).date().isoformat(),
            'time_zone':settings['time_zone'],'status':'disabled' if not settings['enabled'] else 'checked','items':[]}
    if not settings['enabled']:return result
    observed={n['notification_token'] for n in log['notifications']}
    for original in log['commitments']:
        if original['status']!='open':continue
        local_date=instant.astimezone(zone(original['time_zone'])).date()
        dates=[day(original[k]) for k in ('deadline','follow_up_date') if original.get(k) is not None]
        if not dates or min((d-local_date).days for d in dates)>settings['lead_days']:continue
        state={k:original.get(k) for k in ('commitment_id','contact_id','who_owes','action','status','deadline_raw','deadline','follow_up_date','time_zone')}
        state['log_id']=log['log_id']
        token=hashlib.sha256(json.dumps(state,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        if token in observed:continue
        item=copy.deepcopy(original);person=contact(log,item['contact_id'])
        nearest=min(dates)
        item.update(contact_name=person['name'],identifying_details=person['identifying_details'],current_date=local_date.isoformat(),
                    due_state='overdue' if nearest<local_date else 'today' if nearest==local_date else 'upcoming',notification_token=token)
        result['items'].append(item)
    return result


def write_new(path, value):
    with Path(path).open('x',encoding='utf-8') as stream:
        import os
        os.chmod(path,0o600)
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['init','resolve','mutate','query','scan'])
    parser.add_argument('--input',type=Path);parser.add_argument('--request',type=Path)
    parser.add_argument('--log-id');parser.add_argument('--expected-snapshot-id')
    parser.add_argument('--contact')
    parser.add_argument('--now',default=datetime.now(timezone.utc).isoformat())
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        source=json.loads(args.input.read_text()) if args.input else None
        if args.command=='init':result=initial(args.log_id,args.now)
        elif args.command=='resolve':result=resolve(source,args.log_id)
        elif args.command=='query':result=query(source,args.now,args.contact)
        elif args.command=='scan':result=scan(source,args.now)
        else:result=mutate(source,json.loads(args.request.read_text()),args.expected_snapshot_id,args.now)
        if args.output:write_new(args.output,result)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except (ValueError,TypeError,KeyError,OSError) as exc:
        print(json.dumps({'status':'error','error':str(exc)}),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
