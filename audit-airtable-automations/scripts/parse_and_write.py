#!/usr/bin/env python3
"""
Airtable Automations Audit Parser

Reads raw_automations.json + ID maps and writes the formatted audit document with
per-automation workflow IDs, hyperlinks back to Airtable, and resolved trigger
conditions (watched fields, filter formulas, view filters).

Usage:
    python parse_and_write.py \
        --raw airtable_audit/raw_automations.json \
        --out airtable_audit/automations_audit.md \
        --base-name "My Base" \
        --base-id appXXXXXXXXX \
        --table-map  '{"tblXXX": "Shipments", ...}' \
        --field-map  '{"tblXXX": {"fldXXX": "Status", ...}, ...}' \
        --view-map   '{"tblXXX": {"viwXXX": "View Name", ...}, ...}' \
        --view-filters airtable_audit/view_filters.json     # optional

Map flags accept either an inline JSON string or a path to a JSON file. If a map
is omitted, IDs render as-is.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

# ─── Trigger / action type readable names ──────────────────────────────────────

TRIGGER_LABELS = {
    "wttCRON0000000000": "Schedule (CRON)",
    "wttRECORDCREATED0": "Record created",
    "wttRECORDMATCHES0": "Record matches conditions",
    "wttRECORDUPDATED0": "Record updated",
    "wttBRZzRXx3C2jyIc": "Record enters view",
    "wttCONNECTIONINPT": "Button / external trigger",
}

ACTION_LABELS = {
    "watOUTLOKSENDMAIL": "Send Outlook email",
    "watSENDEMAIL00000": "Send email",
    "watFINDRECORDS000": "Find records",
    "watCUSTOMSCRIPT00": "Run script",
    "watUPDATERECORD00": "Update record",
    "watCREATERECORD00": "Create record",
    "watBETUHIcuho4hit": "Conditional logic",
    "watAIGENERATESTR0": "AI generate text",
    "watGSHEETSCREATE0": "Create Google Sheet",
}

EMAIL_ACTIONS = {"watOUTLOKSENDMAIL", "watSENDEMAIL00000"}

# Operator → human phrasing for filtersObj rendering. Anything not in this map
# falls back to the raw operator string so we never silently drop conditions.
OPERATOR_PHRASES = {
    "=": "=",
    "!=": "≠",
    ">": ">",
    "<": "<",
    ">=": "≥",
    "<=": "≤",
    "isEmpty": "is empty",
    "isNotEmpty": "is not empty",
    "contains": "contains",
    "doesNotContain": "does not contain",
    "isAnyOf": "is any of",
    "isNoneOf": "is none of",
    "isWithin": "is within",
}


# ─── Helpers ───────────────────────────────────────────────────────────────────

def load_json_arg(val):
    """Accept a file path or an inline JSON string. Empty/None returns {}."""
    if val is None:
        return {}
    p = Path(val)
    if p.exists():
        return json.loads(p.read_text())
    return json.loads(val)


def resolve(id_val, id_map, fallback=None):
    if not id_val:
        return fallback or id_val
    return id_map.get(id_val, id_val)


def resolve_field(table_id, field_id, field_map):
    if not field_id:
        return field_id
    fmap = field_map.get(table_id, {}) if table_id else {}
    return fmap.get(field_id, field_id)


def airtable_url(app_id, *parts):
    return "https://airtable.com/" + "/".join([app_id, *[p for p in parts if p]])


def sends_email(automation):
    return any(a["actionType"] in EMAIL_ACTIONS for a in automation.get("actions", []))


# ─── Filter tree rendering ─────────────────────────────────────────────────────

def _props_to_dict(node):
    """Turn an Airtable expression-tree `properties` array into a plain dict."""
    if not isinstance(node, dict):
        return {}
    props = node.get("properties", [])
    if not isinstance(props, list):
        return {}
    out = {}
    for p in props:
        key = (p.get("key") or {}).get("value")
        if key is not None:
            out[key] = p.get("value")
    return out


def _render_operand(operand, table_id, field_map):
    """Render a single operand from a filter tree as a string."""
    if not isinstance(operand, dict):
        return repr(operand)
    t = operand.get("type")
    if t == "literal":
        v = operand.get("value")
        if isinstance(v, str) and v.startswith("fld"):
            return f"`{resolve_field(table_id, v, field_map)}`"
        if isinstance(v, str) and v.startswith("sel"):
            return f'option `{v}`'
        return f'"{v}"' if isinstance(v, str) else json.dumps(v)
    if t == "object":
        return _render_filter_node(operand, table_id, field_map, depth=1)
    return "(complex expression)"


def _render_filter_node(node, table_id, field_map, depth=0):
    """Recursively render a filter tree node (object with operator + operands)."""
    d = _props_to_dict(node)
    op = (d.get("operator") or {}).get("value") if isinstance(d.get("operator"), dict) else None
    operands = (d.get("operands") or {}).get("elements", []) if isinstance(d.get("operands"), dict) else []

    if op in ("and", "or"):
        rendered = [_render_filter_node(el, table_id, field_map, depth + 1) for el in operands]
        joiner = f"\n{'  ' * depth}{op.upper()} "
        if depth == 0:
            return "\n".join(f"- {r}" for r in rendered)
        return "(" + joiner.join(rendered) + ")"

    if op in OPERATOR_PHRASES:
        phrase = OPERATOR_PHRASES[op]
    elif op:
        phrase = op
    else:
        return "(unparsed)"

    if not operands:
        return phrase

    # First operand is conventionally the field; remainder are values
    first = _render_operand(operands[0], table_id, field_map)
    if len(operands) == 1:
        return f"{first} {phrase}"
    rest = ", ".join(_render_operand(op_, table_id, field_map) for op_ in operands[1:])
    return f"{first} {phrase} {rest}"


def render_trigger_conditions(automation, table_map, field_map, view_map,
                              view_filters, app_id):
    """Return a list of markdown lines describing the trigger conditions."""
    lines = []
    tid = automation.get("triggerTypeId", "")
    ti = automation.get("trigInputs", {}) or {}
    tc = automation.get("triggerConditions", {}) or {}
    table_id = ti.get("tableId")
    table_name = resolve(table_id, table_map, "—") if table_id else "—"
    label = TRIGGER_LABELS.get(tid, tid or "Unknown")

    if tid == "wttCRON0000000000":
        cron = ti.get("cronType") or "scheduled"
        lines.append(f"**Trigger:** Schedule ({cron})")
        return lines

    if tid == "wttCONNECTIONINPT":
        lines.append(f"**Trigger:** Button / external on **{table_name}**")
        return lines

    lines.append(f"**Trigger:** {label} on **{table_name}**")

    if tid == "wttRECORDCREATED0":
        lines.append("**Fires when:** any new record is created in this table")

    elif tid == "wttRECORDUPDATED0":
        watch = tc.get("watchFields", []) or []
        if watch:
            names = [f"`{resolve_field(table_id, f, field_map)}`" for f in watch]
            lines.append(f"**Watched fields:** {', '.join(names)}")
            lines.append(
                "**Fires when:** any of the watched fields above is modified on a record. "
                "Other field edits do not fire this trigger."
            )
        else:
            lines.append("**Watched fields:** any field")
            lines.append("**Fires when:** any field on the record is modified")

    elif tid == "wttRECORDMATCHES0":
        filters_obj = tc.get("filtersObj")
        if filters_obj:
            rendered = _render_filter_node(filters_obj, table_id, field_map)
            lines.append("**Filter:**")
            lines.append(rendered if rendered.startswith("- ") else f"- {rendered}")
        else:
            lines.append("**Filter:** _(not captured)_")

    elif tid == "wttBRZzRXx3C2jyIc":
        view_id = ti.get("viewId")
        view_name = (view_map.get(table_id, {}) or {}).get(view_id, view_id) if view_id else None
        if view_id:
            view_url = airtable_url(app_id, table_id, view_id)
            lines.append(f"**View:** `{view_name}` ([open in Airtable]({view_url}))")
            vf = (view_filters or {}).get(view_id) or {}
            ff = vf.get("filterFormula")
            if ff:
                lines.append(f"**View filter:** `{ff}`")
            else:
                lines.append("**View filter:** _(not captured — see view in Airtable)_")
        else:
            lines.append("**View:** _(missing viewId)_")

    return lines


# ─── Action rendering ──────────────────────────────────────────────────────────

def render_action(action, table_map, field_map, idx):
    at = action.get("actionType", "?")
    label = ACTION_LABELS.get(at, at)
    table_id = action.get("tableId")
    table_name = resolve(table_id, table_map, None)

    head = f"{idx}. **{label}**"
    if table_name:
        head += f" → **{table_name}**"

    bullets = []
    raw_fields = action.get("fieldsWritten", [])
    if raw_fields:
        named = [f"`{resolve_field(table_id, f, field_map)}`" for f in raw_fields]
        bullets.append(f"Writes: {', '.join(named)}")

    if at in EMAIL_ACTIONS:
        to = action.get("toVal", "") or "(dynamic)"
        subj = action.get("subjectVal", "")
        bullets.append(f"To: {to[:200]}")
        if subj:
            bullets.append(f"Subject: {subj[:200]}")

    if action.get("scriptLen"):
        bullets.append(f"Script: {action['scriptLen']} chars")

    if action.get("filterFormula"):
        bullets.append(f"Find filter: `{action['filterFormula']}`")

    if not bullets:
        return head
    return head + "\n" + "\n".join(f"   - {b}" for b in bullets)


# ─── Document sections ─────────────────────────────────────────────────────────

def section_header(base_name, base_id, automations):
    total = len(automations)
    enabled = sum(1 for a in automations if a.get("enabled"))
    disabled = total - enabled
    today = date.today().isoformat()

    lines = [
        f"# {base_name} — Airtable Automations Audit",
        "",
        f"**Date:** {today}  ",
        f"**Base:** {base_name} (`{base_id}`)  ",
        f"**Total automations:** {total} ({enabled} enabled, {disabled} disabled)",
        "",
    ]
    if total and enabled / total > 0.8:
        lines += [
            "> ⚠️ **Schema cleanup warning:** Most automations are currently ON. Any field",
            "> rename, deletion, or view change may silently break one or more automations.",
            "> Review per-automation trigger conditions before making schema changes.",
            "",
        ]
    return "\n".join(lines)


def section_summary_table(automations, table_map, app_id):
    lines = [
        "## Summary Table",
        "",
        "| # | Name | Status | Trigger Table | Trigger Type | Email? |",
        "|---|------|--------|---------------|--------------|--------|",
    ]
    for i, auto in enumerate(automations, 1):
        status = "✓ ON" if auto.get("enabled") else "✗ OFF"
        tbl = resolve((auto.get("trigInputs") or {}).get("tableId"), table_map, "—")
        tid = auto.get("triggerTypeId", "")
        trig_label = TRIGGER_LABELS.get(tid, tid or "Unknown")
        email = "✉️" if sends_email(auto) else ""
        name = auto.get("name", auto.get("id", "?"))
        url = auto.get("url") or airtable_url(app_id, auto.get("id"))
        lines.append(f"| {i} | [{name}]({url}) | {status} | {tbl} | {trig_label} | {email} |")
    return "\n".join(lines)


def section_email_automations(automations, table_map, view_map, field_map,
                              view_filters, app_id):
    email_autos = [a for a in automations if sends_email(a)]
    if not email_autos:
        return "## Email-Sending Automations\n\nNone found."

    lines = [
        "## Email-Sending Automations",
        "",
        f"_{len(email_autos)} automations send email._",
        "",
    ]
    for auto in email_autos:
        name = auto.get("name", auto.get("id"))
        status = "✓ ON" if auto.get("enabled") else "✗ OFF"
        url = auto.get("url") or airtable_url(app_id, auto.get("id"))
        lines += [
            f"### [{name}]({url}) ({status})",
            f"**ID:** `{auto.get('id')}`  ",
        ]
        lines += [l + "  " for l in render_trigger_conditions(
            auto, table_map, field_map, view_map, view_filters, app_id)]
        lines.append("")

        for action in auto.get("actions", []):
            if action["actionType"] not in EMAIL_ACTIONS:
                continue
            to = action.get("toVal", "")
            subj = action.get("subjectVal", "")
            lines.append(f"- **Action:** {ACTION_LABELS.get(action['actionType'], action['actionType'])}")
            lines.append(f"  - To: {to[:200] or '(dynamic)'}")
            if subj:
                lines.append(f"  - Subject: {subj[:200]}")

        other = [a for a in auto.get("actions", []) if a["actionType"] not in EMAIL_ACTIONS]
        if other:
            lines.append("")
            lines.append("**Other actions in this automation:**")
            for j, a in enumerate(other, 1):
                lines.append(render_action(a, table_map, field_map, j))
        lines.append("")

    return "\n".join(lines)


def section_per_automation(automations, table_map, view_map, field_map,
                           view_filters, app_id):
    lines = ["## Per-Automation Details", ""]

    by_table = {}
    for auto in automations:
        tbl_id = (auto.get("trigInputs") or {}).get("tableId") or "__no_table__"
        by_table.setdefault(tbl_id, []).append(auto)

    def group_sort_key(k):
        if k == "__no_table__":
            return "zzz"
        return resolve(k, table_map, k)

    for tbl_id in sorted(by_table.keys(), key=group_sort_key):
        if tbl_id == "__no_table__":
            tbl_name = "Schedule & Button Triggers"
        else:
            tbl_name = resolve(tbl_id, table_map, tbl_id)
        lines += [f"### {tbl_name}", ""]

        for auto in by_table[tbl_id]:
            name = auto.get("name", auto.get("id"))
            status = "✓ ON" if auto.get("enabled") else "✗ OFF"
            url = auto.get("url") or airtable_url(app_id, auto.get("id"))
            lines += [
                f"#### {name} [{status}]",
                f"**ID:** `{auto.get('id')}` · [Open in Airtable]({url})  ",
            ]
            lines += [l + "  " for l in render_trigger_conditions(
                auto, table_map, field_map, view_map, view_filters, app_id)]
            if auto.get("description"):
                lines += ["", f"> {auto['description']}"]

            actions = auto.get("actions", [])
            lines.append("")
            if actions:
                lines.append("**Actions:**")
                for j, a in enumerate(actions, 1):
                    lines.append(render_action(a, table_map, field_map, j))
            else:
                lines.append("_No actions captured._")
            lines.append("")

    return "\n".join(lines)


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Parse raw automations JSON and write audit doc.")
    parser.add_argument("--raw",          required=True, help="Path to raw_automations.json")
    parser.add_argument("--out",          required=True, help="Output markdown path")
    parser.add_argument("--base-name",    default="Airtable Base", help="Human-readable base name")
    parser.add_argument("--base-id",      required=True, help="Airtable base ID (appXXX) — needed for hyperlinks")
    parser.add_argument("--table-map",    default=None, help="JSON file or string: {tableId: tableName}")
    parser.add_argument("--field-map",    default=None, help="JSON file or string: {tableId: {fieldId: fieldName}}")
    parser.add_argument("--view-map",     default=None, help="JSON file or string: {tableId: {viewId: viewName}}")
    parser.add_argument("--view-filters", default=None, help="JSON file: {viewId: {tableId, name, filterFormula}}")
    args = parser.parse_args()

    raw_path = Path(args.raw)
    if not raw_path.exists():
        print(f"ERROR: raw file not found: {raw_path}", file=sys.stderr)
        sys.exit(1)

    automations = json.loads(raw_path.read_text())
    table_map = load_json_arg(args.table_map)
    field_map = load_json_arg(args.field_map)
    view_map = load_json_arg(args.view_map)
    view_filters = load_json_arg(args.view_filters)
    app_id = args.base_id

    sections = [
        section_header(args.base_name, app_id, automations),
        "---",
        section_summary_table(automations, table_map, app_id),
        "",
        "---",
        section_email_automations(automations, table_map, view_map, field_map,
                                  view_filters, app_id),
        "",
        "---",
        section_per_automation(automations, table_map, view_map, field_map,
                               view_filters, app_id),
    ]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(sections))
    print(f"Wrote {out_path} ({out_path.stat().st_size:,} bytes, {len(automations)} automations)")


if __name__ == "__main__":
    main()
