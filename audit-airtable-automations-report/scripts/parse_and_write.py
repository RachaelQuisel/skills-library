#!/usr/bin/env python3
"""
Airtable Automations Audit Parser

Reads raw_automations.json + ID maps and writes the formatted audit document
with per-automation workflow IDs, hyperlinks back to Airtable, resolved trigger
conditions (watched fields, filter formulas, view filters), and a cascade map
showing which automations could trigger which others.

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
        --choices-map  '{"fldXXX": {"selYYY": "Option Name", ...}, ...}'  # optional

Map flags accept either an inline JSON string or a path to a JSON file. If a
map is omitted, IDs render as-is.

Why field/option resolution lives here (not in the fetch script): the fetch
script runs in a browser context with no access to the schema. The schema
fetch (scripts/fetch_schema.js or MCP describe_table) happens in a separate
step. Resolving names in this parser keeps the toolchain composable — you
can re-resolve later without re-running the browser fetch.
"""

import argparse
import json
import re
import sys
from collections import defaultdict
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
    "wttFORMSUBMITTED0": "Form submitted",
    "wttEMAILRECEIVED0": "Email received",
    "wttGENERICWEBHOOK": "Incoming webhook",
}

ACTION_LABELS = {
    "watOUTLOKSENDMAIL": "Send Outlook email",
    "watSENDEMAIL00000": "Send email",
    "watFINDRECORDS000": "Find records",
    "watCUSTOMSCRIPT00": "Run script",
    "watUPDATERECORD00": "Update record",
    "watCREATERECORD00": "Create record",
    # watBETUHIcuho4hit was previously labeled "Conditional logic" but inspection
    # of its inputExpressions (to/cc/bcc/subject/message/attachments) shows it's a
    # conditional-send email variant — same shape as watOUTLOKSENDMAIL but only
    # fires when a prior branch matches. Counts as email for the cascade map.
    "watBETUHIcuho4hit": "Send email (with conditions)",
    "watAIGENERATESTR0": "AI generate text",
    "watGSHEETSCREATE0": "Create Google Sheet",
    # Additional action types observed in the wild (Gmail/Slack/GCal/AI).
    # watGMAILSENDMAIL0 stores recipient/subject under the same to/subject keys
    # as the Outlook variant, so it decodes identically and counts as email.
    "watGMAILSENDMAIL0": "Send Gmail",
    "watSENDTOSLACK000": "Send Slack message",
    "watSLACKSNDACTMSG": "Send Slack action message",
    "watGCALUPDATEEVT0": "Update Google Calendar event",
    "watAIGENERATE0000": "AI generate text",
    "watSENDTOMSTEAMS0": "Send Microsoft Teams message",
}

# Decision nodes — these orchestrate control flow inside an automation. The
# fetch script captures them alongside actions so the audit can show the full
# graph (e.g., "for each record found, send email" rather than just two flat
# actions with an unexplained gap).
DECISION_LABELS = {
    "wdtFANOUT00000000": "Fan-out (forEach)",
    "wdtREDUCER0000000": "End of forEach (reducer)",
    "wdtNWAY0000000000": "Branch (N-way conditional)",
}

EMAIL_ACTIONS = {"watOUTLOKSENDMAIL", "watSENDEMAIL00000", "watBETUHIcuho4hit", "watGMAILSENDMAIL0"}

# Operator → human phrasing for filtersObj rendering. Anything missing here
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
    if field_id in fmap:
        return fmap[field_id]
    # Fall back: maybe field_id appears in another table (linked-record artifact)
    for other in field_map.values():
        if field_id in other:
            return other[field_id]
    return field_id


def resolve_option(field_id, opt_id, choices_map):
    """Render selXXX as 'Option Name' using a {fldXXX: {selYYY: name}} map."""
    if not opt_id:
        return opt_id
    if field_id and field_id in choices_map:
        return choices_map[field_id].get(opt_id, opt_id)
    # Fall back: scan all field choice maps for this opt_id
    for choices in choices_map.values():
        if opt_id in choices:
            return choices[opt_id]
    return opt_id


