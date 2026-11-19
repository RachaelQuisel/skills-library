#!/usr/bin/env python3
"""Normalize raw Airtable `workflow/{id}/read` responses into the shape
parse_and_write.py expects.

This is the missing link between Phase 3 (raw capture) and Phase 6 (document build):
the /v0.3 API returns deeply-nested expression trees, while parse_and_write.py expects
flat `{id, name, url, enabled, triggerTypeId, trigInputs, triggerConditions, actions[]}`
records. Run this in between.

Reads (from --dir):  workflow_details_raw.json, view_filters_raw.json,
                     field_map.json, choices_map.json
Writes (to --dir):   automations_normalized.json, view_filters.json

Usage:
    python normalize_workflows.py --dir airtable_audit --base-id appXXXXXXXXXXXXXX
"""
import argparse, json, re
from pathlib import Path

_ap = argparse.ArgumentParser(description=__doc__)
_ap.add_argument("--dir", required=True,
                 help="Audit directory holding the raw captures and ID maps")
_ap.add_argument("--base-id", required=True, help="Airtable base ID (appXXX)")
_args = _ap.parse_args()

D = Path(_args.dir)
APP = _args.base_id

field_map = json.loads((D / "field_map.json").read_text())
choices_map = json.loads((D / "choices_map.json").read_text())
FLAT_FIELDS = {}
for tbl in field_map.values():
    for fid, fname in tbl.items():
        FLAT_FIELDS.setdefault(fid, fname)
FLAT_CHOICES = {}
for ch in choices_map.values():
    FLAT_CHOICES.update(ch)


# ── generic expression-tree renderer ──────────────────────────────────────────

def render(n):
    """Render an Airtable expression node to a readable string."""
    if n is None:
        return ""
    if not isinstance(n, dict):
        return str(n)
    t = n.get("type")

    if t == "literal":
        v = n.get("value")
        if isinstance(v, str) and re.fullmatch(r"fld[A-Za-z0-9]{14}", v):
            return "{field:%s}" % v
        if isinstance(v, str) and v.startswith("sel"):
            return FLAT_CHOICES.get(v, v)
        return "" if v is None else str(v)

    if t == "null":
        return ""

    if t == "template":
        return "".join(render(e) for e in n.get("elements", []))

    if t in ("array", "tuple"):
        parts = [render(e) for e in n.get("elements", [])]
        parts = [p for p in parts if p != ""]
        return ", ".join(parts)

    if t == "object":
        bits = []
        for p in n.get("properties", []):
            k = render(p.get("key"))
            v = render(p.get("value"))
            bits.append(f"{k}: {v}")
        return "{" + ", ".join(bits) + "}"

    if t == "nodeIdentifier":
        if n.get("nodeType") == "trigger":
            return "trigger record"
        return "{node:%s}" % n.get("nodeId")

    if t == "spread":
        return render(n.get("expression"))

    if t == "objectPropertyLookup":
        parts = [(e.get("value") if isinstance(e, dict) else e)
                 for e in (n.get("path") or {}).get("elements", [])]
        # cellValuesByFieldId → fldXXX  is just "this field on the trigger/loop record"
        if len(parts) >= 2 and parts[0] == "cellValuesByFieldId":
            fid = parts[1]
            if isinstance(fid, str) and re.fullmatch(r"fld[A-Za-z0-9]{14}", fid):
                return "{field:%s}" % fid
        obj = render(n.get("object"))
        path = ".".join(str(p) for p in parts)
        # trigger record / loop item plumbing carries no meaning for a reader
        if path in ("selectedNextNodes", "records"):
            return obj
        if path == "id":
            return f"{obj}.recordId" if obj else "{record id}"
        return f"{obj}.{path}" if path else obj

    if t == "functionCall":
        fn = (n.get("function") or {}).get("id", "fn")
        args = n.get("parameters") or []
        # readProperty(X, 'fldXXX')  →  the field itself
        if fn == "readProperty" and len(args) == 2:
            key = args[1]
            kv = key.get("value") if isinstance(key, dict) else None
            if isinstance(kv, str) and re.fullmatch(r"fld[A-Za-z0-9]{14}", kv):
                return "{field:%s}" % kv
            if kv == "cellValuesByFieldId":
                return render(args[0])
            if kv == "id":
                inner = render(args[0])
                return f"{inner}.recordId" if inner else "{record id}"
            return render(args[0])
        # unwrap plumbing that carries no meaning for a reader
        if fn in ("pickBranchData", "toString", "flatten", "first"):
            return render(args[0]) if args else ""
        if fn == "propertyGetter":
            return ""
        if fn == "map" and args:
            return render(args[0])
        rendered = [render(a) for a in args]
        rendered = [r for r in rendered if r != ""]
        return f"{fn}({', '.join(rendered)})" if rendered else f"{fn}()"

    return f"({t})"


