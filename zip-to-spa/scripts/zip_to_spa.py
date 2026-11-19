"""Look up the Los Angeles County Service Planning Area for one or more zip codes.

Uses LA County's public ArcGIS layers. No API key.

CLI:
    python zip_to_spa.py 90001 90292 90815
    python zip_to_spa.py --csv out.csv 90001 90292 90815

Module:
    from zip_to_spa import lookup, lookup_many
    row = lookup("90001")
    rows = lookup_many(["90001", "90292"])
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.parse
import urllib.request
from typing import Iterable

from shapely.geometry import Polygon, MultiPolygon


ZIP_LAYER = "https://arcgis.gis.lacounty.gov/arcgis/rest/services/LACounty_Dynamic/Administrative_Boundaries/MapServer/5/query"
SPA_LAYER = "https://arcgis.gis.lacounty.gov/arcgis/rest/services/LACounty_Dynamic/Administrative_Boundaries/MapServer/23/query"
MIN_OVERLAP_FRACTION = 0.01


def _post(url: str, params: dict) -> dict:
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def _rings_to_shape(rings):
    polys = []
    for ring in rings:
        if len(ring) < 4:
            continue
        try:
            poly = Polygon(ring)
            if not poly.is_valid:
                poly = poly.buffer(0)
            polys.append(poly)
        except Exception:
            continue
    if not polys:
        return None
    if len(polys) == 1:
        return polys[0]
    return MultiPolygon(polys)


_SPA_CACHE: list[tuple[int, str, object]] | None = None


def _spa_polygons():
    global _SPA_CACHE
    if _SPA_CACHE is not None:
        return _SPA_CACHE
    data = _post(SPA_LAYER, {
        "where": "1=1",
        "outFields": "SPA_NUM,SPA_NAME",
        "returnGeometry": "true",
        "f": "json",
    })
    out = []
    for feat in data.get("features", []):
        n = feat["attributes"].get("SPA_NUM")
        name = feat["attributes"].get("SPA_NAME", "")
        shape = _rings_to_shape(feat["geometry"]["rings"])
        if n is None or shape is None:
            continue
        if not shape.is_valid:
            shape = shape.buffer(0)
        out.append((int(n), name, shape))
    _SPA_CACHE = out
    return out


def _normalize(z) -> str | None:
    if z is None:
        return None
    s = str(z).strip()
    if len(s) >= 5 and s[:5].isdigit():
        return s[:5]
    return None


def lookup(zip_code: str) -> dict:
    """Return the Service Planning Area for one zip. Fields: zip, spa, spa_name, source, overlap_pct, note."""
    z = _normalize(zip_code)
    if not z:
        return {"zip": str(zip_code), "spa": "", "spa_name": "",
                "source": "unresolved", "overlap_pct": "",
                "note": "zip did not read as 5 digits"}
    zq = _post(ZIP_LAYER, {
        "where": f"ZIPCODE='{z}'",
        "outFields": "ZIPCODE",
        "returnGeometry": "true",
        "f": "json",
    })
    feats = zq.get("features", [])
    if not feats:
        return {"zip": z, "spa": "", "spa_name": "",
                "source": "unresolved", "overlap_pct": "",
                "note": "zip polygon not in LA County layer"}
    shape = _rings_to_shape(feats[0]["geometry"]["rings"])
    if shape is None:
        return {"zip": z, "spa": "", "spa_name": "",
                "source": "unresolved", "overlap_pct": "",
                "note": "zip polygon could not be parsed"}
    if not shape.is_valid:
        shape = shape.buffer(0)
    total = shape.area or 1.0
    best = (None, "", 0.0)
    for num, name, poly in _spa_polygons():
        inter = shape.intersection(poly).area
        if inter > best[2]:
            best = (num, name, inter)
    if best[0] is None or best[2] / total < MIN_OVERLAP_FRACTION:
        return {"zip": z, "spa": "", "spa_name": "",
                "source": "unresolved", "overlap_pct": "",
                "note": f"no SPA overlaps > {MIN_OVERLAP_FRACTION * 100:.0f}%"}
    pct = round(100.0 * best[2] / total, 1)
    return {"zip": z, "spa": best[0], "spa_name": best[1],
            "source": "dcfs-gis", "overlap_pct": pct, "note": ""}


def lookup_many(zip_codes: Iterable[str]) -> list[dict]:
    return [lookup(z) for z in zip_codes]


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("zips", nargs="+", help="One or more zip codes")
    parser.add_argument("--csv", help="Write results to this CSV path instead of printing JSON lines")
    args = parser.parse_args()

    rows = lookup_many(args.zips)

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["zip", "spa", "spa_name", "source", "overlap_pct", "note"])
            w.writeheader()
            for r in rows:
                w.writerow(r)
        print(f"Wrote {len(rows)} rows to {args.csv}")
    else:
        for r in rows:
            print(json.dumps(r))


if __name__ == "__main__":
    _main()