def airtable_url(app_id, *parts):
    return "https://airtable.com/" + "/".join([app_id, *[p for p in parts if p]])


def td(s):
    """Escape a value for safe use inside a markdown table cell. Pipes in
    automation/table names (e.g. 'SYNC | Invoice | QBD') otherwise break the
    column layout; newlines collapse the row."""
    if s is None:
        return ""
    return str(s).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def sends_email(automation):
    return any(a["actionType"] in EMAIL_ACTIONS for a in automation.get("actions", []))


# ─── Template post-decoding (field-ID substitution) ────────────────────────────
# The fetch script decodes Airtable's expression trees but leaves field IDs
# as {field:fldXXX} or {cellValuesByFieldId, fldXXX} because the browser
# context has no field map. Substitute names here.

_FIELD_REF_PATTERNS = [
    re.compile(r"\{field:(fld[A-Za-z0-9]+)\}"),
    re.compile(r"\{cellValuesByFieldId,\s*(fld[A-Za-z0-9]+)\}"),
]

# Bare field IDs also surface inside decoded function calls — e.g. a script input
# of the form {getBaseMetadata(fldXXX, id)} where a literal field ID is passed as
# an argument. These don't match the wrapped {field:...} patterns above, so resolve
# any remaining bare fldXXX token too. Safe because substitute_field_refs is only
# applied to script-input refs and email to/subject templates (never script bodies),
# where a bare field ID is unambiguously a field reference.
_BARE_FIELD_ID = re.compile(r"\bfld[A-Za-z0-9]{14}\b")


def substitute_field_refs(text, field_map):
    if not isinstance(text, str) or "fld" not in text:
        return text
    # Build a flat field id → name index (any table)
    flat = {}
    for tbl in field_map.values():
        for fid, fname in tbl.items():
            flat.setdefault(fid, fname)
    out = text
    for pat in _FIELD_REF_PATTERNS:
        out = pat.sub(lambda m: "{" + flat.get(m.group(1), m.group(1)) + "}", out)
    # Resolve any leftover bare field IDs (only those present in the field map;
    # unknown IDs are left untouched so a stale reference stays visible).
    out = _BARE_FIELD_ID.sub(lambda m: flat.get(m.group(0), m.group(0)), out)
    return out


# Script input variables can reference a preceding action's output as {node:wacXXX}.
# Resolve those to the action's human label so "recordIds ← {node:wac...}" reads as
# "recordIds ← output of 'Find records'".
_NODE_REF_PATTERN = re.compile(r"\{node:(wac[A-Za-z0-9]+)\}")


def _resolve_node_refs(text, actions_by_id):
    if not isinstance(text, str) or "{node:" not in text:
        return text

    def repl(m):
        nid = m.group(1)
        a = (actions_by_id or {}).get(nid)
        if a:
            at = a.get("actionType")
            label = ACTION_LABELS.get(at) or DECISION_LABELS.get(at) or at or nid
            return f"output of '{label}'"
        return f"output of {nid}"

    return _NODE_REF_PATTERN.sub(repl, text)


# ─── Script extraction (one .js file per "Run a script" action) ─────────────────
# Inline code bloats the audit doc and reads as prose to an agent. We extract each
# script to its own self-describing .js file under scripts/ and link to it from the
# audit, plus emit a scripts.json manifest mapping automation → files.

def _slug(text, maxlen=60):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", (text or "").strip().lower()).strip("-")
    return s[:maxlen].rstrip("-") or "automation"


def script_rel_path(auto_name, node_id):
    """Stable, collision-free relative path for a script action's file. The slug
    carries the automation name (readable); the full node id guarantees uniqueness
    when one automation has several scripts."""
    return f"scripts/{_slug(auto_name)}__{node_id or 'node'}.js"