def resolve_field_refs(text):
    """Turn {field:fldXXX} placeholders into `Field Name` for standalone strings."""
    if not isinstance(text, str):
        return text
    return re.sub(r"\{field:(fld[A-Za-z0-9]{14})\}",
                  lambda m: "`%s`" % FLAT_FIELDS.get(m.group(1), m.group(1)), text)


def collect_field_ids(n, out):
    """Every fldXXX literal appearing anywhere in a subtree."""
    if isinstance(n, dict):
        v = n.get("value")
        if isinstance(v, str) and re.fullmatch(r"fld[A-Za-z0-9]{14}", v):
            out.add(v)
        for val in n.values():
            collect_field_ids(val, out)
    elif isinstance(n, list):
        for e in n:
            collect_field_ids(e, out)
    return out


def lit(n, default=None):
    """Unwrap a plain {type: literal, value: X} node."""
    if isinstance(n, dict) and n.get("type") == "literal":
        return n.get("value")
    return default


# ── filtersObj → readable formula (for find-records "Find filter") ────────────

def props(node):
    out = {}
    for p in (node or {}).get("properties", []) or []:
        k = (p.get("key") or {}).get("value")
        if k is not None:
            out[k] = p.get("value")
    return out


def fmt_filters(node):
    d = props(node)
    op = lit(d.get("operator"))
    operands = (d.get("operands") or {}).get("elements", []) if isinstance(d.get("operands"), dict) else []
    if op in ("and", "or"):
        return "(" + f" {op.upper()} ".join(fmt_filters(e) for e in operands) + ")"
    if not operands:
        return op or "?"
    fid = lit(operands[0])
    fname = FLAT_FIELDS.get(fid, fid) if isinstance(fid, str) else render(operands[0])
    if len(operands) == 1:
        return f"`{fname}` {op}"
    rest = []
    for o in operands[1:]:
        if isinstance(o, dict) and o.get("type") == "tuple":
            vals = [FLAT_CHOICES.get(lit(e), lit(e)) for e in o.get("elements", [])]
            rest.append("[" + ", ".join(f'"{v}"' for v in vals) + "]")
        elif isinstance(o, dict) and o.get("type") == "object":
            rest.append(render(o))
        elif isinstance(o, dict) and o.get("type") == "literal":
            v = o.get("value")
            v = FLAT_CHOICES.get(v, v) if isinstance(v, str) else v
            rest.append(f'"{v}"' if isinstance(v, str) else json.dumps(v))
        else:
            # array/spread/functionCall operand — render it rather than dropping to null
            rest.append(render(o) or "(expr)")
    return f"`{fname}` {op} " + ", ".join(rest)


# ── N-way branch conditions ───────────────────────────────────────────────────

def fmt_branch(group):
    """Render one branch of a wdtNWAY decision as `Field` op "A", "B"."""
    g = props(group)
    if lit(g.get("hasCondition")) is False:
        return "otherwise (no condition)"
    cond = props(g.get("condition"))
    conj = (lit(cond.get("conjunction")) or "and").upper()
    conds = cond.get("conditions") or {}
    elements = conds.get("elements", []) if isinstance(conds, dict) else []
    parts = []
    for c in elements:
        cp = props(c)
        left = render(cp.get("left"))
        op = lit(cp.get("operator")) or "?"
        right = cp.get("right")
        if isinstance(right, dict) and right.get("type") in ("tuple", "array"):
            vals = [FLAT_CHOICES.get(lit(e), lit(e)) for e in right.get("elements", [])]
            rv = ", ".join(f'"{v}"' for v in vals)
        else:
            v = lit(right)
            v = FLAT_CHOICES.get(v, v) if isinstance(v, str) else v
            rv = f'"{v}"' if isinstance(v, str) else json.dumps(v)
        parts.append(f"{left} {op} {rv}")
    return f" {conj} ".join(parts) or "(no condition captured)"


