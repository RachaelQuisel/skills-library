#!/usr/bin/env python3
"""
Build an Airtable Interfaces audit document from captured raw JSON.

Inputs (all under --raw-dir, captured per the SKILL.md fetch flow):
  readForPages.json        the {msg, data} wrapper from /v0.3/application/{appId}/readForPages
                           (data carries tableSchemas, pageBundles, unparentedPageMetadata,
                            pageSections, workflowTriggerConnectionsById, sharesById)
  all_page_drafts.json     a JSON list of {id, value} — one per page, value is the
                           /v0.3/page/{pageId}/readDraft `data.value` (the page layout)

Optional cross-reference (enables the interface -> automation trigger map):
  --automations PATH       automations_normalized.json produced by the
                           audit-airtable-automations skill (list of automation objects)

Output:
  --out interfaces_audit.md

The document answers, without opening Airtable:
  * What interfaces/pages exist and what each is for.
  * WHERE data can be READ (every element's source table + filters).
  * WHERE data can be MODIFIED (editable grids, editable fields, forms, update/delete buttons).
  * WHICH buttons / form submits / field writes can TRIGGER an automation
    (cross-referenced to the automations audit), i.e. the cascade from clicks into workflows.
  * How pages link to each other (navigation / expanded-row / form redirects).

No network calls. Pure transform of the captured JSON.
"""
import argparse, json, os, re, sys
from collections import defaultdict, Counter

# ---------------------------------------------------------------- load helpers

def load_json_maybe_double(path):
    """Load JSON; tolerate a value that was JSON-encoded one or more extra times."""
    with open(path) as f:
        d = json.load(f)
    while isinstance(d, str):
        d = json.loads(d)
    return d

def load_drafts(path):
    """all_page_drafts.json -> {pageId: layoutValue}."""
    d = load_json_maybe_double(path)
    out = {}
    for r in d:
        if not isinstance(r, dict):
            continue
        v = r.get("value")
        if v:
            out[r["id"]] = v
    return out

# ------------------------------------------------------------------- ID maps

class Resolver:
    def __init__(self, data):
        self.table = {}          # tblXXX -> name
        self.field = {}          # fldXXX -> name
        self.field_table = {}    # fldXXX -> tblXXX
        self.choice = {}         # selXXX -> name
        self.page = {}           # pagXXX -> name
        self.workflow = {}       # wflXXX -> name (filled later if automations given)
        for t in data.get("tableSchemas", []):
            self.table[t["id"]] = t.get("name", t["id"])
            for c in (t.get("columns") or t.get("fields") or []):
                self.field[c["id"]] = c.get("name", c["id"])
                self.field_table[c["id"]] = t["id"]
                opts = ((c.get("typeOptions") or {}).get("choices")
                        or (c.get("options") or {}).get("choices"))
                if isinstance(opts, dict):
                    for sid, o in opts.items():
                        self.choice[sid] = (o or {}).get("name", sid)
                elif isinstance(opts, list):
                    for o in opts:
                        if isinstance(o, dict) and o.get("id"):
                            self.choice[o["id"]] = o.get("name", o["id"])

    def t(self, tid):
        if not tid: return "—"
        return self.table.get(tid, f"⚠️DELETED TABLE ({tid})")

    def f(self, fid):
        if not fid: return "—"
        return self.field.get(fid, f"⚠️DELETED FIELD ({fid})")

    def c(self, sid):
        if sid is None: return "—"
        if isinstance(sid, bool): return str(sid).lower()
        if isinstance(sid, list):
            return ", ".join(self.c(x) for x in sid)
        # A filter value can be a structured object (date-relative modes, linked-record
        # specs) nested inside a list, which never reaches render_leaf's dict branch.
        # Keep c() total so an unhashable value can't crash the whole build.
        if isinstance(sid, dict):
            if "mode" in sid: return str(sid.get("mode"))
            return json.dumps(sid, sort_keys=True)[:60]
        if not isinstance(sid, str): return str(sid)
        return self.choice.get(sid, sid)

    def p(self, pid):
        if not pid: return "—"
        return self.page.get(pid, pid)

    def w(self, wid):
        return self.workflow.get(wid, wid)

    # --- hyperlink helpers (base_id is set on the instance in main) ---
    def page_link(self, pid):
        if not pid: return "—"
        return f"[{md_escape(self.p(pid))}](https://airtable.com/{self.base_id}/{pid})"

    def wf_link(self, wid):
        if not wid: return "—"
        return f"[{md_escape(self.w(wid))}](https://airtable.com/{self.base_id}/{wid})"

# --------------------------------------------------------------- filter AST

def render_filters(flt, R):
    """Render a {conjunction, filterSet:[...]} expression (the page/view variant)."""
    if not flt or not isinstance(flt, dict):
        return ""
    conj = flt.get("conjunction", "and")
    parts = []
    for leaf in flt.get("filterSet", []):
        if leaf.get("type") == "nested" or "filterSet" in leaf:
            inner = render_filters(leaf, R)
            if inner:
                parts.append(f"({inner})")
            continue
        col = R.f(leaf.get("columnId"))
        op = leaf.get("operator", "?")
        val = leaf.get("value", None)
        parts.append(render_leaf(col, op, val, R))
    sep = f" {conj.upper()} "
    return sep.join(p for p in parts if p)

