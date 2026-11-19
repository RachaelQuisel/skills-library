#!/usr/bin/env python3
"""Build the Softr app audit document.

Input:
  --raw  softr_audit/raw_pages.json
         List of full page objects from
         https://studio-api.softr.io/v1/applications/{appId}/pages/{pageId}

Outputs:
  --out                softr_audit.md   (the audit doc)
  --field-index-out    field_usage_by_table.json
  --page-index-out     page_index.json

Optional:
  --schema-audit-rel   relative path to airtable_schema_audit/schema_audit.md
                       for cross-referencing field/table headings.
"""
import argparse
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path


def slug(s: str) -> str:
    """GitHub-style anchor slug."""
    s = (s or "").lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    return s


def safe_json(maybe_str, default=None):
    if maybe_str is None:
        return default if default is not None else {}
    if isinstance(maybe_str, (dict, list)):
        return maybe_str
    if isinstance(maybe_str, str):
        s = maybe_str.strip()
        if not s or s == "{}":
            return default if default is not None else {}
        try:
            return json.loads(s)
        except Exception:
            return default if default is not None else {}
    return default if default is not None else {}


# ---------------------------------------------------------------------------
# Block extraction
# ---------------------------------------------------------------------------

def extract_list_or_detail_fields(elements):
    """Returns [{label, field}] for list/list-details blocks where
    elements.fields.items[*].field.mappedTo holds the Airtable field name."""
    out = []
    items = (elements.get("fields") or {}).get("items") or []
    for it in items:
        f = it.get("field") or {}
        mapped = f.get("mappedTo")
        if mapped:
            out.append({
                "label": (it.get("label") or {}).get("value") or "",
                "field": mapped,
                "type": f.get("type"),
            })
    return out


def extract_form_fields(elements):
    """Returns [{step, section, name, type, label, required, hidden}] for
    conditionalForm / form blocks. The Airtable field name lives in field.name
    (decorative items have name == '')."""
    out = []
    form = elements.get("form") or {}
    for step in form.get("steps") or []:
        step_name = step.get("name") or step.get("id")
        for section in step.get("sections") or []:
            section_name = section.get("name") or section.get("id")
            for f in section.get("fields") or []:
                name = (f.get("name") or "").strip()
                ftype = f.get("type")
                # Skip decorative-only fields with no Airtable mapping
                if not name and ftype in {"heading1", "heading2", "heading3", "text", "divider", "image"}:
                    continue
                out.append({
                    "step": step_name,
                    "section": section_name,
                    "name": name,
                    "type": ftype,
                    "label": (f.get("label") or {}).get("value") or "",
                    "required": bool(f.get("isRequired")),
                    "hidden": ftype == "hidden",
                })
    return out


def extract_form_branching(elements):
    """Returns [{from_step, to_step, expressions}] capturing step routing."""
    out = []
    form = elements.get("form") or {}
    steps_by_id = {s.get("id"): s.get("name") or s.get("id") for s in (form.get("steps") or [])}
    for step in form.get("steps") or []:
        from_step = step.get("name") or step.get("id")
        for cond in step.get("conditions") or []:
            target = cond.get("targetStep")
            target_name = steps_by_id.get(target, target)
            exprs = []
            for e in cond.get("expressions") or []:
                subj = (e.get("subject") or {}).get("field") or "(unknown)"
                # Form answers look like "FORM_ANSWER:::step1:::<uuid>" — leave as-is
                exprs.append(f"{subj} {e.get('operator')} {json.dumps(e.get('value'))}")
            out.append({
                "from_step": from_step,
                "to_step": target_name,
                "logical": cond.get("logicalOperator", "AND"),
                "expressions": exprs,
            })
    return out