# ── view filters (filterSet/conjunction shape) ────────────────────────────────

def fmt_view_filter(f):
    if not f:
        return None
    conj = f.get("conjunction", "and").upper()
    parts = []
    for c in f.get("filterSet", []):
        if c.get("type") == "nested":
            parts.append("(" + fmt_view_filter(c) + ")")
            continue
        col = c.get("columnId")
        name = FLAT_FIELDS.get(col, col)
        op = c.get("operator")
        val = c.get("value")
        if val is None:
            parts.append(f"`{name}` {op}")
        elif isinstance(val, dict):
            parts.append(f"`{name}` {op} {json.dumps(val)}")
        elif isinstance(val, str) and val.startswith("sel"):
            parts.append(f'`{name}` {op} "{FLAT_CHOICES.get(val, val)}"')
        else:
            parts.append(f"`{name}` {op} {json.dumps(val)}")
    return f" {conj} ".join(parts)


# ── graph traversal ───────────────────────────────────────────────────────────

def walk(graph):
    """Return node IDs in execution order, descending into decision branches."""
    nodes = graph.get("actionsById") or {}
    order, seen = [], set()

    def visit(nid):
        while nid and nid not in seen:
            n = nodes.get(nid)
            if not n:
                return
            seen.add(nid)
            order.append(nid)
            if n.get("workflowDecisionTypeId"):
                for b in n.get("nextWorkflowNodeIds") or []:
                    visit(b)
                nid = n.get("nextWorkflowNodeId")
            else:
                nid = n.get("nextWorkflowActionId")

    visit(graph.get("entryWorkflowActionId"))
    for nid in nodes:              # anything unreachable from entry
        if nid not in seen:
            visit(nid)
    return order


# ── main ──────────────────────────────────────────────────────────────────────

raw = json.loads((D / "workflow_details_raw.json").read_text())
if isinstance(raw, str):
    raw = json.loads(raw)

