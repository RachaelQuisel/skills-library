#!/usr/bin/env python3
"""Build the Airtable schema audit document and Mermaid ERD.

Inputs:
  --raw     airtable_schema_audit/raw_schema.json
            list of full table objects from mcp__airtable__describe_table
  --drafts  airtable_schema_audit/description_drafts.json (optional)
            {tableId: {fieldId: "draft", "__table__": "table draft"}}

Outputs:
  --out      schema_audit.md  (with embedded Mermaid ERD)
  --erd-out  erd.mmd          (standalone diagram)
"""
import argparse
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

AI_TAG = " _(AI-drafted)_"
FORMULA_REF_RE = re.compile(r"\{([^{}]+)\}")
FIELD_ID_RE = re.compile(r"^fld[A-Za-z0-9]{14}$")


# ---------------------------------------------------------------------------
# Load + index
# ---------------------------------------------------------------------------

def load_inputs(raw_path, drafts_path):
    raw = json.loads(Path(raw_path).read_text())
    if isinstance(raw, dict) and "tables" in raw:
        raw = raw["tables"]
    drafts = {}
    if drafts_path and Path(drafts_path).exists():
        drafts = json.loads(Path(drafts_path).read_text())
    return raw, drafts


def build_indices(tables):
    by_tid = {t["id"]: t for t in tables}
    field_by_id = {}
    field_by_name = {}
    field_id_to_table = {}  # fid -> tid (for resolving cross-table refs in formulas)
    for t in tables:
        for f in t.get("fields") or []:
            field_by_id[(t["id"], f["id"])] = f
            field_by_name[(t["id"], (f.get("name") or "").lower())] = f
            field_id_to_table[f["id"]] = t["id"]
    return by_tid, field_by_id, field_by_name, field_id_to_table


def resolve_formula_ref(ref, tid, by_tid, field_by_id, field_by_name, field_id_to_table):
    """Resolve a single {ref} from formula text.

    Returns (scope, label) where scope is one of:
      "in-table"   – resolved to a field in this table; label is the field name
      "cross-table" – resolved to a field in another table; label is "Table.Field"
      "unresolved" – no match; label is the raw ref string

    Airtable formulas may contain either {Field Name} or {fldXXX} — both forms are
    produced by Airtable depending on how the user typed the formula. Resolve both.
    """
    # Try by name in same table first (most common case)
    if (tid, ref.lower()) in field_by_name:
        return "in-table", field_by_name[(tid, ref.lower())]["name"]

    # Try as a field ID
    if FIELD_ID_RE.match(ref):
        owner_tid = field_id_to_table.get(ref)
        if owner_tid:
            field = field_by_id.get((owner_tid, ref))
            if field:
                if owner_tid == tid:
                    return "in-table", field["name"]
                owner_name = (by_tid.get(owner_tid) or {}).get("name", "?")
                return "cross-table", f"{owner_name}.{field['name']}"

    return "unresolved", ref


def substitute_formula_ids(formula_text, tid, by_tid, field_by_id, field_id_to_table):
    """Replace {fldXXX} occurrences in a formula text with {Field Name} for display.

    Same-table refs become {Field Name}; cross-table refs become {Table.Field Name}
    so the reader can tell when a formula reaches across tables. Unknown IDs are
    left as-is.
    """
    def repl(match):
        ref = match.group(1)
        if not FIELD_ID_RE.match(ref):
            return match.group(0)  # leave {Field Name} as-is
        owner_tid = field_id_to_table.get(ref)
        if not owner_tid:
            return match.group(0)
        field = field_by_id.get((owner_tid, ref))
        if not field:
            return match.group(0)
        if owner_tid == tid:
            return "{" + field["name"] + "}"
        owner_name = (by_tid.get(owner_tid) or {}).get("name", "?")
        return "{" + owner_name + "." + field["name"] + "}"

    return FORMULA_REF_RE.sub(repl, formula_text or "")


# ---------------------------------------------------------------------------
# Descriptions (with AI-drafted tag)
# ---------------------------------------------------------------------------

def field_description(field, drafts, tid):
    existing = (field.get("description") or "").strip()
    if existing:
        return existing, False
    drafted = ((drafts.get(tid) or {}).get(field["id"]) or "").strip()
    if drafted:
        return drafted, True
    return "", False


def table_description(table, drafts):
    existing = (table.get("description") or "").strip()
    if existing:
        return existing, False
    drafted = ((drafts.get(table["id"]) or {}).get("__table__") or "").strip()
    if drafted:
        return drafted, True
    return "", False


