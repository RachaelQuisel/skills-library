import json
import re
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / 'plugins' / 'skillkeeper'


def test_skillkeeper_manifest_and_marketplace_agree():
    manifest = json.loads((PLUGIN / '.claude-plugin' / 'plugin.json').read_text())
    marketplace = json.loads((ROOT / '.claude-plugin' / 'marketplace.json').read_text())
    entry = next(item for item in marketplace['plugins'] if item['name'] == 'skillkeeper')

    assert manifest['name'] == entry['name']
    assert re.fullmatch(r'\d+\.\d+\.\d+', manifest['version'])
    assert manifest['license'] == 'UNLICENSED'
    assert manifest['icon'] == './icon.png'
    assert entry['source'] == './plugins/skillkeeper'


def test_skillkeeper_package_has_instructions_and_disclosures():
    skill = PLUGIN / 'skills' / 'skillkeeper' / 'SKILL.md'
    required = [PLUGIN / 'README.md', PLUGIN / 'PRIVACY.md', PLUGIN / 'LICENSE', skill]

    assert all(path.is_file() for path in required)
    text = skill.read_text()
    assert text.startswith('---\n')
    assert '\nname: skillkeeper\n' in text
    assert 'Do not invent a root cause.' in text


def test_skillkeeper_icon_matches_directory_preflight_limits():
    data = (PLUGIN / 'icon.png').read_bytes()

    assert data.startswith(b'\x89PNG\r\n\x1a\n')
    assert struct.unpack('>II', data[16:24]) == (1024, 1024)
    assert len(data) < 768 * 1024
