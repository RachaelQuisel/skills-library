#!/usr/bin/env python3
"""Inventory only user-selected CSVs. No network, client matching, or data writes."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import date, timedelta
import hashlib
import html
import json
import os
from pathlib import Path
import re
import tempfile

GROUPS = ('gol-applications', 'gol-renewals', 'diup-applications', 'diup-renewals')
BINTI_REQUIRED = {'Binti application id', 'CBOs', 'Status', 'Application template', 'Applicant name'}
ACUITY_REQUIRED = {'First Name', 'Last Name', 'Phone', 'Email'}


def read_csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle, strict=True)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)):
            raise ValueError('Duplicate CSV column names')
        missing = sorted(required - set(headers))
        if missing:
            raise ValueError('Missing required columns: ' + ', '.join(missing))
        rows = []
        for line, row in enumerate(reader, 2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f'CSV column count mismatch at row {line}')
            rows.append(row)
        return rows


def fingerprint(path: Path) -> dict:
    return {'path': str(path), 'filename': path.name,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'export_date': None, 'export_date_note': 'Record from verified provenance; not inferred from filename or modification time.'}


def canonical_phone(value: str) -> str:
    value = html.unescape(value).strip().strip("'\"").strip()
    if not re.fullmatch(r'\+?[0-9\s().-]+', value):
        return ''
    digits = re.sub(r'[^0-9]', '', value)
    if len(digits) == 10 and not value.startswith('+'):
        return '+1' + digits
    if len(digits) == 11 and digits.startswith('1'):
        return '+' + digits
    if value.startswith('+') and not digits.startswith(('0', '1')) and 8 <= len(digits) <= 15:
        return '+' + digits
    return ''


def person_present(row: dict, prefix: str) -> bool:
    return any(row.get(f'{prefix} {part}', '').strip() for part in
               ('name', 'first name', 'middle name', 'last name', 'suffix', 'email', 'phone number'))


def row_groups(row: dict) -> tuple[list[str], list[str]]:
    cbo = row.get('CBOs', '').casefold()
    organizations = []
    if re.search(r'\bguardians\s+of\s+love\b', cbo):
        organizations.append('gol')
    if re.search(r'\bdangerfield\s+institute\b', cbo):
        organizations.append('diup')
    warnings = []
    if not organizations:
        warnings.append('No recognized EA or PARTNER organization; clarify the source.')
    template = row.get('Application template', '').casefold()
    status = row.get('Status', '').strip().casefold()
    template_stage = ('renewals' if 'renewal' in template else
                      'applications' if 'application' in template else None)
    status_stage = {'applying': 'applications', 'in renewal': 'renewals'}.get(status)
    if template_stage and status_stage and template_stage != status_stage:
        warnings.append('Application template and status disagree about applications versus renewals.')
        return [], warnings
    stage = template_stage or status_stage
    if not stage:
        warnings.append('Application or renewal stage is unclear.')
        return [], warnings
    return [f'{org}-{stage}' for org in organizations], warnings


def inspect_binti(path: Path, as_of: date, recent_days: int) -> dict:
    rows = read_csv(path, BINTI_REQUIRED)
    result = {**fingerprint(path), 'application_rows': len(rows), 'applicant_occurrences': 0,
              'cbo_values': dict(Counter(r['CBOs'].strip() for r in rows)),
              'status_values': dict(Counter(r['Status'].strip() for r in rows)),
              'groups': {}, 'warnings': []}
    warnings = result['warnings']
    if not rows:
        warnings.append({'row': None, 'reason': 'Empty export; confirm scope before treating any group as checked.'})
    ids = Counter(r['Binti application id'].strip() for r in rows if r['Binti application id'].strip())
    result['duplicate_application_identifiers'] = sum(n > 1 for n in ids.values())
    groups = defaultdict(lambda: {'application_rows': 0, 'applicant_occurrences': 0,
                                 'recent_inquiry_occurrences': 0, 'inquiry_date_unknown_occurrences': 0})
    start = as_of - timedelta(days=recent_days - 1)
    for line, row in enumerate(rows, 2):
        memberships, issues = row_groups(row)
        if not row['Binti application id'].strip():
            issues.append('Binti application ID is blank; investigate before matching or writing.')
        if ids[row['Binti application id'].strip()] > 1:
            issues.append('Binti application ID repeats in this export; preserve all source rows for review.')
        count = sum(person_present(row, prefix) for prefix in ('Applicant', 'Co-applicant'))
        result['applicant_occurrences'] += count
        if not person_present(row, 'Applicant'):
            issues.append('Primary applicant details are blank.')
        for prefix in ('Applicant', 'Co-applicant'):
            if person_present(row, prefix) and not any(row.get(f'{prefix} {part}', '').strip() for part in ('name', 'first name', 'last name')):
                issues.append(f'{prefix} has contact details but no usable name.')
        declared = row.get('Number of applicants', '').strip()
        if declared:
            try:
                if int(declared) != count:
                    issues.append('Number of applicants differs from populated applicant/co-applicant entries.')
            except ValueError:
                issues.append('Number of applicants is not an integer.')
        try:
            inquiry = date.fromisoformat(row.get('Date of inquiry', '').strip())
        except ValueError:
            inquiry = None
        if inquiry and inquiry > as_of:
            issues.append('Inquiry date is after the as-of date; verify the date.')
        for group in memberships:
            group_count = groups[group]
            group_count['application_rows'] += 1
            group_count['applicant_occurrences'] += count
            if group.endswith('-applications'):
                if inquiry is None:
                    group_count['inquiry_date_unknown_occurrences'] += count
                elif start <= inquiry <= as_of:
                    group_count['recent_inquiry_occurrences'] += count
            else:
                group_count['recent_inquiry_occurrences'] = None
                group_count['inquiry_date_unknown_occurrences'] = None
        warnings.extend({'row': line, 'reason': reason} for reason in issues)
    result['groups'] = dict(groups)
    return result


def inspect_acuity(path: Path) -> dict:
    rows = read_csv(path, ACUITY_REQUIRED)
    phones = Counter(canonical_phone(r['Phone']) for r in rows if canonical_phone(r['Phone']))
    invalid_email = lambda value: bool(value.strip()) and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value.strip())
    return {**fingerprint(path), 'client_records': len(rows),
            'blank_email_records': sum(not r['Email'].strip() for r in rows),
            'invalid_nonblank_email_records': sum(bool(invalid_email(r['Email'])) for r in rows),
            'blank_phone_records': sum(not r['Phone'].strip() for r in rows),
            'unparsed_nonblank_phone_records': sum(bool(r['Phone'].strip()) and not canonical_phone(r['Phone']) for r in rows),
            'garbled_apostrophe_phone_records': sum(bool(re.search(r'&#0*39;|&#x0*27;', r['Phone'], re.I)) for r in rows),
            'phone_numbers_used_by_multiple_clients': sum(count > 1 for count in phones.values()),
            'client_records_sharing_phone_numbers': sum(count for count in phones.values() if count > 1),
            'scope_note': 'Counts include all supplied rows, including any duplicates or test records. A CSV alone does not verify the account or All clients filter.',
            'account_verified': False, 'all_clients_filter_verified': False}


def build_inventory(binti_paths: list[Path], acuity_path: Path | None, as_of: date,
                    recent_days: int, expected: list[str]) -> dict:
    if recent_days < 1:
        raise ValueError('recent_days must be positive')
    if any(group not in GROUPS for group in expected):
        raise ValueError('Unknown expected group')
    files, errors, seen_paths, seen_hashes = [], [], set(), set()
    for supplied in binti_paths:
        path = supplied.expanduser().resolve()
        if path in seen_paths:
            errors.append({'path': str(path), 'reason': 'Same input path supplied twice; counted only once.'})
            continue
        seen_paths.add(path)
        try:
            entry = inspect_binti(path, as_of, recent_days)
            if entry['sha256'] in seen_hashes:
                errors.append({'path': str(path), 'reason': 'Identical export contents already supplied; counted only once.'})
                continue
            seen_hashes.add(entry['sha256'])
            files.append(entry)
        except (OSError, ValueError, csv.Error) as exc:
            errors.append({'path': str(path), 'reason': str(exc)})
    received = {group for entry in files for group in entry['groups']}
    states = {group: ('received' if group in received and group in expected else
                      'pending' if group in expected else 'out of scope') for group in GROUPS}
    acuity = None
    if acuity_path:
        try:
            acuity = inspect_acuity(acuity_path.expanduser().resolve())
        except (OSError, ValueError, csv.Error) as exc:
            errors.append({'path': str(acuity_path), 'reason': str(exc)})
    return {'as_of_date': as_of.isoformat(),
            'recent_applications': {'field': 'Date of inquiry', 'from': (as_of - timedelta(days=recent_days - 1)).isoformat(),
                                    'through': as_of.isoformat(), 'renewals': 'Not classified by original inquiry date'},
            'expected_groups': expected, 'group_status': states, 'binti_files': files,
            'received_groups_outside_requested_scope': sorted(received - set(expected)),
            'acuity': acuity, 'errors': errors,
            'needs_attention': bool(errors or any(f['warnings'] for f in files) or 'pending' in states.values() or acuity is None),
            'comparison_complete': False, 'writes_authorized': False,
            'note': 'Inventory only. Verify account, provenance, source completeness, Airtable data, identities, and authorization before any client writes. Mixed-group source rows can appear in several group views.'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binti', action='append', type=Path, default=[])
    parser.add_argument('--acuity', type=Path)
    parser.add_argument('--as-of', type=date.fromisoformat, required=True)
    parser.add_argument('--recent-days', type=int, default=30)
    parser.add_argument('--expect-group', action='append', choices=GROUPS)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.recent_days < 1:
        parser.error('--recent-days must be positive')
    if not args.binti and not args.acuity:
        parser.error('Supply at least one explicit CSV path')
    output = args.output.expanduser().resolve()
    inputs = {p.expanduser().resolve() for p in args.binti + ([args.acuity] if args.acuity else [])}
    if output in inputs:
        parser.error('Output must not overwrite a source CSV')
    if output.is_relative_to(Path(__file__).resolve().parents[1]):
        parser.error('Save private run outputs outside the skill folder')
    result = build_inventory(args.binti, args.acuity, args.as_of, args.recent_days, args.expect_group or list(GROUPS))
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=output.parent, delete=False) as handle:
        temp = Path(handle.name)
        json.dump(result, handle, indent=2, ensure_ascii=False)
        handle.write('\n')
    try:
        os.chmod(temp, 0o600)
        os.replace(temp, output)
    finally:
        temp.unlink(missing_ok=True)
    print(json.dumps({'inventory': str(output), 'group_status': result['group_status'],
                      'needs_attention': result['needs_attention'], 'comparison_complete': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
