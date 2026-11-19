---
name: zip-to-spa
description: Look up the Los Angeles County Service Planning Area for one zip or a list of zips, using the LA County public GIS layers. Use when the user asks "what SPA is zip X in", needs to backfill or verify a SPA field on Applications or caregivers, is mapping GoL or DCFS case locations, or needs the Service Planning Area for any LA County address. Returns the Service Planning Area number 1 through 8 and the SPA name, with provenance set to `dcfs-gis`.
---

# Zip to SPA

Resolves a US zip code to its Los Angeles County Service Planning Area (1 through 8), using LA County's public GIS services. No API key needed. For GoL in particular this covers every case location in Service Planning Areas 1 through 8.

## When to invoke

- Rachael asks "what SPA is zip X in" or "what's the Service Planning Area for 90001."
- A client build needs a SPA field populated and the base already carries zip codes.
- A diagnostic session needs to confirm whether a specific address is inside Service Planning Area 5, 6, or 8.
- Any backfill, migration, or dashboard that needs zip → Service Planning Area.

## When NOT to invoke

- The address is outside Los Angeles County. LA County GIS has no polygon for Riverside, San Bernardino, Kern, Orange, or Ventura zips. The script flags them as `unresolved`.
- The source already carries SPA (treat the existing value as the source of truth; this skill is for empty SPA fields).

## How it works

Two public ArcGIS layers:

- Zipcodes (layer 5 on the LA County Administrative Boundaries MapServer)
- Service Planning Areas 2022 (layer 23 on the same MapServer)

For each zip:

1. Query the Zipcodes layer for the polygon matching `ZIPCODE='<zip>'`.
2. If no polygon is returned, mark the zip `unresolved` with the note "zip polygon not in LA County layer."
3. Query the SPA 2022 layer with the zip's polygon as the spatial filter.
4. Pick the SPA whose area overlaps the most with the zip polygon. Shapely does the overlap math.
5. If no SPA overlaps by more than one percent of the zip's area, mark it `unresolved` with the note "no SPA overlaps > 1%."

The overlap decision is a ratio and is not affected by Web Mercator area distortion.

## How to use

The script at `scripts/zip_to_spa.py` runs as either a one-off CLI or an importable module.

### CLI

```
python ~/.claude/skills/zip-to-spa/scripts/zip_to_spa.py 90001 90292 90815
```

Prints one JSON object per zip to stdout:

```
{"zip":"90001","spa":6,"spa_name":"South","source":"dcfs-gis","overlap_pct":100.0,"note":""}
{"zip":"90292","spa":5,"spa_name":"West","source":"dcfs-gis","overlap_pct":100.0,"note":""}
```

### Import

```python
from scripts.zip_to_spa import lookup, lookup_many

row = lookup("90001")
# {"zip": "90001", "spa": 6, "spa_name": "South", "source": "dcfs-gis", "overlap_pct": 100.0, "note": ""}

rows = lookup_many(["90001", "90292", "90815"])
# [{"zip": "90001", ...}, ...]
```

### CSV output

Pass `--csv <path>` to write results to a CSV instead of stdout:

```
python zip_to_spa.py --csv out.csv 90001 90292 90815
```

Columns: `zip, spa, spa_name, source, overlap_pct, note`.

## Dependencies

- Python 3.10 or later for `str | None` syntax.
- `shapely` for the polygon overlap math. Install once with `pip install shapely`.
- `requests` or `urllib` from the standard library (the script uses `urllib`).

## What it returns per zip

- `zip`: the five-digit zip the lookup used
- `spa`: integer 1 through 8, or empty string on `unresolved`
- `spa_name`: Antelope Valley, San Fernando Valley, San Gabriel Valley, Metro, West, South, East, South Bay
- `source`: always `dcfs-gis` for a successful lookup, `unresolved` otherwise
- `overlap_pct`: percent of the zip's area that falls inside the chosen SPA
- `note`: empty on success, explains why on `unresolved`

## Known shape

- A zip that straddles two SPAs is assigned to the SPA with the largest overlap.
- A zip's polygon can be a multi-ring shape (a donut). The script treats each ring as its own polygon. The decision is still correct because it is a ratio over the same zip.
- Zips outside LA County return no polygon from the Zipcodes layer. They are marked `unresolved`, not misassigned.

## Shipping discipline

The caller is responsible for writing to the base. This skill never writes to Airtable, Zapier, or any client system. It reads from LA County's public GIS layers only.

## Related

- The one-off backfill that first used this logic: `~/Claude-Work/CLIENTS/Guardians_of_Love_Jessica_Peoples/Automations/zip-spa-backfill-2026-10-26/`
- The LA County SPA 2022 ArcGIS layer: https://arcgis.gis.lacounty.gov/arcgis/rest/services/LACounty_Dynamic/Administrative_Boundaries/MapServer/23
- The LA County Zipcodes layer: https://arcgis.gis.lacounty.gov/arcgis/rest/services/LACounty_Dynamic/Administrative_Boundaries/MapServer/5