def render_leaf(col, op, val, R):
    if val is None:
        return f"`{col}` {op}"
    if isinstance(val, dict):
        # date-relative or special
        if "mode" in val:
            mode = val.get("mode")
            if mode == "withinExactDates":
                return f"`{col}` {op} {val.get('fromExactDate','?')[:10]}..{val.get('toExactDate','?')[:10]}"
            if mode == "daysAgo":
                return f"`{col}` {op} daysAgo({val.get('numberOfDays')})"
            return f"`{col}` {op} {mode}"
        return f"`{col}` {op} {json.dumps(val)[:60]}"
    return f"`{col}` {op} {R.c(val)!r}"

# ------------------------------------------------------ element introspection

# element types that primarily READ a single table's data
CONTAINER_TYPES = {"grid", "kanban", "gallery", "calendar", "levels", "queryContainer",
                   "blockInstallationInQueryContainer"}
# element types that READ for a chart / number (no row interaction)
VIZ_TYPES = {"bigNumber", "chart", "pivotTable", "dashboard"}

def element_source_table(el):
    """Best-effort: which tableId this element reads from."""
    if "leafTableId" in el and el["leafTableId"]:
        return el["leafTableId"]
    src = el.get("source")
    if isinstance(src, dict):
        if src.get("tableId"):
            return src["tableId"]
        q = src.get("query")
        if isinstance(q, dict) and q.get("tableId"):
            return q["tableId"]
    q = el.get("query")
    if isinstance(q, dict):
        s = q.get("source")
        if isinstance(s, dict):
            if s.get("tableId"):
                return s["tableId"]
            qq = s.get("query")
            if isinstance(qq, dict) and qq.get("tableId"):
                return qq["tableId"]
    # levels: queryByLevel
    qbl = el.get("queryByLevel")
    if isinstance(qbl, dict):
        for lvl in qbl.values():
            if isinstance(lvl, dict):
                s = lvl.get("source")
                if isinstance(s, dict):
                    if s.get("tableId"): return s["tableId"]
                    qq = s.get("query")
                    if isinstance(qq, dict) and qq.get("tableId"): return qq["tableId"]
    return None

def element_editability(el):
    """Return (canEditCells, canCreate, canDelete) booleans or None if not applicable."""
    e = el.get("editability")
    if not isinstance(e, dict):
        return None
    return (bool(e.get("canUpdateAllVisibleCells")),
            bool(e.get("canCreateRowsInline")),
            bool(e.get("canDestroyRows")))

def editable_columns(el):
    """For an inline-editable grid (canUpdateAllVisibleCells), the visible/editable columns."""
    lc = el.get("levelsConfig") or {}
    leaf = lc.get("leafLevel") or {}
    cols = leaf.get("allOrderedDisplayColumnIds")
    if isinstance(cols, list):
        return cols
    for k in ("visibleColumnOrder", "columnOrder", "allColumnIds", "visibleColumnIds"):
        v = el.get(k)
        if isinstance(v, list):
            return v
    return []

def expanded_row_pages(el):
    """levels/grid expandedRowByTableId -> list of (tableId, pageId)."""
    out = []
    erb = el.get("expandedRowByTableId")
    if isinstance(erb, dict):
        for tid, cfg in erb.items():
            if isinstance(cfg, dict) and cfg.get("pageId"):
                out.append((tid, cfg["pageId"]))
    er = el.get("expandedRow")
    if isinstance(er, dict) and er.get("pageId"):
        out.append((None, er["pageId"]))
    return out

# ------------------------------------------------------------- button actions

URL_PAGE_RE = re.compile(r"/(pag[A-Za-z0-9]{14})")

def describe_button_action(el, page_id, R, wf_conn):
    """Return a dict describing a button's action in resolved terms."""
    a = el.get("action") or {}
    t = a.get("type")
    d = {"actionType": t}
    if t == "triggerWorkflow":
        wid = wf_conn.get((page_id, el["id"]))
        d["workflowId"] = wid
        d["workflow"] = R.w(wid) if wid else None
        rt = (a.get("rowInput") or {}).get("tableId")
        d["onTable"] = rt
    elif t == "updateRow":
        sets = []
        for u in a.get("columnUpdateSet", []):
            sets.append((u.get("columnId"), u.get("value"), u.get("updateBehavior", "set")))
        d["sets"] = sets
        d["onTable"] = (a.get("rowInput") or {}).get("tableId")
    elif t == "deleteRow":
        d["onTable"] = (a.get("rowInput") or {}).get("tableId")
    elif t == "navigateToSelectedPage":
        d["targetPage"] = a.get("selectedPageId")
        d["newWindow"] = a.get("shouldOpenInNewWindow")
    elif t == "navigateToStaticUrl":
        url = a.get("url", "")
        d["url"] = url
        m = URL_PAGE_RE.search(url or "")
        d["targetPage"] = m.group(1) if m else None
        d["isForm"] = url.endswith("/form")
    elif t == "openFormModalDialog":
        efb = a.get("embeddedFormButton") or {}
        d["targetPage"] = efb.get("pageId")
        d["onTable"] = a.get("tableId")
        d["formType"] = efb.get("type")
    elif t == "addForeignRow":
        efb = a.get("embeddedFormButton") or {}
        d["targetPage"] = efb.get("pageId")
        d["onTable"] = a.get("tableId")
        d["foreignColumn"] = a.get("foreignColumnId")
    return d

