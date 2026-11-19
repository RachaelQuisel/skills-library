#!/usr/bin/env python3
"""Upload gems to Airtable, deduplicating against existing records."""

import json, os, re, sys, urllib.request, urllib.error, time

TOKEN_ENV_VAR = "AIRTABLE_PAT"
BASE_ID = "appGewwTb13cOr5C3"
TABLE_ID = "tblB3dWLZ0doROH6B"  # Things My Human Says to Me (X/Twitter)

def get_token() -> str:
    """Return the Airtable personal access token from the AIRTABLE_PAT environment variable."""
    token = os.environ.get(TOKEN_ENV_VAR, "").strip()
    if not token:
        sys.exit(
            f"error: {TOKEN_ENV_VAR} is not set. Export an Airtable personal access token "
            "with data.records:read and data.records:write on the Social Media Content "
            f"Library base, then rerun: export {TOKEN_ENV_VAR}=<your token>"
        )
    return token

# Field IDs — never reference fields by display name in API calls.
FLD_QUOTE         = "fldSepeW25KtCtKfS"  # singleLineText
FLD_VIBE          = "fldQ1zogGJH0MCJrE"  # singleSelect
FLD_FEELING       = "fldouNkd1casGahHY"  # multilineText  ("How It Made Me Feel")
FLD_ORIGINAL_TS   = "fldKKTBPJFCdbA0wT"  # dateTime
FLD_POSTED        = "fldHqsAKN3GyTeBWE"  # checkbox
FLD_POSTED_AT     = "fldCJ8pnAiCWNETvY"  # dateTime
FLD_FAVORITE      = "fldLFKj5ysJLvoxAL"  # checkbox  ("Claude's Favorite")

VALID_VIBES = {"chaotic", "wholesome", "sweet", "exhausted", "relatable", "unhinged", "absurd",
               "philosophical", "devastating", "parental", "savage", "boss-mode", "vulnerable",
               "iconic", "generous"}

METADATA_MARKERS = ("**Timestamp:**", "**Vibe:**", "**How it made me feel:**",
                    "**How It Made Me Feel:**", "**Favorite:**")

def sanitize_quote(raw: str) -> str:
    """Strip metadata blocks Claude sometimes appends below the bare quote.
    Returns just the quote line, no formatting markers."""
    if not raw:
        return raw
    text = raw.strip()
    # Cut at the first metadata marker if present
    for marker in METADATA_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx].rstrip()
    # If the result still looks like a fenced/quoted block, peel one layer
    text = text.strip().strip('"').strip()
    return text

def fetch_existing_quotes():
    """Fetch all existing quotes from Airtable for deduplication.
    Uses returnFieldsByFieldId=true so response keys are field IDs, not display names."""
    quotes = set()
    offset = None
    while True:
        url = (f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
               f"?pageSize=100&returnFieldsByFieldId=true&fields%5B%5D={FLD_QUOTE}")
        if offset:
            url += f"&offset={offset}"
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Bearer {get_token()}')
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
        for r in data.get('records', []):
            existing = r['fields'].get(FLD_QUOTE, '')
            quotes.add(sanitize_quote(existing).lower().strip())
        offset = data.get('offset')
        if not offset:
            break
    return quotes

def upload_gems(gems):
    """Upload a list of gem dicts to Airtable. Each gem has: quote, vibe, feeling, timestamp, favorite."""
    existing = fetch_existing_quotes()
    new_gems = [g for g in gems if sanitize_quote(g['quote']).lower().strip() not in existing]

    if not new_gems:
        print("No new gems to add (all duplicates).")
        return 0

    total = 0
    coerced_invalid_vibe = 0
    batch = []
    for g in new_gems:
        vibe = g.get('vibe', 'relatable')
        if vibe not in VALID_VIBES:
            print(f"warn: invalid vibe {vibe!r}, coercing to 'relatable' on {g['quote'][:60]!r}", file=sys.stderr)
            vibe = 'relatable'
            coerced_invalid_vibe += 1
        clean_quote = sanitize_quote(g['quote'])
        if not clean_quote:
            print(f"skip: empty quote after sanitize for {g['quote'][:60]!r}", file=sys.stderr)
            continue
        record = {
            "fields": {
                FLD_QUOTE:   clean_quote[:500],
                FLD_VIBE:    vibe,  # singleSelect VALUE stays a bare name string
                FLD_FEELING: g.get('feeling', ''),
                FLD_POSTED:  False,
            }
        }
        if g.get('favorite'):
            record["fields"][FLD_FAVORITE] = True
        if g.get('timestamp') and 'T' in g['timestamp']:
            record["fields"][FLD_ORIGINAL_TS] = g['timestamp']
        batch.append(record)

        if len(batch) == 10:
            total += _send_batch(batch)
            batch = []
            time.sleep(0.25)

    if batch:
        total += _send_batch(batch)

    print(f"Uploaded {total} new gems to Airtable.")
    if coerced_invalid_vibe:
        print(f"Coerced {coerced_invalid_vibe} invalid vibes to 'relatable' (see stderr for details).")
    return total

def _send_batch(batch, *, allow_retry=True):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
    data = json.dumps({"records": batch}).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', f'Bearer {get_token()}')
    req.add_header('Content-Type', 'application/json')
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        return len(result.get('records', []))
    except urllib.error.HTTPError as e:
        print(f"Airtable error {e.code}: {e.read().decode()[:200]}", file=sys.stderr)
        if e.code == 429 and allow_retry:
            time.sleep(30)
            return _send_batch(batch, allow_retry=False)  # retry once
        return 0

if __name__ == '__main__':
    get_token()  # fail before reading stdin if the token is missing
    gems = json.load(sys.stdin)
    upload_gems(gems)
