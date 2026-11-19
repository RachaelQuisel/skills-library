"""Offline package checks. This does not replace the Claude validator."""
from pathlib import Path
import json
import re
import struct

ROOT = Path(__file__).resolve().parents[2]
market = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
assert market['name'] == 'rachael-quisel-skills'
catalog_names = {'automation-catalog', 'automation-catalog-failure-check'}
entries = [entry for entry in market['plugins'] if entry['name'] in catalog_names]
assert {entry['name'] for entry in entries} == catalog_names
names = set()
for entry in entries:
    source = entry['source']
    assert source.startswith('./') and '..' not in Path(source).parts
    package = ROOT / source
    manifest = json.loads((package / '.claude-plugin/plugin.json').read_text())
    assert manifest['name'] == entry['name']
    assert re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', entry['name'])
    assert entry['name'] not in names
    names.add(entry['name'])
    for field in ('icon', 'documentationUrl', 'supportUrl', 'privacyPolicyUrl'):
        assert field not in entry
        assert field in manifest
    for field in ('homepage', 'repository', 'documentationUrl', 'supportUrl', 'privacyPolicyUrl'):
        assert manifest[field].startswith('https://')
    for path in ('README.md', 'PRIVACY.md', 'LICENSE', 'icon.png'):
        assert (package / path).is_file()
    for host in ('plugin.json', '.codex-plugin/plugin.json'):
        other = json.loads((package / host).read_text())
        assert other['name'] == manifest['name']
        assert other['version'] == manifest['version']
    data = (package / manifest['icon']).read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    width, height, depth, color = struct.unpack('>IIBB', data[16:26])
    assert (width, height, depth, color) == (1024, 1024, 8, 6)
    assert len(data) < 768 * 1024
    offset = 8
    while offset < len(data):
        size = struct.unpack('>I', data[offset:offset+4])[0]
        tag = data[offset+4:offset+8]
        assert tag not in (b'tEXt', b'iTXt', b'zTXt', b'eXIf', b'iCCP')
        offset += 12 + size
    skills = list((package / 'skills').glob('*/SKILL.md'))
    assert skills
    for skill in skills:
        body = skill.read_text()
        assert f'name: {skill.parent.name}\n' in body
        for link in re.findall(r'\]\(([^)]+)\)', body):
            if '://' not in link:
                target = (skill.parent / link).resolve()
                assert target.is_relative_to(package.resolve()) and target.exists(), link
    for file in package.rglob('*'):
        if not file.is_file() or file.suffix not in ('.md', '.json', '.yaml', '.py'):
            continue
        body = file.read_text()
        for private_id in ('C0C7XQK3TTR', 'T0AT819U2UQ', 'link_6acb11', '6acb928d16bc'):
            assert private_id not in body, f'Private deployment setting in {file}'
    print(f"{manifest['displayName']}: package paths, metadata, icon and private-settings boundary passed")
print('Claude strict validation and installation remain unverified.')
