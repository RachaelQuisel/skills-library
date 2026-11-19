#!/usr/bin/env python3
"""Enrich raw_schema.json with rollup/lookup filter conditions.

Why this exists: the public Metadata API (and the Airtable MCP's describe_table)
return a rollup's link field, target field, and aggregation formula — but NOT the
*filter* applied to it. That omission is not cosmetic. A base can carry four
rollups that are byte-identical at the public API level and differ only by a
hidden condition, e.g. four "does this consultant hold clearance X?" rollups that
all roll up Clearances.Is Valid and are distinguished purely by a Type filter.
Without the filter, an audit renders them as four duplicates and a reader
reasonably concludes the schema is redundant when it isn't.

The internal readForWorkflows schema DOES expose them, at
  columns[].typeOptions.filters = {filterSet:[{columnId, operator, value}], conjunction}

This script merges those filters into raw_schema.json as a pre-rendered human
string at options.conditionsRendered, which build_audit.py appends to the field's
Notes cell. Values that are select-option IDs (selXXX) are resolved to their
labels using the internal schema's own choice definitions.

Usage:
    python merge_internal_options.py \
        --raw airtable_schema_audit/raw_schema.json \
        --internal airtable_audit/describes_workflows.json

Safe to skip: if you have no internal schema capture (i.e. you didn't run the
automations audit), the schema audit still builds — it just won't show conditions.
"""
import argparse
import json
from pathlib import Path


def load_maybe_double(path):
    """readForWorkflows captures are often JSON-encoded strings, sometimes twice."""
    d = json.loads(Path(path).read_text())
    while isinstance(d, str):
        d = json.loads(d)
    return d


def build_maps(tables):
    """field id -> name, and field id -> {choiceId: choiceLabel}."""
    fname, choices = {}, {}
    for t in tables:
        for c in t.get("columns") or []:
            fname[c["id"]] = c["name"]
            cs = ((c.get("typeOptions") or {}).get("choices")) or {}
            if isinstance(cs, dict) and cs:
                choices[c["id"]] = {k: (v or {}).get("name") for k, v in cs.items()}
    return fname, choices


# Unary operators carry value:null — rendering "= None" for them would be wrong.
UNARY = {"isEmpty", "isNotEmpty", "isAnyOf", "isNoneOf", "isChecked", "isNotChecked"}


def render_value(col_id, val, choices):
    if isinstance(val, str) and val.startswith("sel"):
        return choices.get(col_id, {}).get(val, val)
    if isinstance(val, list):
        return ", ".join(render_value(col_id, v, choices) for v in val)
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, dict):
        # date-relative filters, linked-record specs, etc.
        return val.get("mode") or json.dumps(val, sort_keys=True)[:60]
    return str(val)


def render_filters(f, fname, choices):
    if not isinstance(f, dict) or not isinstance(f.get("filterSet"), list):
        return None
    conj = f" {(f.get('conjunction') or 'and').upper()} "
    parts = []
    for c in f["filterSet"]:
        if not isinstance(c, dict):
            continue
        if isinstance(c.get("filterSet"), list):  # nested group
            inner = render_filters(c, fname, choices)
            if inner:
                parts.append(f"({inner})")
            continue
        col = c.get("columnId")
        label = fname.get(col, col or "?")
        op = c.get("operator") or "="
        if op in UNARY or c.get("value") is None:
            parts.append(f"{label} {op}")
        else:
            parts.append(f"{label} {op} {render_value(col, c['value'], choices)}")
    return conj.join(parts) if parts else None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", required=True, help="raw_schema.json to enrich in place")
    ap.add_argument("--internal", required=True,
                    help="describes_workflows.json (internal readForWorkflows capture)")
    args = ap.parse_args()

    internal = load_maybe_double(args.internal)
    tables = internal["data"]["tableSchemas"]
    fname, choices = build_maps(tables)

    # field id -> rendered condition, for every rollup/lookup that has one
    conditions = {}
    for t in tables:
        for c in t.get("columns") or []:
            filt = (c.get("typeOptions") or {}).get("filters")
            rendered = render_filters(filt, fname, choices)
            if rendered:
                conditions[c["id"]] = rendered

    raw_path = Path(args.raw)
    raw = json.loads(raw_path.read_text())
    applied = 0
    for t in raw:
        for f in t.get("fields") or []:
            if f["id"] in conditions:
                f.setdefault("options", {})["conditionsRendered"] = conditions[f["id"]]
                applied += 1

    raw_path.write_text(json.dumps(raw, indent=1))
    print(f"found {len(conditions)} conditional field(s) in the internal schema; "
          f"applied {applied} to {raw_path}")
    for fid, cond in sorted(conditions.items(), key=lambda kv: fname.get(kv[0], "")):
        print(f"  {fname.get(fid, fid)}: {cond}")


if __name__ == "__main__":
    main()