def extract_actions(collection):
    """Returns [{type, fields, destination, button_label}] for collection.actions."""
    out = []
    for a in collection.get("actions") or []:
        atype = a.get("type")
        if not atype:
            continue
        entry = {"type": atype, "id": a.get("id")}
        if atype == "UPDATE_RECORD" or atype == "CREATE_RECORD":
            entry["fields"] = [
                f.get("mappedTo") for f in (a.get("fields") or []) if f.get("mappedTo")
            ]
        # OPEN_PAGE destination lives in the action's options when present,
        # but for record actions it's also in elements.recordActions[].options.
        out.append(entry)
    return out


def extract_open_page_destinations(elements):
    """Look up OPEN_PAGE destinations from elements.recordActions[*].options.destination."""
    dests = {}
    ra = (elements.get("recordActions") or {}).get("items") or []
    for item in ra:
        if item.get("action") == "OPEN_PAGE":
            opts = item.get("options") or {}
            dest = opts.get("destination")
            label = (item.get("button") or {}).get("label")
            if dest:
                dests.setdefault(dest, []).append(label or "(button)")
    return dests


def extract_restrictions(collection):
    """Returns list of human-readable restriction strings from collection.condition."""
    out = []
    cond = collection.get("condition") or {}
    logical = cond.get("logicalOperator") or "AND"
    for e in cond.get("expressions") or []:
        field = (e.get("subject") or {}).get("field") or (e.get("subject") or {}).get("type")
        op = e.get("operator")
        val = e.get("value")
        out.append({"field": field, "operator": op, "value": val, "logical": logical})
    return out


def parse_block(b):
    """Return a normalised block summary, or None if the block has no Airtable footprint."""
    btype = b.get("type")
    if btype != "dynamic":
        return None
    coll = safe_json(b.get("collection"))
    elems = safe_json(b.get("elements"))
    if not coll:
        return None

    ds = coll.get("dataSource") or {}
    at = ds.get("airtable") or {}
    # Some blocks (forms) leave dataSource.airtable empty but populate collection.dataSources
    sources = coll.get("dataSources") or []
    primary_source = None
    if at.get("baseId") and at.get("tableName"):
        primary_source = {
            "base": at.get("baseId"),
            "table": at.get("tableName"),
            "view": at.get("viewName") or "",
        }
    elif sources:
        keys = (sources[0].get("resourceIdentifier") or {}).get("keys") or {}
        primary_source = {
            "base": keys.get("base"),
            "table": keys.get("table"),
            "view": keys.get("view") or "",
        }

    all_sources = []
    for s in sources:
        keys = (s.get("resourceIdentifier") or {}).get("keys") or {}
        all_sources.append({
            "base": keys.get("base"),
            "table": keys.get("table"),
            "view": keys.get("view") or "",
        })

    # `onboarding` blocks carry the same elements.form.steps[] shape as conditionalForm
    # but don't match on the word "form", so they were previously parsed as read-only
    # list blocks and their (often large) write surface was silently dropped.
    bname = (b.get("name") or "").lower()
    is_form = (
        b.get("name") in {"conditionalForm", "form3", "form2", "form1", "onboarding"}
        or "form" in bname
        or bool((elems.get("form") or {}).get("steps"))
    )

    return {
        "block_id": b.get("id"),
        "block_name": b.get("name"),
        "hrid": b.get("hrid"),
        "is_form": is_form,
        "source": primary_source,
        "all_sources": all_sources,
        "sort": [
            f"{s.get('field')} {s.get('direction')}"
            for s in (coll.get("sortOptions") or [])
        ],
        "search": (coll.get("searchOptions") or {}).get("fields") or [],
        "restrictions": extract_restrictions(coll),
        "read_fields": extract_list_or_detail_fields(elems),
        "form_fields": extract_form_fields(elems) if is_form else [],
        "form_branching": extract_form_branching(elems) if is_form else [],
        "actions": extract_actions(coll),
        "open_page_destinations": extract_open_page_destinations(elems),
    }


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def normalise(pages):
    out = []
    for p in pages:
        blocks = (p.get("page_payload") or {}).get("blocks") or []
        parsed = [parse_block(b) for b in blocks]
        parsed = [b for b in parsed if b]
        out.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "path": p.get("path"),
            "enabled": p.get("enabled"),
            "permissions": (p.get("page_payload") or {}).get("permissions"),
            "blocks": parsed,
        })
    return out