# ------------------------------------------------------- automation indexing

def build_automation_index(autos, R):
    """
    Build cross-reference indexes from normalized automations.
    Returns dict with:
      by_form:        {formPageId: [autos]}
      by_field_write: {(tableId, fieldId): [autos]}   (watch + filter fields)
      by_table_create:{tableId: [autos]}              (created / any-match triggers)
      by_id:          {wflId: auto}
    Also populates R.workflow names.
    """
    idx = {"by_form": defaultdict(list), "by_field_write": defaultdict(list),
           "by_table_create": defaultdict(list),         # record-created ONLY (inline create)
           "by_table_match": defaultdict(list),           # record-matches / enters-view (may fire on create)
           "by_table_any_update": defaultdict(list),      # record-updated watching ANY field
           "by_id": {}}
    for a in autos or []:
        R.workflow[a.get("id")] = a.get("name", a.get("id"))
        idx["by_id"][a.get("id")] = a
        ti = a.get("trigInputs") or {}
        tc = a.get("triggerConditions") or {}
        tid = ti.get("tableId")
        ttype = a.get("triggerTypeId")
        if ti.get("formId"):
            idx["by_form"][ti["formId"]].append(a)
        # Inline grid / embedded-form record creation fires Record-created automations only.
        # Form-submitted automations fire solely from their own form page (handled via by_form).
        if tid and ttype == "wttRECORDCREATED0":
            idx["by_table_create"][tid].append(a)
        if tid and ttype in ("wttRECORDMATCHES0", "wttBRZzRXx3C2jyIc"):
            idx["by_table_match"][tid].append(a)
        if tid:
            fids = set(tc.get("watchFields") or []) | set(tc.get("filterFieldIds") or [])
            # record-updated with no watched fields = any field; record-matches w/ filter fields
            for fid in fids:
                idx["by_field_write"][(tid, fid)].append(a)
            # a bare "record updated, any field" automation triggers on ANY write to the table
            if ttype == "wttRECORDUPDATED0" and not tc.get("watchFields"):
                idx["by_table_any_update"][tid].append(a)
    return idx

def autos_for_field_write(idx, tid, fid):
    res = list(idx["by_field_write"].get((tid, fid), []))
    for a in idx.get("by_table_any_update", {}).get(tid, []):
        if a not in res:
            res.append(a)
    return res

# ------------------------------------------------------------------- inventory

def build_inventory(data):
    """Return ordered list of bundles with their pages, plus unparented (form/record) pages."""
    bundles = []
    for b in data.get("pageBundles", []):
        pages = []
        for p in b.get("pages", []):
            md = p.get("metadata") or {}
            pages.append({
                "id": p["id"], "name": md.get("name"),
                "layout": (p.get("pageLayoutTypeInfo") or {}).get("pageLayoutType"),
                "published": p.get("isPublished"),
                "hidden": md.get("isHiddenFromNavigation"),
                "navType": md.get("type"),
            })
        bundles.append({"id": b["id"], "name": b.get("name"), "icon": b.get("icon"),
                        "description": b.get("description"), "pages": pages})
    unparented = []
    for p in data.get("unparentedPageMetadata", []):
        md = p.get("metadata") or {}
        unparented.append({
            "id": p["id"], "name": md.get("name"),
            "layout": (p.get("pageLayoutTypeInfo") or {}).get("pageLayoutType"),
            "published": p.get("isPublished"),
            "formSourceTableId": p.get("formSourceTableIdIfExists"),
            "redirect": md.get("formPostSubmissionRedirectUrl"),
        })
    return bundles, unparented

# ------------------------------------------------------------------- page scan