def render_script_inputs(action, field_map, actions_by_id):
    """Return [(name, readable_ref)] for a script action's input.config() variables,
    with {field:...}/{node:...} placeholders resolved to names/labels."""
    out = []
    for v in action.get("scriptInputs", []) or []:
        ref = substitute_field_refs(v.get("ref", ""), field_map)
        ref = _resolve_node_refs(ref, actions_by_id)
        out.append((v.get("name", "?"), ref))
    return out


def write_script_files(automations, field_map, app_id, out_dir):
    """Write one .js file per script action and a scripts.json manifest. Returns the
    number of script files written. Clears stale .js files from a prior run first."""
    scripts_dir = out_dir / "scripts"
    if scripts_dir.exists():
        for f in scripts_dir.glob("*.js"):
            f.unlink()

    manifest = {"baseId": app_id, "automations": []}
    count = 0
    for auto in automations:
        actions = auto.get("actions", []) or []
        actions_by_id = {a.get("id") or f"_unknown_{i}": a for i, a in enumerate(actions)}
        script_actions = [a for a in actions if a.get("script")]
        if not script_actions:
            continue

        name = auto.get("name", auto.get("id"))
        url = auto.get("url") or airtable_url(app_id, auto.get("id"))
        entry = {"id": auto.get("id"), "name": name, "url": url, "scripts": []}

        for a in script_actions:
            node_id = a.get("id") or "node"
            rel = script_rel_path(name, node_id)
            pairs = render_script_inputs(a, field_map, actions_by_id)
            label = ACTION_LABELS.get(a.get("actionType"), "Run script")

            header = [
                "/*",
                f" * Automation: {name}",
                f" * Workflow ID: {auto.get('id')}",
                f" * Action node: {node_id}  ({label})",
                f" * Open in Airtable: {url}",
            ]
            if pairs:
                header += [" *", " * Script input variables (input.config()):"]
                header += [f" *   {n} <- {r}" for n, r in pairs]
            header += [
                " *",
                " * Extracted by audit-airtable-automations. Airtable is the source of",
                " * truth; edits to this file are not synced back.",
                " */",
                "",
            ]
            file_path = out_dir / rel
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("\n".join(header) + a["script"].rstrip("\n") + "\n")
            count += 1

            entry["scripts"].append({
                "node": node_id,
                "file": rel,
                "chars": a.get("scriptLen", len(a["script"])),
                "actionType": a.get("actionType"),
                "inputs": [{"name": n, "ref": r} for n, r in pairs],
            })
        manifest["automations"].append(entry)

    (out_dir / "scripts.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    return count


def classify_recipient(to_val):
    """Tag the To: value so partner-facing vs internal-only is visible at a glance."""
    if not to_val:
        return "(no recipients captured)"
    # Hardcoded internal-org emails (heuristic: @ in literal addresses)
    has_dynamic = "{" in to_val or "dynamic" in to_val.lower()
    has_static = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", to_val))
    if has_dynamic and not has_static:
        return to_val + "  _(dynamic — likely partner-facing)_"
    if has_dynamic and has_static:
        return to_val + "  _(mixed: internal + dynamic recipients)_"
    return to_val


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


def _render_operand(operand, table_id, field_map, choices_map, parent_field_id=None):
    if not isinstance(operand, dict):
        return repr(operand)
    t = operand.get("type")
    if t == "literal":
        v = operand.get("value")
        if isinstance(v, str) and v.startswith("fld"):
            return f"`{resolve_field(table_id, v, field_map)}`"
        if isinstance(v, str) and v.startswith("sel"):
            return f'"{resolve_option(parent_field_id, v, choices_map)}"'
        if isinstance(v, list):
            # multi-value (isAnyOf, isNoneOf)
            rendered = []
            for item in v:
                if isinstance(item, str) and item.startswith("sel"):
                    rendered.append(f'"{resolve_option(parent_field_id, item, choices_map)}"')
                else:
                    rendered.append(json.dumps(item))
            return "[" + ", ".join(rendered) + "]"
        return f'"{v}"' if isinstance(v, str) else json.dumps(v)
    if t == "tuple":
        # multi-value operand (isAnyOf / isNoneOf) arrives as a tuple of literal
        # nodes rather than a single literal holding a list.
        return "[" + ", ".join(
            _render_operand(el, table_id, field_map, choices_map, parent_field_id)
            for el in operand.get("elements", [])
        ) + "]"
    if t == "object":
        return _render_filter_node(operand, table_id, field_map, choices_map, depth=1)
    if t == "functionCall":
        # date arithmetic, NOW(), etc. — render fn name + arg count so it's at
        # least visible rather than silently swallowed.
        fn = (operand.get("function") or {}).get("id", "fn")
        args = operand.get("arguments") or operand.get("parameters") or []
        return f"`{fn}(…{len(args)} args)`"
    if t == "nodeIdentifier":
        return "(action ref)"
    return f"({t or 'expr'})"


def _render_filter_node(node, table_id, field_map, choices_map, depth=0):
    d = _props_to_dict(node)
    op = (d.get("operator") or {}).get("value") if isinstance(d.get("operator"), dict) else None
    operands = (d.get("operands") or {}).get("elements", []) if isinstance(d.get("operands"), dict) else []

    if op in ("and", "or"):
        rendered = [_render_filter_node(el, table_id, field_map, choices_map, depth + 1) for el in operands]
        if depth == 0:
            return "\n".join(f"- {r}" for r in rendered)
        joiner = f" {op.upper()} "
        return "(" + joiner.join(rendered) + ")"

    phrase = OPERATOR_PHRASES.get(op, op or "(unknown op)")
    if not operands:
        return phrase

    # First operand is conventionally the field — capture its ID so we can
    # resolve select options on the value side.
    first_field = None
    if isinstance(operands[0], dict) and operands[0].get("type") == "literal":
        fv = operands[0].get("value")
        if isinstance(fv, str) and fv.startswith("fld"):
            first_field = fv

    first = _render_operand(operands[0], table_id, field_map, choices_map)
    if len(operands) == 1:
        return f"{first} {phrase}"
    rest = ", ".join(_render_operand(op_, table_id, field_map, choices_map, parent_field_id=first_field) for op_ in operands[1:])
    return f"{first} {phrase} {rest}"


def render_trigger_conditions(automation, table_map, field_map, view_map,
                              view_filters, choices_map, app_id, form_map=None):
    """Return a list of markdown lines describing the trigger conditions."""
    form_map = form_map or {}
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

    if tid == "wttGENERICWEBHOOK":
        lines.append("**Trigger:** Incoming webhook")
        lines.append("**Fires when:** an external system POSTs to this automation's generated webhook URL (no table or filter condition)")
        return lines

    if tid == "wttEMAILRECEIVED0":
        lines.append("**Trigger:** Email received")
        lines.append("**Fires when:** an email arrives at this automation's generated inbound address (no table or filter condition)")
        return lines

    if tid == "wttFORMSUBMITTED0":
        form_id = ti.get("formId")
        form_name = resolve(form_id, form_map, form_id) if form_id else None
        lines.append(f"**Trigger:** Form submitted on **{table_name}**")
        if form_id:
            form_url = airtable_url(app_id, form_id, "form")
            lines.append(f"**Form:** `{form_name}` ([open form]({form_url}))")
            lines.append("**Fires when:** the form above is submitted, creating a new record in this table")
        else:
            lines.append("**Fires when:** a form on this table is submitted")
        return lines

    lines.append(f"**Trigger:** {label} on **{table_name}**")

    if tid == "wttRECORDCREATED0":
        lines.append("**Fires when:** any new record is created in this table")

    elif tid == "wttRECORDUPDATED0":
        watch = tc.get("watchFields", []) or []
        if watch:
            names = [f"`{resolve_field(table_id, f, field_map)}`" for f in watch]
            lines.append(f"**Watched fields:** {', '.join(names)}")
            lines.append("**Fires when:** any of the watched fields above is modified. Other field edits do not fire this trigger.")
        else:
            lines.append("**Watched fields:** any field")
            lines.append("**Fires when:** any field on the record is modified")

    elif tid == "wttRECORDMATCHES0":
        filters_obj = tc.get("filtersObj")
        if filters_obj:
            rendered = _render_filter_node(filters_obj, table_id, field_map, choices_map)
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
            # Accept either filterFormula (legacy) or filterRendered (new JS shape)
            ff = vf.get("filterFormula") or vf.get("filterRendered")
            if ff:
                # The view filter uses fldXXX column IDs and selXXX option IDs.
                # Substitute field names AND option names so the formula reads
                # in business terms instead of opaque IDs.
                ff_resolved = re.sub(
                    r"`(fld[A-Za-z0-9]+)`",
                    lambda m: f"`{resolve_field(table_id, m.group(1), field_map)}`",
                    ff,
                )
                ff_resolved = re.sub(
                    r'"(sel[A-Za-z0-9]+)"',
                    lambda m: f'"{resolve_option(None, m.group(1), choices_map)}"',
                    ff_resolved,
                )
                lines.append(f"**View filter:** `{ff_resolved}`")
            else:
                lines.append("**View filter:** _(not captured — see view in Airtable)_")
        else:
            lines.append("**View:** _(missing viewId)_")

    return lines


# ─── Action rendering ──────────────────────────────────────────────────────────

def _decision_extras(action, all_actions_by_id):
    """Render decision-specific context: what's being looped over, how many branches."""
    extras = []
    at = action.get("actionType")
    if at == "wdtFANOUT00000000":
        src_id = action.get("loopOver")
        if src_id:
            src = all_actions_by_id.get(src_id) or {}
            src_label = ACTION_LABELS.get(src.get("actionType"), src.get("actionType") or src_id)
            extras.append(f"Iterates over results from: **{src_label}** (`{src_id}`)")
    if at == "wdtNWAY0000000000":
        bc = action.get("branchCount")
        if bc is not None:
            extras.append(f"Branches: {bc}")
    return extras


def render_action(action, table_map, field_map, app_id, idx, actions_by_id=None):
    at = action.get("actionType", "?")
    # Try action label first, then decision label; fall back to the raw ID rather than '?'
    # so callers can spot unmapped types and add them.
    label = ACTION_LABELS.get(at) or DECISION_LABELS.get(at) or at
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
        to_raw = substitute_field_refs(action.get("toVal", ""), field_map)
        subj_raw = substitute_field_refs(action.get("subjectVal", ""), field_map)
        if to_raw:
            bullets.append(f"To: {classify_recipient(to_raw)}")
        for key, label in (("ccVal", "Cc"), ("fromVal", "From"), ("attachmentsVal", "Attachments")):
            v = substitute_field_refs(action.get(key, ""), field_map)
            if v:
                bullets.append(f"{label}: {v}")
        if subj_raw:
            bullets.append(f"Subject: {subj_raw}")

    # AI-generate actions: the prompt IS the logic — never leave it out.
    if action.get("promptVal"):
        p = substitute_field_refs(action["promptVal"], field_map)
        if action.get("modelVal"):
            bullets.append(f"Model: `{action['modelVal']}`")
        bullets.append(f"Prompt ({len(p)} chars): {p[:400]}{'…' if len(p) > 400 else ''}")
    if action.get("outputSchema"):
        bullets.append(f"Output schema: {action['outputSchema'][:300]}")
    if action.get("teamsRecipient"):
        bullets.append(f"Teams recipient: {action['teamsRecipient']}")

    # N-way branch conditions decide which email a recipient gets — surface them.
    for i_b, (cond, tgt) in enumerate(zip(action.get("branchConditions") or [],
                                          action.get("branchTargets") or []), 1):
        c = substitute_field_refs(cond, field_map)
        bullets.append(f"Branch {i_b} → `{tgt}` when: {c[:300]}{'…' if len(c) > 300 else ''}")

    if action.get("scriptInputs"):
        pairs = render_script_inputs(action, field_map, actions_by_id)
        if pairs:
            bullets.append("Script inputs: " + "; ".join(f"`{n}` ← {r}" for n, r in pairs))

    if action.get("scriptLen"):
        suffix = " (see Scripts section for file link)" if action.get("script") else ""
        bullets.append(f"Script: {action['scriptLen']} chars{suffix}")

    if action.get("filterFormula"):
        bullets.append(f"Find filter: `{action['filterFormula']}`")

    if action.get("nodeKind") == "decision" and actions_by_id is not None:
        bullets += _decision_extras(action, actions_by_id)

    if not bullets:
        return head
    return head + "\n" + "\n".join(f"   - {b}" for b in bullets)


# ─── Cascade map ───────────────────────────────────────────────────────────────

def _trigger_field_ids(automation, view_filters):
    """Return (table_id, field_id, source_label) tuples — fields that, when
    modified, cause this automation to fire."""
    tt = automation.get("triggerTypeId")
    ti = automation.get("trigInputs") or {}
    tc = automation.get("triggerConditions") or {}
    table_id = ti.get("tableId")
    out = []
    if tt == "wttRECORDUPDATED0":
        for fid in tc.get("watchFields") or []:
            out.append((table_id, fid, "watched"))
    elif tt == "wttRECORDMATCHES0":
        for fid in tc.get("filterFieldIds") or []:
            out.append((table_id, fid, "filter"))
    elif tt == "wttBRZzRXx3C2jyIc":
        vid = ti.get("viewId")
        vf = (view_filters or {}).get(vid) or {}
        raw = vf.get("filterRaw") or vf.get("raw") or {}

        def walk(node):
            if not isinstance(node, dict):
                return
            if isinstance(node.get("filterSet"), list):
                for c in node["filterSet"]:
                    walk(c)
            cid = node.get("columnId") or node.get("fieldId")
            if cid:
                out.append((table_id, cid, "view filter"))

        walk(raw)
    return out


def render_cascade_section(automations, table_map, field_map, view_filters, app_id, choices_map=None):
    choices_map = choices_map or {}
    """Find automation→automation cascades and render them.

    A cascade exists when an UPDATE-record action in automation X writes a
    field that's watched, matched, or referenced in a view filter by another
    automation Y. We list the upstream writers under each downstream target,
    rather than vice versa, because that's how a cleanup-minded reader thinks:
    "if I touch this field, what fires?"
    """
    # Build (table_id, field_id) → list of (writer_automation, writer_enabled)
    writers = defaultdict(list)
    for a in automations:
        for ac in a.get("actions", []):
            if ac.get("actionType") != "watUPDATERECORD00":
                continue
            tid = ac.get("tableId")
            for fid in ac.get("fieldsWritten", []):
                writers[(tid, fid)].append((a, ac))

    chains = []
    for a in automations:
        if not a.get("enabled"):
            continue
        triggers = _trigger_field_ids(a, view_filters)
        if not triggers:
            continue
        upstream = []
        for (tid, fid, src) in triggers:
            for (w, _) in writers.get((tid, fid), []):
                if w["id"] == a["id"]:
                    continue
                upstream.append((w, tid, fid, src))
        if upstream:
            chains.append((a, upstream))

    lines = [
        "## Cascade Map",
        "",
        "Automations where a write from one automation could fire another.",
        "Use this to spot blast-radius before changing field values, trigger",
        "views, or watched-fields lists.",
        "",
    ]
    if not chains:
        lines.append("_No automation-to-automation cascades detected._")
        return "\n".join(lines)

    for target, ups in chains:
        ti = target.get("trigInputs") or {}
        tc = target.get("triggerConditions") or {}
        tt = target.get("triggerTypeId")
        tid_trig = ti.get("tableId")
        tname = resolve(tid_trig, table_map, "—")
        lines.append(f"### [{target['name']}]({target['url']}) — fires on {tname}")

        if tt == "wttRECORDUPDATED0":
            wnames = [f"`{resolve_field(tid_trig, f, field_map)}`" for f in tc.get("watchFields") or []]
            lines.append(f"**Watches:** {', '.join(wnames) if wnames else '(any field)'}")
        elif tt == "wttBRZzRXx3C2jyIc":
            vid = ti.get("viewId")
            vf = (view_filters or {}).get(vid) or {}
            ff = vf.get("filterFormula") or vf.get("filterRendered") or "(filter not captured)"
            # Resolve fldXXX (backticked) and selXXX (quoted) to readable names, the
            # same way the per-automation trigger section does — otherwise the cascade
            # map shows opaque IDs while the detail section shows names.
            ff = re.sub(
                r"`(fld[A-Za-z0-9]+)`",
                lambda m: f"`{resolve_field(tid_trig, m.group(1), field_map)}`",
                ff,
            )
            ff = re.sub(
                r'"(sel[A-Za-z0-9]+)"',
                lambda m: f'"{resolve_option(None, m.group(1), choices_map)}"',
                ff,
            )
            lines.append(f"**View filter (via {vid}):** {ff}")
        elif tt == "wttRECORDMATCHES0":
            ff_fields = [f"`{resolve_field(tid_trig, f, field_map)}`" for f in (tc.get("filterFieldIds") or [])]
            lines.append(f"**Filter fields:** {', '.join(sorted(set(ff_fields)))}")

        lines.append("")
        lines.append("**Could be fired by writes from:**")
        seen = set()
        for (w, tid, fid, src) in ups:
            key = (w["id"], fid)
            if key in seen:
                continue
            seen.add(key)
            status = "✓" if w.get("enabled") else "✗ OFF"
            fname = resolve_field(tid, fid, field_map)
            lines.append(f"- [{w['name']}]({w['url']}) ({status}) writes `{fname}`")
        lines.append("")

    return "\n".join(lines)


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
        lines.append(f"| {i} | [{td(name)}]({url}) | {status} | {td(tbl)} | {td(trig_label)} | {email} |")
    return "\n".join(lines)


def section_email_automations(automations, table_map, view_map, field_map,
                              view_filters, choices_map, app_id, form_map=None):
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
            auto, table_map, field_map, view_map, view_filters, choices_map, app_id, form_map)]
        lines.append("")

        # Build a lookup of every node in this automation (action + decision)
        # so render_action can resolve fan-out source references to readable labels.
        actions_by_id = {a.get("id") or f"_unknown_{i}": a
                         for i, a in enumerate(auto.get("actions", []))}
        # The fetch script doesn't include action IDs in each action dict (it returns
        # the values of actionsById, not the keys). Fall back to actionType keying so
        # at least decision label resolution still works for unambiguous types.
        for a in auto.get("actions", []):
            if "id" not in a and a.get("actionType"):
                actions_by_id.setdefault(a["actionType"], a)

        for action in auto.get("actions", []):
            if action["actionType"] not in EMAIL_ACTIONS:
                continue
            to_raw = substitute_field_refs(action.get("toVal", ""), field_map)
            subj_raw = substitute_field_refs(action.get("subjectVal", ""), field_map)
            lines.append(f"- **Action:** {ACTION_LABELS.get(action['actionType'], action['actionType'])}")
            if to_raw:
                lines.append(f"  - To: {classify_recipient(to_raw)}")
            if subj_raw:
                lines.append(f"  - Subject: {subj_raw}")

        other = [a for a in auto.get("actions", []) if a["actionType"] not in EMAIL_ACTIONS]
        if other:
            lines.append("")
            lines.append("**Other actions in this automation:**")
            for j, a in enumerate(other, 1):
                lines.append(render_action(a, table_map, field_map, app_id, j, actions_by_id))
        lines.append("")

    return "\n".join(lines)


