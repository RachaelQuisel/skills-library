#!/usr/bin/env python3
"""Retrieve paper candidates and check source-linked research records."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


def now():
    return datetime.now(timezone.utc).isoformat()


def request(url, headers=None):
    h = {'User-Agent': 'CiteOrDecline/0.1 (public academic search)'}
    h.update(headers or {})
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=25) as response:
        return response.read().decode('utf-8')


def dates(start, end):
    for value in (start, end):
        if value:
            datetime.strptime(value, '%Y-%m-%d')
    if start and end and start > end:
        raise ValueError('start date must be before end date')


def search_arxiv(query, start=None, end=None, limit=10):
    dates(start, end)
    terms = query.split()
    # A space in an ungrouped query is rewritten by arXiv as OR, and AND binds
    # tighter than OR. `all:graph neural network AND submittedDate:[...]` is
    # read as `all:graph OR all:neural OR (all:network AND submittedDate:[...])`,
    # so hits miss the other words and the date range. Group every word first.
    if len(terms) > 1:
        search = 'all:(' + ' AND '.join(terms) + ')'
    else:
        search = f'all:{query}'
    if start or end:
        low = (start or '1991-01-01').replace('-', '') + '0000'
        high = (end or datetime.now(timezone.utc).date().isoformat()).replace('-', '') + '2359'
        search += f' AND submittedDate:[{low} TO {high}]'
    url = 'https://export.arxiv.org/api/query?' + urllib.parse.urlencode(
        {'search_query':search, 'start':0, 'max_results':limit})
    try:
        tree = ET.fromstring(request(url))
        ns = {'a':'http://www.w3.org/2005/Atom'}
        sources = []
        for entry in tree.findall('a:entry', ns):
            identifier = urllib.parse.urlsplit(entry.findtext('a:id', '', ns)).path.removeprefix('/abs/')
            if not re.fullmatch(r'(?:\d{4}\.\d{4,5}|[A-Za-z.-]+/\d{7})v\d+', identifier):
                raise ValueError('arXiv response lacks a versioned paper ID')
            abstract = ' '.join(entry.findtext('a:summary', '', ns).split())
            title = ' '.join(entry.findtext('a:title', '', ns).split())
            sources.append({'source_id':'arxiv-' + identifier.replace('/', '-'), 'identifier':identifier,
                            'url':'https://arxiv.org/abs/' + identifier, 'title':title,
                            'authors':[a.findtext('a:name', '', ns) for a in entry.findall('a:author', ns)],
                            'submitted_date':entry.findtext('a:published', None, ns),
                            'updated_date':entry.findtext('a:updated', None, ns), 'publication_date':None,
                            'scope':'abstract' if abstract else 'metadata', 'content':abstract or title,
                            'publication_status':'preprint', 'retrieved_at':now(),
                            'external_ids':{'arxiv':identifier}})
        return {'sources':sources, 'date_basis':'arxiv_submission', 'unavailable':None}
    except (OSError, ValueError, ET.ParseError) as error:
        return {'sources':[], 'unavailable':str(error), 'fallback':'Use WebSearch on arxiv.org; fetch evidence before citing.'}


def search_scholar(query, start=None, end=None, limit=10):
    dates(start, end)
    params = {'query':query, 'limit':limit, 'fields':'title,authors,url,abstract,externalIds,publicationDate'}
    if start or end:
        params['year'] = f'{(start or "1900")[:4]}:{(end or "2100")[:4]}'
    try:
        response = json.loads(request('https://api.semanticscholar.org/graph/v1/paper/search?' + urllib.parse.urlencode(params)))
        sources, unknown = [], 0
        for paper in response.get('data', []):
            publication = paper.get('publicationDate')
            if start or end:
                if not publication:
                    unknown += 1
                    continue
                if (start and publication < start) or (end and publication > end):
                    continue
            abstract = paper.get('abstract')
            identifier = paper['paperId']
            sources.append({'source_id':'scholar-' + identifier, 'identifier':identifier,
                            'url':paper.get('url') or 'https://www.semanticscholar.org/paper/' + identifier,
                            'title':paper['title'], 'authors':[a['name'] for a in paper.get('authors', [])],
                            'publication_date':publication, 'submitted_date':None, 'updated_date':None,
                            'scope':'abstract' if abstract else 'metadata', 'content':abstract or paper['title'],
                            'publication_status':'unknown', 'retrieved_at':now(),
                            'external_ids':{k.lower():v for k,v in paper.get('externalIds', {}).items()}})
        return {'sources':sources, 'date_basis':'reported_publication', 'unknown_date_count':unknown, 'unavailable':None}
    except (OSError, ValueError, KeyError, TypeError) as error:
        return {'sources':[], 'unavailable':str(error),
                'fallback':'Use WebSearch restricted to semanticscholar.org for candidates. Fetch a passage or record unavailable support.'}


def duplicate_groups(sources):
    keys = []
    for source in sources:
        ids = source.get('external_ids', {})
        normalized = set()
        for kind, value in ids.items():
            kind = kind.lower()
            if kind not in ('arxiv','doi') or not value:
                continue
            value = str(value).lower()
            if kind == 'arxiv':
                value = re.sub(r'v\d+$', '', value)
            normalized.add(f'{kind}:{value}')
        keys.append(normalized)
    groups = []
    remaining = set(range(len(sources)))
    while remaining:
        group = {remaining.pop()}
        linked = set().union(*(keys[i] for i in group))
        while True:
            found = {i for i in remaining if keys[i] & linked}
            if not found:
                break
            group |= found
            remaining -= found
            linked |= set().union(*(keys[i] for i in found))
        if len(group) > 1:
            groups.append([sources[i]['source_id'] for i in sorted(group)])
    return groups


def single_line(value, field):
    if not isinstance(value, str) or not value.strip() or any(ord(c) < 32 for c in value):
        raise ValueError(field + ' must be a nonempty single line')
    return value


def validate(records):
    if not isinstance(records, dict) or not isinstance(records.get('sources'), list) or not isinstance(records.get('claims'), list):
        raise ValueError('records require sources and claims arrays')
    sources = {}
    for source in records['sources']:
        identifier = single_line(source.get('source_id'), 'source_id')
        if identifier in sources:
            raise ValueError('duplicate source_id')
        for field in ('identifier','title','retrieved_at'):
            single_line(source.get(field), field)
        parsed = urllib.parse.urlsplit(single_line(source.get('url'), 'url'))
        if parsed.scheme not in ('https','http') or not parsed.netloc or parsed.username or parsed.password:
            raise ValueError('source URL must be a public HTTP(S) address without credentials')
        if source.get('scope') not in ('full_text','abstract','metadata'):
            raise ValueError('unknown access scope')
        if not isinstance(source.get('content'), str) or not source['content'].strip():
            raise ValueError('source needs actually retrieved content')
        if source.get('publication_status') not in ('preprint','published','unknown'):
            raise ValueError('publication_status must be preprint, published, or unknown')
        sources[identifier] = source
    seen = set()
    for claim in records['claims']:
        identifier = single_line(claim.get('claim_id'), 'claim_id')
        if identifier in seen:
            raise ValueError('duplicate claim_id')
        seen.add(identifier)
        single_line(claim.get('text'), 'claim text')
        status = claim.get('status')
        if status not in ('supported','contradicted','unverifiable'):
            raise ValueError('unknown claim status')
        evidence = claim.get('evidence', [])
        if not isinstance(evidence, list):
            raise ValueError('evidence must be an array')
        relationships = set()
        for item in evidence:
            source = sources.get(item.get('source_id'))
            if not source:
                raise ValueError('evidence refers to a missing source')
            passage = single_line(item.get('passage'), 'supporting passage')
            if passage not in source['content']:
                raise ValueError('supporting passage is absent from retrieved content')
            relation = item.get('relationship')
            if relation not in ('supports','contradicts'):
                raise ValueError('unknown evidence relationship')
            relationships.add(relation)
            if status == 'supported' and source['scope'] == 'metadata' and claim.get('kind') != 'bibliographic':
                raise ValueError('metadata cannot support a substantive claim')
        if status == 'supported':
            if 'supports' not in relationships:
                raise ValueError('supported claim needs supporting evidence')
            if 'contradicts' in relationships:
                raise ValueError('disagreement must remain explicit; do not mark the disputed claim supported')
            single_line(claim.get('support_review'), 'support_review')
            if type(claim.get('inference', False)) is not bool:
                raise ValueError('inference must be a boolean')
        else:
            single_line(claim.get('reason'), 'gap reason')
            reason_sources = claim.get('reason_source_ids', [])
            if not isinstance(reason_sources, list) or any(s not in sources for s in reason_sources):
                raise ValueError('gap explanation refers to a missing source')
            if status == 'contradicted' and 'contradicts' not in relationships:
                raise ValueError('contradicted claim needs contrary evidence')
    return sources


def escape(value):
    return re.sub(r'([\\`*_\[\]<>])', r'\\\1', value)


def cite(source):
    label = escape(f'{source["source_id"]}: {source["title"]} · {source["scope"]} · {source["publication_status"]}')
    url = urllib.parse.quote(source['url'], safe=':/?=&%#@+;,~!$')
    return f'[{label}]({url})'


def render(records):
    sources = validate(records)
    lines = ['## Supported claims']
    supported = [c for c in records['claims'] if c['status'] == 'supported']
    if not supported:
        lines.append('No supported claims.')
    for claim in supported:
        refs = ' '.join(cite(sources[e['source_id']]) for e in claim['evidence'])
        lines.append(f'- {"Inference: " if claim.get("inference") else ""}{escape(claim["text"])} {refs}')
    lines += ['', '## Unresolved claims']
    gaps = [c for c in records['claims'] if c['status'] != 'supported']
    if not gaps:
        lines.append('None recorded.')
    for claim in gaps:
        refs = ' '.join(cite(sources[s]) for s in claim.get('reason_source_ids', []))
        lines.append(f'- I can\'t verify this: “{escape(claim["text"])}” — {escape(claim["reason"])} ({escape(claim["claim_id"])}).{(" " + refs) if refs else ""}')
    lines += ['', '## Supporting passages']
    for claim in records['claims']:
        for evidence in claim.get('evidence', []):
            lines.append(f'- {escape(claim["claim_id"])} · {evidence["relationship"]}: “{escape(evidence["passage"])}” {cite(sources[evidence["source_id"]])}')
    lines += ['', '## References']
    for source in records['sources']:
        lines.append(f'- {cite(source)}; identifier {escape(source["identifier"])}; retrieved {escape(source["retrieved_at"])}.')
    return '\n'.join(lines)


def session_path(data, session):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', session):
        raise ValueError('invalid session ID')
    return data / 'sessions' / (session + '.json')


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as file:
        json.dump(value, file, ensure_ascii=False, indent=2)
        file.flush()
        os.fsync(file.fileno())
    os.replace(file.name, path)


def begin(data, session):
    atomic_json(session_path(data, session), {'active':True,'completed':False,'records':None,'brief':None})


def prepare(data, session, records):
    brief = render(records)
    atomic_json(session_path(data, session), {'active':True,'completed':False,'records':records,'brief':brief})
    return brief


def final_check(data, event):
    path = session_path(data, event['session_id'])
    if not path.exists():
        return {}
    state = json.loads(path.read_text(encoding='utf-8'))
    if not state.get('active'):
        return {}
    actual = event.get('last_assistant_message', '').strip()
    expected = render(state['records']) if state.get('records') is not None else None
    passed = expected is not None and actual == expected.strip()
    audit = data / 'audits' / (event['session_id'] + '.jsonl')
    audit.parent.mkdir(parents=True, exist_ok=True)
    with audit.open('a', encoding='utf-8') as file:
        os.chmod(audit, 0o600)
        file.write(json.dumps({'time':now(),'actual':actual,'coverage_pass':passed}, ensure_ascii=False) + '\n')
    if passed:
        state['active'], state['completed'] = False, True
        atomic_json(path, state)
        return {}
    if event.get('stop_hook_active'):
        return {'continue':False,'stopReason':'Cite-or-Decline final-response coverage failed. The local audit records the unchecked reply; this run is incomplete.'}
    return {'decision':'block','reason':f'Citation coverage failed. Prepare checked claim records if missing. Then read {path} and return exactly its brief string, with no added introduction, heading, code fence, or conclusion. Unsupported claims must remain declined.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', type=Path, default=Path.home() / '.local/share/cite-or-decline')
    sub = parser.add_subparsers(dest='command', required=True)
    search = sub.add_parser('search')
    search.add_argument('--provider', choices=['arxiv','scholar'], required=True)
    search.add_argument('--query', required=True)
    search.add_argument('--start')
    search.add_argument('--end')
    search.add_argument('--limit', type=int, default=10)
    start_session = sub.add_parser('begin')
    start_session.add_argument('--session-id', required=True)
    prepared = sub.add_parser('prepare')
    prepared.add_argument('--session-id', required=True)
    prepared.add_argument('--input', type=Path, required=True)
    prepared.add_argument('--output', type=Path, required=True)
    sub.add_parser('final-check')
    duplicates = sub.add_parser('duplicates')
    duplicates.add_argument('--input', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'search':
            if not 1 <= args.limit <= 20:
                raise ValueError('limit must be between 1 and 20')
            function = search_arxiv if args.provider == 'arxiv' else search_scholar
            result = function(args.query, args.start, args.end, args.limit)
        elif args.command == 'begin':
            begin(args.data_dir, args.session_id)
            result = {'session_id':args.session_id,'citation_mode':'active'}
        elif args.command == 'prepare':
            records = json.loads(args.input.read_text(encoding='utf-8'))
            brief = render(records)
            outputs = {args.output:brief,
                       args.output.with_suffix('.references.json'):json.dumps(records['sources'],ensure_ascii=False,indent=2),
                       args.output.with_suffix('.gaps.json'):json.dumps([c for c in records['claims'] if c['status'] != 'supported'],ensure_ascii=False,indent=2)}
            if any(p.exists() for p in outputs):
                raise ValueError('export destination already exists; choose a new output name')
            for path, content in outputs.items():
                with path.open('x', encoding='utf-8') as file:
                    file.write(content)
            prepare(args.data_dir, args.session_id, records)
            result = {'brief':brief,'exports':[str(p) for p in outputs], 'semantic_support':'reviewed by Claude or user; structural checks do not prove truth'}
        elif args.command == 'duplicates':
            result = {'same_work_groups':duplicate_groups(json.loads(args.input.read_text(encoding='utf-8'))['sources'])}
        else:
            result = final_check(args.data_dir, json.load(sys.stdin))
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        if args.command == 'final-check':
            print(json.dumps({'continue':False,'stopReason':'Cite-or-Decline final-response check failed: ' + str(error)}))
            return 0
        print('error: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