def scan_page(pid, layout, R, wf_conn):
    """Extract everything interesting from one page layout."""
    info = {"id": pid, "rootTable": None, "reads": [], "writes": [],
            "buttons": [], "links": [], "forms": []}
    if not isinstance(layout, dict):
        return info
    rrc = layout.get("rootRowContainer")
    if isinstance(rrc, dict):
        info["rootTable"] = rrc.get("tableId")
    ebi = layout.get("elementById") or {}
    for eid, el in ebi.items():
        t = el.get("type")
        if t == "button":
            info["buttons"].append({"id": eid, "text": el.get("buttonText"),
                                    "color": el.get("colorTheme"),
                                    "confirm": el.get("confirmationModalMessage"),
                                    "visibility": el.get("visibilityFilters"),
                                    **describe_button_action(el, pid, R, wf_conn)})
        elif t == "formContainer":
            act = el.get("action") or {}
            info["forms"].append({"id": eid, "title": el.get("title"),
                                  "action": act.get("type"), "tableId": act.get("tableId"),
                                  "required": el.get("requiredColumnIds") or [],
                                  "prefilled": list((el.get("prefilledCellValueByColumnId") or {}).keys()),
                                  "buttonLabel": el.get("buttonLabel")})
        elif t in CONTAINER_TYPES:
            src = element_source_table(el)
            edit = element_editability(el)
            entry = {"elementType": t, "tableId": src, "edit": edit,
                     "filters": el.get("staticFilters"),
                     "endUser": el.get("endUserControls"),
                     "label": (el.get("label") or {}).get("value")}
            info["reads"].append(entry)
            if edit and any(edit):
                info["writes"].append({"via": t, "tableId": src,
                                       "cells": edit[0], "create": edit[1], "delete": edit[2]})
                # enumerate the editable columns of an inline-editable grid as Table.Field
                if edit[0] and src:
                    for cid in editable_columns(el):
                        info["writes"].append({"via": "gridCell", "tableId": src, "fieldId": cid})
            for tid, tgt in expanded_row_pages(el):
                info["links"].append({"kind": "expandRow", "tableId": tid or src, "targetPage": tgt})
        elif t in VIZ_TYPES:
            src = element_source_table(el)
            if src:
                info["reads"].append({"elementType": t, "tableId": src, "edit": None,
                                      "label": el.get("descriptionText") or (el.get("label") or {}).get("value")})
        elif t == "cellEditor":
            srow = el.get("source") or {}
            tid = (srow.get("row") or {}).get("tableId")
            cid = srow.get("columnId")
            if not el.get("isReadOnly", False) and tid and cid:
                info["writes"].append({"via": "cellEditor", "tableId": tid, "fieldId": cid})
    return info

# --------------------------------------------------------------------- render

def md_escape(s):
    if s is None: return ""
    return str(s).replace("|", "\\|").replace("\n", " ").strip()

def alink(a, R):
    """Markdown link to an automation, given a normalized automation dict."""
    url = a.get("url") or f"https://airtable.com/{R.base_id}/{a.get('id')}"
    return f"[{md_escape(a.get('name'))}]({url})"