def build_field_index(pages):
    """Returns {table: {field: {reads:set, writes:set, searches:set,
    sorts:set, restricts:set, form_writes:set}}}."""
    idx = defaultdict(lambda: defaultdict(lambda: {
        "reads": set(), "writes": set(), "searches": set(),
        "sorts": set(), "restricts": set(), "form_writes": set(),
    }))
    for p in pages:
        page_label = f"{p['name']} (`{p['path']}`)"
        for b in p["blocks"]:
            src = b["source"] or {}
            table = src.get("table")
            if not table:
                # form may write to multiple sources via all_sources
                for s in b["all_sources"]:
                    if s.get("table"):
                        table = s["table"]
                        break
            if not table:
                continue

            # Reads (list/detail field display)
            for rf in b["read_fields"]:
                idx[table][rf["field"]]["reads"].add(page_label)
            # Searches & sorts
            for sf in b["search"]:
                idx[table][sf]["searches"].add(page_label)
            for srt in b["sort"]:
                fname = srt.rsplit(" ", 1)[0]
                idx[table][fname]["sorts"].add(f"{page_label} ({srt.rsplit(' ',1)[-1]})")
            # Restrictions
            for r in b["restrictions"]:
                if r.get("field"):
                    idx[table][r["field"]]["restricts"].add(
                        f"{page_label}: {r['operator']} {json.dumps(r['value'])}"
                    )
            # UPDATE_RECORD / CREATE_RECORD button writes
            for a in b["actions"]:
                if a["type"] in {"UPDATE_RECORD", "CREATE_RECORD"}:
                    for fname in a.get("fields") or []:
                        idx[table][fname]["writes"].add(page_label)
            # Form field writes — these may target a different table than `source`
            if b["is_form"]:
                # Form writes go to the first dataSource (forms typically have one)
                form_table = (b["all_sources"][0] or {}).get("table") if b["all_sources"] else table
                for ff in b["form_fields"]:
                    if ff["name"]:
                        idx[form_table][ff["name"]]["form_writes"].add(page_label)

    # Convert sets to sorted lists for JSON
    out = {}
    for table, fields in idx.items():
        out[table] = {}
        for fname, usage in fields.items():
            out[table][fname] = {k: sorted(v) for k, v in usage.items()}
    return out


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def td(s):
    """Escape a value for a markdown table cell. Airtable field names legitimately
    contain pipes (e.g. `Grants | Funding Request`), which silently break the row."""
    if s is None:
        return ""
    return str(s).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def render_md(pages, field_index, schema_audit_rel=None,
              app_name="Softr App", app_id=None):
    today = date.today().isoformat()
    # Summary
    tables_touched = sorted(field_index.keys())
    dynamic_blocks = sum(len(p["blocks"]) for p in pages)
    form_blocks = sum(1 for p in pages for b in p["blocks"] if b["is_form"])
    enabled = sum(1 for p in pages if p["enabled"])
    disabled = len(pages) - enabled

    lines = []
    lines.append(f"# {app_name} — Softr Audit")
    lines.append("")
    lines.append(f"_Generated {today}_")
    lines.append("")
    if app_id:
        lines.append(f"**App:** [`{app_id}`](https://studio.softr.io/applications/{app_id})")
        lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Pages:** {len(pages)}  ({enabled} enabled, {disabled} disabled)")
    lines.append(f"- **Dynamic blocks:** {dynamic_blocks}  ({form_blocks} forms)")
    lines.append(f"- **Airtable tables touched:** {len(tables_touched)}")
    lines.append("")
    if schema_audit_rel:
        lines.append(f"_Field/table names link to [`{schema_audit_rel}`]({schema_audit_rel})._")
        lines.append("")

    # Page index
    lines.append("## Page Index")
    lines.append("")
    lines.append("| Page | Path | Status | Blocks | Tables touched |")
    lines.append("|---|---|---|---|---|")
    for p in sorted(pages, key=lambda x: x["path"]):
        tables = sorted({b["source"]["table"] for b in p["blocks"] if b.get("source") and b["source"].get("table")} |
                        {s["table"] for b in p["blocks"] for s in b["all_sources"] if s.get("table")})
        status = "enabled" if p["enabled"] else "_disabled_"
        block_summary = ", ".join(
            (f"{b['block_name']}" + ("*" if b['is_form'] else ""))
            for b in p["blocks"]
        ) or "—"
        anchor = slug(f"{p['name']} {p['path']}")
        lines.append(f"| [{td(p['name'])}](#{anchor}) | `{td(p['path'])}` | {status} | "
                     f"{td(block_summary)} | {td(', '.join(tables)) or '—'} |")
    lines.append("")
    lines.append("_* = form block_")
    lines.append("")

    # Field-level audit per table
    lines.append("## Field-Level Audit (per Airtable table)")
    lines.append("")
    for table in tables_touched:
        if schema_audit_rel:
            table_link = f"{schema_audit_rel}#{slug(table)}"
            lines.append(f"### [{table}]({table_link})")
        else:
            lines.append(f"### {table}")
        lines.append("")

        # Views observed
        views = set()
        for p in pages:
            for b in p["blocks"]:
                for s in [b.get("source")] + b.get("all_sources", []):
                    if s and s.get("table") == table and s.get("view"):
                        views.add(s["view"])
        if views:
            lines.append("**Views used:** " + ", ".join(f"`{v}`" for v in sorted(views)))
            lines.append("")

        fields = field_index.get(table, {})
        if not fields:
            lines.append("_No fields touched._")
            lines.append("")
            continue
        lines.append("| Field | Read on | Written on | Search / Sort / Restrict |")
        lines.append("|---|---|---|---|")
        for fname in sorted(fields.keys(), key=lambda x: x.lower()):
            u = fields[fname]
            reads = "<br>".join(u["reads"]) or "—"
            writes_parts = []
            if u["writes"]:
                writes_parts += [f"{w} (button)" for w in u["writes"]]
            if u["form_writes"]:
                writes_parts += [f"{w} (form)" for w in u["form_writes"]]
            writes = "<br>".join(writes_parts) or "—"
            meta_parts = []
            if u["searches"]:
                meta_parts.append("**search:** " + "; ".join(u["searches"]))
            if u["sorts"]:
                meta_parts.append("**sort:** " + "; ".join(u["sorts"]))
            if u["restricts"]:
                meta_parts.append("**restrict:** " + "; ".join(u["restricts"]))
            meta = "<br>".join(meta_parts) or "—"
            lines.append(f"| `{td(fname)}` | {td(reads)} | {td(writes)} | {td(meta)} |")
        lines.append("")

    # Per-page breakdown
    lines.append("## Per-Page Breakdown")
    lines.append("")
    for p in sorted(pages, key=lambda x: x["path"]):
        anchor = slug(f"{p['name']} {p['path']}")
        status = "enabled" if p["enabled"] else "_disabled_"
        lines.append(f"### {p['name']}  ·  `{p['path']}`  ·  {status}")
        lines.append("")
        if not p["blocks"]:
            lines.append("_No dynamic blocks._")
            lines.append("")
            continue
        for b in p["blocks"]:
            src = b["source"] or {}
            kind = "form" if b["is_form"] else "list/detail"
            src_str = f"{src.get('table','?')}" + (f" · view `{src['view']}`" if src.get("view") else "")
            lines.append(f"**`{b['block_name']}`** ({kind}) — {src_str}")
            lines.append("")
            if b["sort"]:
                lines.append(f"- **Sort:** {', '.join(b['sort'])}")
            if b["search"]:
                lines.append(f"- **Search fields:** {', '.join(f'`{x}`' for x in b['search'])}")
            if b["restrictions"]:
                rstrs = []
                for r in b["restrictions"]:
                    rstrs.append(f"`{r['field']}` {r['operator']} {json.dumps(r['value'])}")
                joiner = f" {b['restrictions'][0].get('logical','AND')} "
                lines.append(f"- **Restriction (Softr-side):** {joiner.join(rstrs)}")
            if b["read_fields"]:
                names = ", ".join("`" + rf["field"] + "`" for rf in b["read_fields"])
                lines.append(f"- **Fields displayed:** {names}")
            if b["form_fields"]:
                lines.append(f"- **Form fields ({len(b['form_fields'])}):**")
                for ff in b["form_fields"]:
                    req = " *(required)*" if ff["required"] else ""
                    hid = " *(hidden)*" if ff["hidden"] else ""
                    lines.append(f"  - `{ff['name']}` — {ff['type']}{req}{hid} — _\"{ff['label'][:80]}\"_  · {ff['step']} / {ff['section']}")
            if b["form_branching"]:
                lines.append(f"- **Form branching:**")
                for br in b["form_branching"]:
                    if br["expressions"]:
                        lines.append(f"  - {br['from_step']} → {br['to_step']} when {(' '+br['logical']+' ').join(br['expressions'])}")
                    else:
                        lines.append(f"  - {br['from_step']} → {br['to_step']} _(default)_")
            for a in b["actions"]:
                if a["type"] in {"UPDATE_RECORD", "CREATE_RECORD"} and a.get("fields"):
                    lines.append(f"- **{a['type']} action:** writes {', '.join(f'`{x}`' for x in a['fields'])}")
            if b["open_page_destinations"]:
                dests = ", ".join(f"`{d}` ({', '.join(labels)})" for d, labels in b["open_page_destinations"].items())
                lines.append(f"- **OPEN_PAGE actions:** {dests}")
            lines.append("")
        lines.append("")
    return "\n".join(lines)


