#!/usr/bin/env python3
"""Save writing preferences and apply approved edits with Humanize Output."""

import argparse
import difflib
import json
import os
from pathlib import Path
import re
import sys
import tempfile


PATTERNS = [
    ("it's worth noting", 'filler', 'This opening adds no information.', 'State the point directly.'),
    ('it’s worth noting', 'filler', 'This opening adds no information.', 'State the point directly.'),
    ('delve', 'vocabulary', 'This verb can make the action unclear.', 'Consider examine, read, or explore. Keep the original meaning.'),
    ('leverage', 'vocabulary', 'This word can make the action unclear.', 'Consider use. Keep the original meaning.'),
    ('deep dive', 'cliche', 'This phrase may be less clear than the specific activity.', 'Describe the specific activity.'),
    ('game changer', 'empty_claim', 'This phrase claims a large impact without evidence.', 'Describe the supported impact. Otherwise, remove the claim.'),
    ('in conclusion', 'transition', 'This transition may be unnecessary.', 'State the final point directly.'),
    ('in today’s rapidly evolving', 'cliche', 'This opening does not name a specific context.', 'Start with the specific topic.'),
    ("in today's rapidly evolving", 'cliche', 'This opening does not name a specific context.', 'Start with the specific topic.'),
]


def profile_path(data_dir, profile_id):
    if not isinstance(profile_id, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', profile_id):
        raise ValueError('Use 1 to 64 letters, numbers, underscores, or hyphens in profile_id. Start with a letter or number.')
    return data_dir / 'profiles' / (profile_id + '.json')


def validate_profile(profile):
    if not isinstance(profile, dict) or profile.get('reviewed') is not True:
        raise ValueError('Review the profile rules before saving. Set reviewed: true after approval.')
    for key in ('rules', 'disliked_phrases', 'exceptions'):
        values = profile.get(key)
        if not isinstance(values, list) or any(not isinstance(v, str) or not v.strip() for v in values):
            raise ValueError(f'Provide {key} as a list of text values. Each value must contain text.')
    return profile


def read_profile(data_dir, profile_id):
    path = profile_path(data_dir, profile_id)
    if not path.is_file():
        raise ValueError(f'The profile was not found: {profile_id}.')
    profile = validate_profile(json.loads(path.read_text(encoding='utf-8')))
    if profile.get('profile_id') != profile_id:
        raise ValueError('The stored profile_id does not match the requested profile.')
    return profile


def save_profile(data_dir, profile):
    validate_profile(profile)
    path = profile_path(data_dir, profile.get('profile_id'))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as f:
            temporary = Path(f.name)
            json.dump(profile, f, ensure_ascii=False, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        temporary.replace(path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return {'profile': profile, 'path': str(path)}


def scan(draft, profile=None):
    profile = profile or {'exceptions': [], 'disliked_phrases': []}
    exceptions = []
    for phrase in profile['exceptions']:
        exceptions.extend((m.start(), m.end()) for m in re.finditer(re.escape(phrase), draft, re.I))
    patterns = list(PATTERNS)
    for phrase in profile['disliked_phrases']:
        if phrase.casefold() not in {p[0].casefold() for p in patterns}:
            patterns.append((phrase, 'personal_rule', 'The saved checklist flags this phrase.',
                             'Choose a replacement that follows the reviewed rules.'))
    flags = []
    for phrase, category, explanation, suggestion in patterns:
        for match in re.finditer(r'(?<!\w)' + re.escape(phrase) + r'(?!\w)', draft, re.I):
            if any(start <= match.start() and match.end() <= end for start, end in exceptions):
                continue
            flags.append({'start': match.start(), 'end': match.end(), 'original': match.group(),
                          'category': category, 'explanation': explanation, 'suggestion': suggestion})
    return {'profile_id': profile.get('profile_id'),
            'style_label': 'reviewed profile' if profile.get('profile_id') else 'default plain writing',
            'flags': sorted(flags, key=lambda f: (f['start'], f['end']))}


def apply_edits(draft, change_set):
    if not isinstance(change_set, dict) or not isinstance(change_set.get('edits'), list):
        raise ValueError('Provide an object with an edits list.')
    protected = change_set.get('protected_phrases', [])
    if not isinstance(protected, list) or any(not isinstance(p, str) or not p for p in protected):
        raise ValueError('Provide protected_phrases as a list of text values. Each value must contain text.')
    accepted = []
    for edit in change_set['edits']:
        if not isinstance(edit, dict) or type(edit.get('accepted')) is not bool:
            raise ValueError('Set accepted to true or false for every edit.')
        start, end = edit.get('start'), edit.get('end')
        if type(start) is not int or type(end) is not int or not 0 <= start <= end <= len(draft):
            raise ValueError('Use valid start and end character positions within the draft.')
        if not isinstance(edit.get('original'), str) or not isinstance(edit.get('replacement'), str):
            raise ValueError('Provide original and replacement as text.')
        if draft[start:end] != edit['original']:
            raise ValueError('The source text changed. Scan the current draft before applying this edit.')
        if edit['accepted']:
            accepted.append(edit)
    accepted.sort(key=lambda e: (e['start'], e['end']))
    for previous, current in zip(accepted, accepted[1:]):
        if previous['end'] > current['start'] or previous['start'] == current['start']:
            raise ValueError('The accepted edits overlap. Review them before applying changes.')
    revised = draft
    for edit in reversed(accepted):
        revised = revised[:edit['start']] + edit['replacement'] + revised[edit['end']:]
    numbers = r'(?<!\w)[+-]?\d+(?:[.,]\d+)*(?:%|\b)'
    quotations = r'"[^"\n]*"|“[^”\n]*”|(?<!\w)\x27[^\x27\n]*\x27(?!\w)|‘[^’\n]*’'
    if re.findall(numbers, draft) != re.findall(numbers, revised):
        raise ValueError('An edit changed protected numbers.')
    if re.findall(quotations, draft) != re.findall(quotations, revised):
        raise ValueError('An edit changed protected quotations.')
    if any(draft.count(phrase) != revised.count(phrase) for phrase in protected):
        raise ValueError('An edit changed protected phrases.')
    return revised, len(accepted)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=Path.home() / '.local' / 'share' / 'de-slop')
    commands = parser.add_subparsers(dest='command', required=True)
    save = commands.add_parser('profile-save')
    save.add_argument('--input', type=Path, required=True)
    get = commands.add_parser('profile-get')
    get.add_argument('--id', required=True)
    check = commands.add_parser('scan')
    check.add_argument('--draft', type=Path, required=True)
    check.add_argument('--profile')
    apply = commands.add_parser('apply')
    apply.add_argument('--draft', type=Path, required=True)
    apply.add_argument('--edits', type=Path, required=True)
    apply.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'profile-save':
            result = save_profile(args.data_dir, json.loads(args.input.read_text(encoding='utf-8')))
        elif args.command == 'profile-get':
            result = {'profile': read_profile(args.data_dir, args.id)}
        elif args.command == 'scan':
            profile = read_profile(args.data_dir, args.profile) if args.profile else None
            result = scan(args.draft.read_text(encoding='utf-8'), profile)
        else:
            if args.output.resolve() == args.draft.resolve() or args.output.exists():
                raise ValueError('Choose a new output file. The tool will not overwrite the source or an existing file.')
            draft = args.draft.read_text(encoding='utf-8')
            revised, count = apply_edits(draft, json.loads(args.edits.read_text(encoding='utf-8')))
            with args.output.open('x', encoding='utf-8') as output:
                output.write(revised)
            result = {'path': str(args.output), 'accepted_edits': count,
                      'diff': ''.join(difflib.unified_diff(draft.splitlines(keepends=True),
                                                         revised.splitlines(keepends=True),
                                                         fromfile=str(args.draft), tofile=str(args.output)))}
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError, TypeError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