def connected_automations(pid, s, idx, R):
    """
    Automations DIRECTLY connected to a page's controls:
      - triggerWorkflow buttons  -> their workflow
      - updateRow buttons        -> automations watching the written field
      - form submit (form page)  -> form-submitted automations
    Returns a deduped list of automation-like dicts ({id, name, url}).
    """
    seen, out = set(), []
    def add(a):
        if a and a.get("id") and a["id"] not in seen:
            seen.add(a["id"]); out.append(a)
    for b in s["buttons"]:
        if b["actionType"] == "triggerWorkflow" and b.get("workflowId"):
            wid = b["workflowId"]
            add(idx["by_id"].get(wid) or
                {"id": wid, "name": R.w(wid), "url": f"https://airtable.com/{R.base_id}/{wid}"})
        elif b["actionType"] == "updateRow":
            tid = b.get("onTable")
            for cid, _v, _beh in b.get("sets", []):
                for a in autos_for_field_write(idx, tid, cid):
                    add(a)
    for a in idx["by_form"].get(pid, []):
        add(a)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", required=True)
    ap.add_argument("--automations", default=None)
    ap.add_argument("--base-name", default="")
    ap.add_argument("--base-id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--date", default="")
    args = ap.parse_args()

    rfp = load_json_maybe_double(os.path.join(args.raw_dir, "readForPages.json"))
    data = rfp.get("data", rfp)
    drafts = load_drafts(os.path.join(args.raw_dir, "all_page_drafts.json"))

    R = Resolver(data)
    R.base_id = args.base_id
    # page names from inventory
    bundles, unparented = build_inventory(data)
    for b in bundles:
        for p in b["pages"]:
            R.page[p["id"]] = p["name"] or p["id"]
    for p in unparented:
        R.page[p["id"]] = p["name"] or p["id"]

    # workflow button connections: (pageId, buttonElementId) -> workflowId
    wf_conn = {}
    wf_conn_all = data.get("workflowTriggerConnectionsById") or {}
    for cid, c in wf_conn_all.items():
        si = c.get("sourceIdentifier") or {}
        if c.get("type") == "pageButtonElement" and si.get("pageId") and si.get("buttonElementId"):
            wf_conn[(si["pageId"], si["buttonElementId"])] = c.get("workflowId")

    autos = None
    if args.automations and os.path.exists(args.automations):
        autos = load_json_maybe_double(args.automations)
    idx = build_automation_index(autos, R)

    # scan every page we have a layout for
    scans = {pid: scan_page(pid, lay, R, wf_conn) for pid, lay in drafts.items()}

    # friendlier names for unnamed record-detail pages: use their record table
    for pid, s in scans.items():
        cur = R.page.get(pid)
        if (not cur or cur == pid) and s.get("rootTable"):
            R.page[pid] = f"{R.t(s['rootTable'])} detail ({pid[:8]}…)"

    # page -> bundle name
    page_bundle = {}
    for b in bundles:
        for p in b["pages"]:
            page_bundle[p["id"]] = b["name"]
    page_meta = {}
    for b in bundles:
        for p in b["pages"]:
            page_meta[p["id"]] = p
    for p in unparented:
        page_meta[p["id"]] = p

    out = []
    W = out.append
    bn = args.base_name or args.base_id
    W(f"# {bn} — Interfaces Audit\n")
    if args.date:
        W(f"**Date:** {args.date}  ")
    W(f"**Base:** `{args.base_id}` ([open](https://airtable.com/{args.base_id}))  ")
    W(f"**Scope:** Every interface (page bundle), every page, every data element, "
      f"every button/action, and how interface actions trigger automations.\n")

    # ---- summary counts
    total_pages = len(drafts)
    btn_actions = Counter()
    write_pages = set()
    read_tables = set()
    trigger_buttons = 0
    for pid, s in scans.items():
        for b in s["buttons"]:
            btn_actions[b["actionType"]] += 1
            if b["actionType"] == "triggerWorkflow":
                trigger_buttons += 1
        if s["writes"]:
            write_pages.add(pid)
        for r in s["reads"]:
            if r.get("tableId"): read_tables.add(r["tableId"])

    W("## Summary\n")
    W(f"- **{len(bundles)} interfaces** (page bundles), **{total_pages} pages** "
      f"with captured layouts.")
    layout_counts = Counter()
    for pid in drafts:
        pm = page_meta.get(pid, {})
        layout_counts[pm.get("layout", "?")] += 1
    W(f"- Page layout types: " + ", ".join(f"{k} ({v})" for k, v in layout_counts.most_common()) + ".")
    W(f"- **{sum(btn_actions.values())} buttons.** Action mix: "
      + ", ".join(f"`{k}` ({v})" for k, v in btn_actions.most_common()) + ".")
    W(f"- **{len(write_pages)} pages expose a write surface** (editable cell, inline create/delete, "
      f"form, or update/delete button).")
    if autos is not None:
        W(f"- Cross-referenced against **{len(autos)} automations** "
          f"(from the automations audit) to map clicks → workflows.")
    W("")

    # ---- interface inventory
    W("## 1. Interface inventory\n")
    W("Each **interface** (page bundle) groups pages shown in the left nav of the published app. "
      "`HIDDEN` = present but hidden from navigation; `UNPUB` = has never been published / "
      "unpublished draft.\n")
    for b in bundles:
        W(f"### {md_escape(b['name'])}  ·  `{b['id']}`")
        if b.get("description"):
            W(f"_{md_escape(b['description'])}_\n")
        if not b["pages"]:
            W("_(no pages)_\n")
            continue
        W("| Page | Layout | Status | Page ID |")
        W("|---|---|---|---|")
        for p in b["pages"]:
            flags = []
            if not p["published"]: flags.append("UNPUB")
            if p["hidden"]: flags.append("HIDDEN")
            W(f"| {R.page_link(p['id'])} | {p['layout']} | {' '.join(flags) or 'live'} | `{p['id']}` |")
        W("")

    # ---- forms & record pages (unparented)
    W("### Forms & record-detail pages (not in left nav)\n")
    forms = [p for p in unparented if p["layout"] == "formContainer"]
    recs = [p for p in unparented if p["layout"] == "recordContainer"]
    W(f"**{len(forms)} form pages** (standalone data-entry; each writes to one table) and "
      f"**{len(recs)} record-detail pages** (open when a row is expanded; hold field editors and buttons).\n")
    W("| Form page | Writes to table | Published | Post-submit redirect |")
    W("|---|---|---|---|")
    for p in sorted(forms, key=lambda x: (x["name"] or "")):
        red = p.get("redirect") or ""
        m = URL_PAGE_RE.search(red or "")
        red_disp = f"→ {md_escape(R.p(m.group(1)))}" if m else ""
        W(f"| {R.page_link(p['id'])} | {md_escape(R.t(p['formSourceTableId']))} | "
          f"{'yes' if p['published'] else 'no'} | {red_disp} |")
    W("")

    # ---- THE HEADLINE: interface -> automation trigger map
    W("## 2. Interface → automation trigger map\n")
    W("The point of this section: **which interface actions can set off an automation.** "
      "Four paths exist.\n")

    # 2a button triggerWorkflow
    W("### 2a. Buttons that directly run a workflow (`triggerWorkflow`)\n")
    W("These buttons are wired straight to an automation via a workflow-trigger connection.\n")
    W("| Page | Button | Runs automation | On table | Connection |")
    W("|---|---|---|---|---|")
    tw_rows = 0
    for pid, s in scans.items():
        for b in s["buttons"]:
            if b["actionType"] != "triggerWorkflow":
                continue
            tw_rows += 1
            wid = b.get("workflowId")
            conn = "✅" if wid else "⚠️ NO CONNECTION (broken/needs publish)"
            wf_disp = R.wf_link(wid) if wid else "—"
            W(f"| {R.page_link(pid)} | {md_escape(b['text'])} | {wf_disp} | "
              f"{md_escape(R.t(b.get('onTable')))} | {conn} |")
    if not tw_rows:
        W("| _none_ | | | | |")
    W("")

    # 2b form submits
    W("### 2b. Form submissions that trigger an automation (`Form submitted`)\n")
    if autos is not None:
        W("Form pages whose submit fires a `wttFORMSUBMITTED0` automation.\n")
        W("| Form page | Writes to | Triggers automation |")
        W("|---|---|---|")
        any_form = False
        for p in sorted(forms, key=lambda x: (x["name"] or "")):
            hits = idx["by_form"].get(p["id"], [])
            if hits:
                any_form = True
                W(f"| {R.page_link(p['id'])} | {md_escape(R.t(p['formSourceTableId']))} | "
                  + "; ".join(alink(a, R) for a in hits) + " |")
        if not any_form:
            W("| _no form-submit automations matched_ | | |")
        W("")
    else:
        W("_(automations not supplied — re-run with `--automations` to populate)_\n")

    # 2c updateRow buttons that write trigger fields
    W("### 2c. Buttons that write a field watched by an automation (`updateRow`)\n")
    W("Each row sets a field to a value; if an automation watches/matches that field on that "
      "table, the click cascades into it.\n")
    W("| Page | Button | Sets | Cascades into automation(s) |")
    W("|---|---|---|---|")
    ur_rows = 0
    for pid, s in scans.items():
        for b in s["buttons"]:
            if b["actionType"] != "updateRow":
                continue
            ur_rows += 1
            tid = b.get("onTable")
            setdesc = []
            casc, casc_ids = [], set()
            for cid, val, beh in b.get("sets", []):
                setdesc.append(f"`{R.f(cid)}` = {R.c(val)}")
                if autos is not None:
                    for a in autos_for_field_write(idx, tid, cid):
                        if a["id"] not in casc_ids:
                            casc_ids.add(a["id"]); casc.append(a)
            W(f"| {R.page_link(pid)} | {md_escape(b['text'])} | {md_escape('; '.join(setdesc))} | "
              + ("; ".join(alink(a, R) for a in casc) if casc else "_(none detected)_") + " |")
    if not ur_rows:
        W("| _none_ | | | |")
    W("")

    # 2d editable surfaces on tables with create/update triggers
    W("### 2d. Editable grids / inline create that can fire create/update automations\n")
    W("Inline-editable elements and forms that create rows on tables which have `Record created`, "
      "`Record matches conditions`, `Record enters view`, or any-field `Record updated` automations. "
      "Match/enters-view automations also fire on creation when the new row meets the filter, so they "
      "are listed here as possibilities.\n")
    W("| Page | Surface | Table | Op | Possible automation(s) |")
    W("|---|---|---|---|---|")
    ed_rows = 0
    for pid, s in scans.items():
        for w in s["writes"]:
            tid = w.get("tableId")
            if not tid:
                continue
            ops = []
            autohits = []
            if w["via"] == "cellEditor":
                continue  # covered by per-page detail; too granular here
            if w.get("create"):
                ops.append("create")
                autohits += idx["by_table_create"].get(tid, [])
                autohits += idx["by_table_match"].get(tid, [])
            if w.get("cells"):
                ops.append("edit-cells")
                autohits += idx.get("by_table_any_update", {}).get(tid, [])
                autohits += idx["by_table_match"].get(tid, [])
            if w.get("delete"):
                ops.append("delete")
            if not ops:
                continue
            uniq, uids = [], set()
            for a in autohits:
                if a["id"] not in uids:
                    uids.add(a["id"]); uniq.append(a)
            ed_rows += 1
            W(f"| {R.page_link(pid)} | {w['via']} | {md_escape(R.t(tid))} | {', '.join(ops)} | "
              + ("; ".join(alink(a, R) for a in uniq) if uniq else "_(none detected)_") + " |")
        for fm in s["forms"]:
            tid = fm.get("tableId")
            if not tid:
                continue
            hits = []
            if fm.get("action") == "createRow":
                hits = idx["by_table_create"].get(tid, []) + idx["by_table_match"].get(tid, [])
                hits = hits + idx["by_form"].get(pid, [])
            ed_rows += 1
            uniq, uids = [], set()
            for a in hits:
                if a["id"] not in uids:
                    uids.add(a["id"]); uniq.append(a)
            W(f"| {R.page_link(pid)} | embedded form | {md_escape(R.t(tid))} | {fm.get('action')} | "
              + ("; ".join(alink(a, R) for a in uniq) if uniq else "_(none detected)_") + " |")
    if not ed_rows:
        W("| _none_ | | | | |")
    W("")

    # ---- data read/write surface matrix
    W("## 3. Data read/write surface by page\n")
    W("One row per page. **Editable fields** are qualified as `Table.Field` (from record-field "
      "editors and inline-editable grid columns); row-level grid/form permissions are tagged "
      "`[+create]` / `[+delete]` / `FORM-createRow`. **Directly-connected automations** are those "
      "this page's buttons or form submit can fire (paths 2a–2c) — each links to the workflow.\n")
    W("| Page | Bundle | Reads tables | Editable fields (`Table.Field`) | Directly-connected automations |")
    W("|---|---|---|---|---|")
    FIELD_CAP = 14  # keep the cell readable; full list is in section 5
    for pid, s in scans.items():
        pm = page_meta.get(pid, {})
        reads = sorted({R.t(r["tableId"]) for r in s["reads"] if r.get("tableId")})

        # editable fields grouped by table (cellEditor + inline-grid columns), de-duped, ordered
        ef_by_tbl = {}
        for w in s["writes"]:
            if w["via"] in ("cellEditor", "gridCell") and w.get("fieldId"):
                ef_by_tbl.setdefault(w["tableId"], [])
                if w["fieldId"] not in ef_by_tbl[w["tableId"]]:
                    ef_by_tbl[w["tableId"]].append(w["fieldId"])
        # row-level permissions / forms as annotations
        rowops = {}  # tableId -> set of tags
        for w in s["writes"]:
            if w["via"] in CONTAINER_TYPES:
                tags = rowops.setdefault(w["tableId"], set())
                if w.get("create"): tags.add("+create")
                if w.get("delete"): tags.add("+delete")
        form_notes = [f"{R.t(fm['tableId'])}: FORM-{fm.get('action')}" for fm in s["forms"]]

        ef_cells = []
        for tid, fids in ef_by_tbl.items():
            tname = R.t(tid)
            shown = fids[:FIELD_CAP]
            frag = ", ".join(f"{tname}.{R.f(c)}" for c in shown)
            if len(fids) > FIELD_CAP:
                frag += f" (+{len(fids)-FIELD_CAP} more)"
            ann = rowops.get(tid)
            if ann:
                frag += f" `[{' '.join(sorted(ann))}]`"
            ef_cells.append(frag)
        # tables that allow create/delete but expose no named editable fields
        for tid, tags in rowops.items():
            if tid not in ef_by_tbl:
                ef_cells.append(f"{R.t(tid)} `[{' '.join(sorted(tags))}]`")
        ef_cells.extend(form_notes)

        conn = connected_automations(pid, s, idx, R)
        conn_disp = "; ".join(alink(a, R) for a in conn) if conn else "—"

        bcol = page_bundle.get(pid) or f"({pm.get('layout','?').replace('Container','')})"
        W(f"| {R.page_link(pid)} | {md_escape(bcol)} | {md_escape(', '.join(reads) or '—')} | "
          f"{md_escape('; '.join(ef_cells) or 'read-only')} | {conn_disp} |")
    W("")

    # ---- navigation map
    W("## 4. Page navigation map\n")
    W("How a user moves between pages: row-expand into a detail page, button navigation, "
      "embedded-form buttons, and form post-submit redirects.\n")
    W("| From page | Via | To page |")
    W("|---|---|---|")
    nav_rows = 0
    for pid, s in scans.items():
        for l in s["links"]:
            nav_rows += 1
            W(f"| {R.page_link(pid)} | expand {md_escape(R.t(l['tableId']))} row | "
              f"{R.page_link(l['targetPage'])} |")
        for b in s["buttons"]:
            tgt = b.get("targetPage")
            if b["actionType"] in ("navigateToSelectedPage", "navigateToStaticUrl",
                                   "openFormModalDialog", "addForeignRow") and tgt:
                nav_rows += 1
                via = {"navigateToSelectedPage": "button (nav)",
                       "navigateToStaticUrl": "button (link)",
                       "openFormModalDialog": "button (embedded form)",
                       "addForeignRow": "button (add linked)"}[b["actionType"]]
                W(f"| {R.page_link(pid)} | {via}: {md_escape(b['text'])} | {R.page_link(tgt)} |")
    for p in unparented:
        red = p.get("redirect")
        if red:
            m = URL_PAGE_RE.search(red)
            if m:
                nav_rows += 1
                W(f"| {R.page_link(p['id'])} (form) | post-submit redirect | {R.page_link(m.group(1))} |")
    if not nav_rows:
        W("| _none_ | | |")
    W("")

    # ---- per-page detail
    W("## 5. Per-page detail\n")
    # order: bundles then unparented
    ordered = []
    for b in bundles:
        for p in b["pages"]:
            if p["id"] in scans:
                ordered.append((p["id"], b["name"]))
    for p in unparented:
        if p["id"] in scans:
            ordered.append((p["id"], "(form/record)"))
    for pid, bname in ordered:
        s = scans[pid]
        pm = page_meta.get(pid, {})
        W(f"### {R.page_link(pid)}  ·  `{pid}`")
        meta_bits = [f"bundle: {bname}", f"layout: {pm.get('layout','?')}"]
        if s["rootTable"]:
            meta_bits.append(f"record table: {R.t(s['rootTable'])}")
        if pm.get("published") is False:
            meta_bits.append("**UNPUBLISHED**")
        W("_" + " · ".join(meta_bits) + "_  \n")
        W(f"[open in Airtable](https://airtable.com/{args.base_id}/{pid})\n")

        if s["reads"]:
            W("**Reads:**")
            for r in s["reads"]:
                lbl = f" — _{md_escape(r['label'])}_" if r.get("label") else ""
                ed = ""
                if r.get("edit") and any(r["edit"]):
                    flags = []
                    if r["edit"][0]: flags.append("edit-cells")
                    if r["edit"][1]: flags.append("create")
                    if r["edit"][2]: flags.append("delete")
                    ed = f" **[{', '.join(flags)}]**"
                filt = ""
                if r.get("filters"):
                    fexpr = render_filters(r["filters"], R)
                    if fexpr:
                        filt = f" — filter: {fexpr}"
                W(f"- `{r['elementType']}` → **{md_escape(R.t(r['tableId']))}**{ed}{lbl}{filt}")
            W("")
        if s["forms"]:
            W("**Form(s):**")
            for fm in s["forms"]:
                req = ", ".join(R.f(c) for c in fm["required"]) or "none"
                W(f"- _{md_escape(fm['title'])}_ → {fm.get('action')} on **{md_escape(R.t(fm['tableId']))}** "
                  f"(submit: “{md_escape(fm.get('buttonLabel'))}”; required: {md_escape(req)})")
            W("")
        if s["buttons"]:
            W("**Buttons:**")
            for b in s["buttons"]:
                W("- " + render_button_line(b, R))
            W("")
        # editable fields list (record-field editors + inline-grid columns), as Table.Field
        ef_by_tbl = {}
        for w in s["writes"]:
            if w["via"] in ("cellEditor", "gridCell") and w.get("fieldId"):
                ef_by_tbl.setdefault(w["tableId"], [])
                if w["fieldId"] not in ef_by_tbl[w["tableId"]]:
                    ef_by_tbl[w["tableId"]].append(w["fieldId"])
        if ef_by_tbl:
            total_ef = sum(len(v) for v in ef_by_tbl.values())
            W(f"**Editable fields ({total_ef}):**")
            for tid, fids in ef_by_tbl.items():
                names = ", ".join(f"{R.t(tid)}.{R.f(c)}" for c in fids)
                W(f"- {md_escape(names)}")
            W("")
        W("")

    with open(args.out, "w") as f:
        f.write("\n".join(out))
    print(f"Wrote {args.out}  ({len(out)} lines)")
    print(f"  interfaces={len(bundles)} pages={total_pages} buttons={sum(btn_actions.values())} "
          f"triggerWorkflow={trigger_buttons} write-pages={len(write_pages)}")