def render_description(text, is_drafted):
    if not text:
        return ""
    return f"{text}{AI_TAG}" if is_drafted else text


# ---------------------------------------------------------------------------
# Mermaid ERD
# ---------------------------------------------------------------------------

def mermaid_id(name):
    s = re.sub(r"[^A-Za-z0-9_]", "_", name or "")
    if not s:
        s = "Table"
    if s[0].isdigit():
        s = "T_" + s
    return s


def safe_name_map(tables):
    """Map tableId -> a Mermaid-safe identifier, disambiguating collisions."""
    base = {t["id"]: mermaid_id(t["name"]) for t in tables}
    seen = defaultdict(int)
    out = {}
    for tid, name in base.items():
        n = seen[name]
        out[tid] = name if n == 0 else f"{name}_{n}"
        seen[name] += 1
    return out


def build_erd(tables, by_tid):
    """Mermaid `erDiagram` source. Entities are name-only; each link drawn once."""
    safe = safe_name_map(tables)
    lines = ["erDiagram"]
    for t in tables:
        lines.append(f"    {safe[t['id']]} {{")
        lines.append("    }")

    drawn = set()
    edges = []
    for t in tables:
        for f in t.get("fields") or []:
            if f.get("type") != "multipleRecordLinks":
                continue
            opts = f.get("options") or {}
            tgt = opts.get("linkedTableId")
            if not tgt or tgt not in by_tid:
                continue
            inv = opts.get("inverseLinkFieldId")
            pair = frozenset({(t["id"], f["id"]), (tgt, inv)})
            if pair in drawn:
                continue
            drawn.add(pair)

            this_single = bool(opts.get("prefersSingleRecordLink"))
            inv_field = next(
                (x for x in (by_tid[tgt].get("fields") or [])
                 if x.get("id") == inv),
                None,
            )
            inv_single = bool(
                ((inv_field or {}).get("options") or {}).get("prefersSingleRecordLink")
            )
            # Cardinality: `||` = exactly-one side, `}o` = zero-or-many side.
            # "prefers single" means the field side holds at most one linked record,
            # so the OTHER side (target) is the constrained one in the relationship.
            if this_single and inv_single:
                card = "||--||"
            elif this_single and not inv_single:
                card = "}o--||"
            elif not this_single and inv_single:
                card = "||--o{"
            else:
                card = "}o--o{"
            label = (f.get("name") or "link").replace('"', "'")
            edges.append((safe[t["id"]], safe[tgt], card, label))

    edges.sort()
    for a, b, card, label in edges:
        lines.append(f'    {a} {card} {b} : "{label}"')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Cross-table dependencies
# ---------------------------------------------------------------------------

def collect_deps(tables, by_tid, field_by_id, field_by_name, field_id_to_table):
    deps = []
    for t in tables:
        tid = t["id"]
        for f in t.get("fields") or []:
            ftype = f.get("type")
            opts = f.get("options") or {}

            if ftype in ("rollup", "multipleLookupValues"):
                link_fid = opts.get("recordLinkFieldId")
                tgt_fid = opts.get("fieldIdInLinkedTable")
                link_field = field_by_id.get((tid, link_fid)) if link_fid else None
                target_tid = ((link_field or {}).get("options") or {}).get("linkedTableId")
                target_field = (
                    field_by_id.get((target_tid, tgt_fid))
                    if (target_tid and tgt_fid) else None
                )
                deps.append({
                    "kind": "rollup" if ftype == "rollup" else "lookup",
                    "table": t["name"], "table_id": tid,
                    "field": f["name"], "field_id": f["id"],
                    "link_field": (link_field or {}).get("name"),
                    "link_field_id": link_fid,
                    "target_table": (by_tid.get(target_tid) or {}).get("name"),
                    "target_table_id": target_tid,
                    "target_field": (target_field or {}).get("name"),
                    "target_field_id": tgt_fid,
                    "agg_formula": opts.get("formula") if ftype == "rollup" else None,
                    "broken": not (link_field and target_tid and target_field),
                })

            elif ftype == "count":
                link_fid = opts.get("recordLinkFieldId")
                link_field = field_by_id.get((tid, link_fid)) if link_fid else None
                target_tid = ((link_field or {}).get("options") or {}).get("linkedTableId")
                deps.append({
                    "kind": "count",
                    "table": t["name"], "table_id": tid,
                    "field": f["name"], "field_id": f["id"],
                    "link_field": (link_field or {}).get("name"),
                    "link_field_id": link_fid,
                    "target_table": (by_tid.get(target_tid) or {}).get("name"),
                    "target_table_id": target_tid,
                    "broken": not (link_field and target_tid),
                })

            elif ftype == "formula":
                formula = opts.get("formula") or ""
                # Skip pure-numeric matches — those are regex quantifiers like `{3}`
                # inside REGEX_* function calls, not field references.
                unique = sorted({
                    r for r in FORMULA_REF_RE.findall(formula)
                    if not r.isdigit()
                })
                if not unique:
                    continue
                in_table, cross_table, unresolved = [], [], []
                for r in unique:
                    scope, label = resolve_formula_ref(
                        r, tid, by_tid, field_by_id, field_by_name,
                        field_id_to_table,
                    )
                    if scope == "in-table":
                        in_table.append(label)
                    elif scope == "cross-table":
                        cross_table.append(label)
                    else:
                        unresolved.append(label)
                deps.append({
                    "kind": "formula",
                    "table": t["name"], "table_id": tid,
                    "field": f["name"], "field_id": f["id"],
                    "formula": formula,
                    "in_table_refs": sorted(set(in_table)),
                    "cross_table_refs": sorted(set(cross_table)),
                    "unresolved_refs": sorted(set(unresolved)),
                })

    return deps


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------