def section_per_automation(automations, table_map, view_map, field_map,
                           view_filters, choices_map, app_id, form_map=None):
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
        tbl_name = "Schedule & Button Triggers" if tbl_id == "__no_table__" else resolve(tbl_id, table_map, tbl_id)
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
                auto, table_map, field_map, view_map, view_filters, choices_map, app_id, form_map)]
            if auto.get("description"):
                lines += ["", f"> {auto['description']}"]

            actions = auto.get("actions", [])
            actions_by_id = {a.get("id") or f"_unknown_{i}": a for i, a in enumerate(actions)}
            lines.append("")
            if actions:
                lines.append("**Actions:**")
                for j, a in enumerate(actions, 1):
                    lines.append(render_action(a, table_map, field_map, app_id, j, actions_by_id))
            else:
                lines.append("_No actions captured._")
            lines.append("")

            # Full script bodies for any "Run a script" actions. Kept out of the
            # numbered action list (where code fences nest badly) and shown here as
            # standalone blocks so the reader can see exactly what each script does.
            script_actions = [a for a in actions if a.get("script")]
            if script_actions:
                lines.append("**Scripts:** _(full code extracted to linked files)_")
                for a in script_actions:
                    alabel = ACTION_LABELS.get(a.get("actionType"), "Run script")
                    rel = script_rel_path(name, a.get("id"))
                    chars = a.get("scriptLen", len(a["script"]))
                    lines.append(f"- _{alabel}_ — {chars} chars — [`{rel}`]({rel})")
                    for n, r in render_script_inputs(a, field_map, actions_by_id):
                        lines.append(f"  - input `{n}` ← {r}")
                lines.append("")

    return "\n".join(lines)


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Parse raw automations JSON and write audit doc.")
    parser.add_argument("--raw",          required=True, help="Path to raw_automations.json")
    parser.add_argument("--out",          required=True, help="Output markdown path")
    parser.add_argument("--base-name",    default="Airtable Base", help="Human-readable base name")
    parser.add_argument("--base-id",      required=True, help="Airtable base ID (appXXX)")
    parser.add_argument("--table-map",    default=None, help="JSON file or string: {tableId: tableName}")
    parser.add_argument("--field-map",    default=None, help="JSON file or string: {tableId: {fieldId: fieldName}}")
    parser.add_argument("--view-map",     default=None, help="JSON file or string: {tableId: {viewId: viewName}}")
    parser.add_argument("--view-filters", default=None, help="JSON file: {viewId: {tableId, name, filterFormula|filterRendered, filterRaw}}")
    parser.add_argument("--choices-map",  default=None, help="JSON file or string: {fieldId: {selXXX: optionName}}")
    parser.add_argument("--form-map",     default=None, help="JSON file or string: {formId(pagXXX): formName} — resolves Form-submitted trigger forms")
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
    choices_map = load_json_arg(args.choices_map)
    form_map = load_json_arg(args.form_map)
    app_id = args.base_id

    sections = [
        section_header(args.base_name, app_id, automations),
        "---",
        section_summary_table(automations, table_map, app_id),
        "",
        "---",
        section_email_automations(automations, table_map, view_map, field_map,
                                  view_filters, choices_map, app_id, form_map),
        "",
        "---",
        render_cascade_section(automations, table_map, field_map, view_filters, app_id, choices_map),
        "",
        "---",
        section_per_automation(automations, table_map, view_map, field_map,
                               view_filters, choices_map, app_id, form_map),
    ]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(sections))
    print(f"Wrote {out_path} ({out_path.stat().st_size:,} bytes, {len(automations)} automations)")

    n_scripts = write_script_files(automations, field_map, app_id, out_path.parent)
    if n_scripts:
        print(f"Wrote {n_scripts} script file(s) to {out_path.parent / 'scripts'}/ "
              f"and {out_path.parent / 'scripts.json'}")


if __name__ == "__main__":
    main()