def render_button_line(b, R):
    t = b["actionType"]
    txt = f"**{md_escape(b['text'])}**"
    extra = ""
    if b.get("visibility"):
        vf = render_filters(b["visibility"], R)
        if vf:
            extra += f"  _(shown when: {vf})_"
    if b.get("confirm"):
        extra += "  _(confirmation prompt)_"
    if t == "triggerWorkflow":
        wf = md_escape(b.get("workflow")) if b.get("workflowId") else "⚠️ NO WORKFLOW CONNECTION"
        return f"{txt} → run automation **{wf}** on {md_escape(R.t(b.get('onTable')))}{extra}"
    if t == "updateRow":
        sets = "; ".join(f"`{R.f(c)}`={R.c(v)}" for c, v, _ in b.get("sets", []))
        return f"{txt} → set {md_escape(sets)} on {md_escape(R.t(b.get('onTable')))}{extra}"
    if t == "deleteRow":
        return f"{txt} → delete row in {md_escape(R.t(b.get('onTable')))}{extra}"
    if t == "navigateToSelectedPage":
        return f"{txt} → open page **{md_escape(R.p(b.get('targetPage')))}**{extra}"
    if t == "navigateToStaticUrl":
        tgt = R.p(b["targetPage"]) if b.get("targetPage") else b.get("url")
        return f"{txt} → open {'form/page ' if b.get('targetPage') else 'URL '}**{md_escape(tgt)}**{extra}"
    if t == "openFormModalDialog":
        return f"{txt} → open embedded form **{md_escape(R.p(b.get('targetPage')))}** ({md_escape(R.t(b.get('onTable')))}){extra}"
    if t == "addForeignRow":
        return f"{txt} → add linked record in {md_escape(R.t(b.get('onTable')))} via {md_escape(R.p(b.get('targetPage')))}{extra}"
    return f"{txt} → {t}{extra}"

if __name__ == "__main__":
    main()