def md_escape(s):
    if s is None:
        return ""
    return s.replace("|", "\\|").replace("\n", " ").replace("\r", " ").strip()


def get_primary_name(table):
    """Return the primary field name.

    The Airtable MCP `describe_table` response does not include `primaryFieldId`,
    so fall back to the first field — Airtable's data model puts the primary
    field at index 0 of the fields array.
    """
    pid = table.get("primaryFieldId")
    if pid:
        for f in table.get("fields") or []:
            if f.get("id") == pid:
                return f.get("name")
    fields = table.get("fields") or []
    if fields:
        return fields[0].get("name")
    return None


def field_notes(field, table, by_tid, field_by_id, field_id_to_table):
    """Notes column content for a single field row (resolves IDs → names)."""
    ftype = field.get("type")
    opts = field.get("options") or {}
    bits = []

    if ftype in ("singleSelect", "multipleSelects"):
        choices = [c.get("name") for c in (opts.get("choices") or []) if c.get("name")]
        if choices:
            preview = ", ".join(f"`{c}`" for c in choices[:8])
            extra = f" _(+{len(choices) - 8} more)_" if len(choices) > 8 else ""
            bits.append(f"choices: {preview}{extra}")

    elif ftype == "formula":
        text = (opts.get("formula") or "").strip()
        if text:
            # Substitute fldXXX refs with field names so the display is readable
            text = substitute_formula_ids(
                text, table["id"], by_tid, field_by_id, field_id_to_table,
            )
            display = text if len(text) <= 200 else text[:200] + "…"
            display = display.replace("\n", " ").replace("|", "\\|")
            bits.append(f"`{display}`")
        if opts.get("isValid") is False:
            bits.append("⚠ invalid")

    elif ftype == "multipleRecordLinks":
        tgt = opts.get("linkedTableId")
        if tgt and tgt in by_tid:
            tag = " (single)" if opts.get("prefersSingleRecordLink") else ""
            bits.append(f"→ **{by_tid[tgt]['name']}**{tag}")
        elif tgt:
            bits.append(f"→ `{tgt}` (external)")

    elif ftype in ("rollup", "multipleLookupValues"):
        link_fid = opts.get("recordLinkFieldId")
        tgt_fid = opts.get("fieldIdInLinkedTable")
        link_field = field_by_id.get((table["id"], link_fid)) if link_fid else None
        link_name = link_field["name"] if link_field else "(missing link)"
        target_tid = ((link_field or {}).get("options") or {}).get("linkedTableId")
        target_tname = (by_tid.get(target_tid) or {}).get("name", "?")
        target_field = (
            field_by_id.get((target_tid, tgt_fid))
            if (target_tid and tgt_fid) else None
        )
        if target_field:
            target_fname = target_field["name"]
        elif tgt_fid:
            target_fname = f"`{tgt_fid}` (missing)"
        else:
            target_fname = "(broken)"
        verb = "rolls up" if ftype == "rollup" else "looks up"
        bits.append(f"{verb} **{target_tname}**.`{target_fname}` via `{link_name}`")
        if ftype == "rollup":
            agg = (opts.get("formula") or "").strip()
            if agg:
                agg_disp = agg if len(agg) <= 120 else agg[:120] + "…"
                bits.append(f"agg: `{agg_disp}`")
        # Conditional rollups/lookups are indistinguishable from each other without
        # this — the public Metadata API omits the filter. Populated by
        # merge_internal_options.py from the internal schema; absent if not run.
        cond = (opts.get("conditionsRendered") or "").strip()
        if cond:
            bits.append(f"**only where** `{cond}`")

    elif ftype == "count":
        link_fid = opts.get("recordLinkFieldId")
        link_field = field_by_id.get((table["id"], link_fid)) if link_fid else None
        link_name = link_field["name"] if link_field else "(missing link)"
        target_tid = ((link_field or {}).get("options") or {}).get("linkedTableId")
        target_tname = (by_tid.get(target_tid) or {}).get("name", "?")
        bits.append(f"counts records in **{target_tname}** via `{link_name}`")

    elif ftype == "lastModifiedTime":
        refs = opts.get("referencedFieldIds")
        if refs:
            names = []
            for fid in refs[:5]:
                f2 = field_by_id.get((table["id"], fid))
                names.append(f2["name"] if f2 else fid)
            extra = f" _(+{len(refs) - 5} more)_" if len(refs) > 5 else ""
            bits.append(f"watches: {', '.join(f'`{n}`' for n in names)}{extra}")
        else:
            bits.append("watches: any field")

    elif ftype == "checkbox":
        icon = opts.get("icon")
        if icon:
            bits.append(f"icon: {icon}")

    return " · ".join(bits)


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