automations = []
for entry in raw:
    w = entry["data"]["data"]["workflow"]
    tr = w.get("trigger") or {}
    tie = tr.get("inputExpressions") or {}
    ttype = tr.get("workflowTriggerTypeId")

    trig_inputs = {
        "tableId": lit(tie.get("tableId")),
        "viewId": lit(tie.get("viewId")),
        "cronType": lit(tie.get("type")),
        # wttFORMSUBMITTED0 carries the interface form's page ID here; the parser
        # resolves it to a form name via --form-map.
        "formId": lit(tie.get("formId")),
    }
    trig_cond = {}
    if ttype == "wttRECORDUPDATED0":
        wf = tie.get("watchedFieldIds")
        trig_cond["watchFields"] = [lit(e) for e in (wf or {}).get("elements", [])] if isinstance(wf, dict) else (wf or [])
    if ttype == "wttRECORDMATCHES0" and tie.get("filtersObj"):
        trig_cond["filtersObj"] = tie["filtersObj"]
        trig_cond["filterFieldIds"] = sorted(collect_field_ids(tie["filtersObj"], set()))

    graph = w.get("graph") or {}
    nodes = graph.get("actionsById") or {}
    actions = []
    for nid in walk(graph):
        n = nodes[nid]
        ie = n.get("inputExpressions") or {}
        dec = n.get("workflowDecisionTypeId")
        a = {
            "id": nid,
            "actionType": dec or n.get("workflowActionTypeId"),
            "nodeKind": "decision" if dec else "action",
            "tableId": lit(ie.get("tableId")),
        }
        if ie.get("fields"):
            a["fieldsWritten"] = [
                (p.get("key") or {}).get("value")
                for p in ie["fields"].get("properties", []) or []
            ]
        if ie.get("to"):
            a["toVal"] = render(ie["to"])
        if ie.get("subject"):
            a["subjectVal"] = render(ie["subject"])
        if ie.get("cc"):
            a["ccVal"] = render(ie["cc"])
        if ie.get("fromAddress"):
            a["fromVal"] = render(ie["fromAddress"])
        if ie.get("message"):
            a["messageVal"] = render(ie["message"])
        if ie.get("attachments"):
            a["attachmentsVal"] = render(ie["attachments"])
        script = lit(ie.get("script"))
        if script:
            a["script"] = script
            a["scriptLen"] = len(script)
        if ie.get("inputObj"):
            a["scriptInputs"] = [
                {"name": (p.get("key") or {}).get("value"), "ref": render(p.get("value"))}
                for p in ie["inputObj"].get("properties", []) or []
            ]
        if ie.get("filtersObj"):
            a["filterFormula"] = resolve_field_refs(fmt_filters(ie["filtersObj"]))
        if ie.get("viewId"):
            a["findViewId"] = lit(ie["viewId"])
        if ie.get("prompt"):
            a["promptVal"] = render(ie["prompt"])
        if ie.get("model"):
            a["modelVal"] = lit(ie["model"])
        if ie.get("outputSchema"):
            a["outputSchema"] = render(ie["outputSchema"])
        if ie.get("recipient"):
            a["teamsRecipient"] = render(ie["recipient"])
        if dec == "wdtFANOUT00000000":
            fa = ie.get("fanOutArray") or {}
            obj = fa.get("object") if isinstance(fa, dict) else None
            a["loopOver"] = (obj or {}).get("nodeId")
        if dec == "wdtNWAY0000000000":
            gr = ie.get("groups") or {}
            a["branchCount"] = len(gr.get("elements", []) or [])
            a["branchTargets"] = n.get("nextWorkflowNodeIds") or []
            a["branchConditions"] = [fmt_branch(e) for e in gr.get("elements", []) or []]
        actions.append(a)

    automations.append({
        "id": w["id"],
        "name": w.get("name"),
        "description": w.get("description"),
        "enabled": w.get("deploymentStatus") == "deployed",
        "deploymentStatus": w.get("deploymentStatus"),
        "url": f"https://airtable.com/{APP}/{w['id']}",
        "triggerTypeId": ttype,
        "trigInputs": trig_inputs,
        "triggerConditions": trig_cond,
        "actions": actions,
    })

(D / "automations_normalized.json").write_text(json.dumps(automations, indent=1))

# view filters
vf_raw = json.loads((D / "view_filters_raw.json").read_text())
if isinstance(vf_raw, str):
    vf_raw = json.loads(vf_raw)
view_filters = {}
# The raw capture arrives in one of three shapes depending on how it was made:
#   1. dict keyed by viewId          — what fetch_view_filters.js emits
#   2. list of {id, filters}         — an ad-hoc Promise.all capture
#   3. list of {viewId, filters}     — ditto, different key name
# Normalize all three rather than forcing the caller to match one.
if isinstance(vf_raw, dict):
    vf_items = [dict(v, viewId=k) if isinstance(v, dict) else {"viewId": k}
                for k, v in vf_raw.items()]
else:
    vf_items = vf_raw
for v in vf_items:
    vid = v.get("viewId") or v.get("id")
    if not vid:
        continue
    # fetch_view_filters.js already renders and stores under filterRaw;
    # a raw capture leaves the API's own `filters` key untouched.
    raw = v.get("filterRaw") if v.get("filterRaw") is not None else v.get("filters")
    view_filters[vid] = {
        "filterRendered": v.get("filterRendered") or fmt_view_filter(raw),
        "filterRaw": raw,
    }
(D / "view_filters.json").write_text(json.dumps(view_filters, indent=1))

print(f"normalized {len(automations)} automations, {len(view_filters)} view filters")
for a in automations:
    print(f"  {a['name']}: {len(a['actions'])} nodes, enabled={a['enabled']}")