def build_page_index(pages):
    """Slim per-page summary."""
    out = []
    for p in pages:
        out.append({
            "id": p["id"],
            "name": p["name"],
            "path": p["path"],
            "enabled": p["enabled"],
            "block_count": len(p["blocks"]),
            "form_count": sum(1 for b in p["blocks"] if b["is_form"]),
            "tables": sorted({s["table"] for b in p["blocks"] for s in [b.get("source")] + b.get("all_sources", []) if s and s.get("table")}),
        })
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--field-index-out", required=True)
    ap.add_argument("--page-index-out", required=True)
    ap.add_argument("--schema-audit-rel", default=None,
                    help="Relative path to airtable_schema_audit/schema_audit.md")
    ap.add_argument("--app-name", default="Softr App",
                    help="Human-readable app name for the document title")
    ap.add_argument("--app-id", default=None,
                    help="Softr application UUID, rendered as a studio link")
    args = ap.parse_args()

    pages_raw = json.loads(Path(args.raw).read_text())
    # evaluate_script(filePath=…) can save a JSON-encoded string; peel until it's a list.
    while isinstance(pages_raw, str):
        pages_raw = json.loads(pages_raw)
    pages = normalise(pages_raw)
    field_index = build_field_index(pages)
    page_index = build_page_index(pages)
    md = render_md(pages, field_index, schema_audit_rel=args.schema_audit_rel,
                   app_name=args.app_name, app_id=args.app_id)
    Path(args.out).write_text(md)
    Path(args.field_index_out).write_text(json.dumps(field_index, indent=2, sort_keys=True))
    Path(args.page_index_out).write_text(json.dumps(page_index, indent=2, sort_keys=True))
    print(f"Wrote {args.out}, {args.field_index_out}, {args.page_index_out}")


if __name__ == "__main__":
    main()