def render_summary(tables, deps, drafted_count, base_name, base_id):
    field_count = sum(len(t.get("fields") or []) for t in tables)

    # Unique link relationships (dedup by inverse pair)
    drawn = set()
    link_pairs = 0
    by_tid = {t["id"]: t for t in tables}
    for t in tables:
        for f in t.get("fields") or []:
            if f.get("type") != "multipleRecordLinks":
                continue
            opts = f.get("options") or {}
            tgt = opts.get("linkedTableId")
            if not tgt or tgt not in by_tid:
                continue
            inv = opts.get("inverseLinkFieldId")
            pair = frozenset({(t["id"], f["id"]), (tgt, inv)})
            if pair in drawn:
                continue
            drawn.add(pair)
            link_pairs += 1

    rollup_count = sum(1 for d in deps if d["kind"] == "rollup")
    lookup_count = sum(1 for d in deps if d["kind"] == "lookup")
    count_count = sum(1 for d in deps if d["kind"] == "count")
    formula_count = sum(1 for d in deps if d["kind"] == "formula")

    out = [
        f"# {base_name} — Schema Audit",
        "",
        f"_Generated {date.today().isoformat()}_",
        "",
        f"**Base:** [`{base_id}`](https://airtable.com/{base_id})",
        "",
        "## Summary",
        "",
        f"- **Tables:** {len(tables)}",
        f"- **Fields:** {field_count:,}",
        f"- **Linked-record relationships:** {link_pairs}",
        f"- **Rollups:** {rollup_count} · **Lookups:** {lookup_count} · "
        f"**Counts:** {count_count} · **Formulas with refs:** {formula_count}",
        f"- **AI-drafted descriptions:** {drafted_count} "
        f"_(tagged `(AI-drafted)` inline — review and copy back into Airtable)_",
        "",
    ]
    return "\n".join(out)


def render_erd_section(erd_text):
    return (
        "## Entity-Relationship Diagram\n\n"
        "Linked-record fields between tables. Cardinality reflects "
        "`prefersSingleRecordLink` (`||` = at most one, `}o` = many).\n\n"
        "```mermaid\n"
        f"{erd_text}\n"
        "```\n"
    )


