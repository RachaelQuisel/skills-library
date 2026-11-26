# Airtable Configuration for Gem Miner

- **Base**: Social Media Content Library
- **Base ID**: appExample0000107
- **Table**: Things My Human Says to Me
- **Table ID**: tblExample0000208
- **API Token**: not stored in this repo. `scripts/upload_gems.py` reads it from the `AIRTABLE_PAT` environment variable (placeholder: `patXXXXXXXXXXXXXX.XXXXXXXX`).

## Setting the token

1. Create a personal access token at https://airtable.com/create/tokens with the `data.records:read` and `data.records:write` scopes and access to the Social Media Content Library base.
2. Export it before running the uploader: `export AIRTABLE_PAT=patXXXXXXXXXXXXXX.XXXXXXXX`
   (or add that line to your shell profile or a local `.env` file, which `.gitignore` already excludes).
3. Never paste the token into this file or any other tracked file.

If `AIRTABLE_PAT` is missing, `upload_gems.py` stops with an error before reading any gems.

## Field IDs

The uploader writes these fields. The IDs match `scripts/upload_gems.py`.

- Quote: fldExample0000209 (singleLineText, primary field)
- Vibe: fldExample0000210 (singleSelect)
- How It Made Me Feel: fldExample0000211 (multilineText)
- Original Timestamp: fldExample0000212 (dateTime)
- Posted: fldExample0000213 (checkbox)
- Claude's Favorite: fldExample0000214 (checkbox, heart icon)

Defined in the script, not written by the uploader:

- Posted At: fldExample0000215 (dateTime)

Present in the base, not used by the script:

- Post Date: fldExample0000216 (date)

## Vibe Options
chaotic, wholesome, sweet, exhausted, relatable, unhinged, absurd, philosophical, devastating, parental, savage, boss-mode, vulnerable, iconic, generous