def render_deps_section(deps):
    out = ["## Cross-table Dependencies", ""]
    if not deps:
        out.append("_(no cross-table dependencies found)_")
        out.append("")
        return "\n".join(out)

    by_table = defaultdict(list)
    for d in deps:
        by_table[d["table"]].append(d)

    for tname in sorted(by_table.keys()):
        out.append(f"### {tname}")
        out.append("")
        rows = sorted(by_table[tname], key=lambda x: (x["kind"], x.get("field", "")))
        for d in rows:
            broken_tag = " ⚠️ **broken**" if d.get("broken") else ""
            if d["kind"] == "rollup":
                line = (
                    f"- **{d['field']}** rolls up "
                    f"`{d.get('target_table') or '?'}`.`{d.get('target_field') or '?'}` "
                    f"via `{d.get('link_field') or '?'}`"
                )
                if d.get("agg_formula"):
                    line += f" — agg: `{d['agg_formula']}`"
                out.append(line + broken_tag)
            elif d["kind"] == "lookup":
                out.append(
                    f"- **{d['field']}** looks up "
                    f"`{d.get('target_table') or '?'}`.`{d.get('target_field') or '?'}` "
                    f"via `{d.get('link_field') or '?'}`{broken_tag}"
                )
            elif d["kind"] == "count":
                out.append(
                    f"- **{d['field']}** counts records in "
                    f"`{d.get('target_table') or '?'}` "
                    f"via `{d.get('link_field') or '?'}`{broken_tag}"
                )
            elif d["kind"] == "formula":
                ref_bits = []
                if d.get("in_table_refs"):
                    ref_bits.append(
                        "in-table: " + ", ".join(f"`{r}`" for r in d["in_table_refs"])
                    )
                if d.get("cross_table_refs"):
                    ref_bits.append(
                        "cross-table: " + ", ".join(f"`{r}`" for r in d["cross_table_refs"])
                    )
                if d.get("unresolved_refs"):
                    ref_bits.append(
                        "unresolved: " + ", ".join(f"`{r}`" for r in d["unresolved_refs"])
                    )
                out.append(f"- **{d['field']}** _(formula)_ — {' · '.join(ref_bits)}")
        out.append("")
    return "\n".join(out)


def render_table_section(table, drafts, by_tid, field_by_id, field_id_to_table):
    tid = table["id"]
    fields = table.get("fields") or []
    out = [
        f"### {table['name']}",
        "",
        f"**ID:** `{tid}` · **Fields:** {len(fields)} · "
        f"**Primary:** `{get_primary_name(table) or '?'}`",
        "",
    ]
    desc_text, drafted = table_description(table, drafts)
    if desc_text:
        out.append(render_description(desc_text, drafted))
        out.append("")

    out.append("| Field | Type | Description | Notes |")
    out.append("|---|---|---|---|")
    for f in fields:
        name = md_escape(f.get("name"))
        ftype = f.get("type", "?")
        desc, is_draft = field_description(f, drafts, tid)
        desc_rendered = md_escape(render_description(desc, is_draft))
        notes = md_escape(field_notes(f, table, by_tid, field_by_id, field_id_to_table))
        out.append(f"| {name} | `{ftype}` | {desc_rendered} | {notes} |")
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--raw", required=True, help="Path to raw_schema.json")
    p.add_argument("--drafts", default=None, help="Path to description_drafts.json")
    p.add_argument("--base-name", default="Airtable Base")
    p.add_argument("--base-id", required=True)
    p.add_argument("--out", required=True, help="Output schema_audit.md")
    p.add_argument("--erd-out", required=True, help="Output erd.mmd")
    args = p.parse_args()

    tables, drafts = load_inputs(args.raw, args.drafts)
    by_tid, field_by_id, field_by_name, field_id_to_table = build_indices(tables)

    drafted_count = 0
    for t in tables:
        for f in t.get("fields") or []:
            _, is_draft = field_description(f, drafts, t["id"])
            if is_draft:
                drafted_count += 1

    erd = build_erd(tables, by_tid)
    deps = collect_deps(tables, by_tid, field_by_id, field_by_name, field_id_to_table)

    parts = [
        render_summary(tables, deps, drafted_count, args.base_name, args.base_id),
        render_erd_section(erd),
        render_deps_section(deps),
        "## Tables",
        "",
    ]
    for t in sorted(tables, key=lambda x: (x.get("name") or "").lower()):
        parts.append(
            render_table_section(t, drafts, by_tid, field_by_id, field_id_to_table)
        )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(parts).rstrip() + "\n")

    erd_path = Path(args.erd_out)
    erd_path.parent.mkdir(parents=True, exist_ok=True)
    erd_path.write_text(erd + "\n")

    field_total = sum(len(t.get("fields") or []) for t in tables)
    print(f"Wrote {out_path}")
    print(f"Wrote {erd_path}")
    print(
        f"Tables: {len(tables)}  Fields: {field_total:,}  "
        f"AI-drafted: {drafted_count}  Cross-table deps: {len(deps)}"
    )


if __name__ == "__main__":
    main()
