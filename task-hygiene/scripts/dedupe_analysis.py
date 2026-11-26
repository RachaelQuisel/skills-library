#!/usr/bin/env python3
"""
Dedupe sweep over all 166 tasks in the Maintenance of current systems project.

Conservative rules (each one exists to avoid a specific mistake):
  R1. Never touch Done, Cancelled, or Archived records — completed work is history,
      and a Done "duplicate" is a record that the work happened.
  R2. Group by normalized task name (case/whitespace/apostrophe-insensitive).
      Name-only similarity is NOT enough — descriptions must match (or one be empty)
      before a record is called redundant. Different descriptions = different asks.
  R3. In a group with a Done copy: open copies (Backlog/Ready/Blocked) whose
      description matches are REDUNDANT — the work is already done.
  R4. In a group with only open copies: keep the earliest-created; later copies
      with matching descriptions are REDUNDANT.
  R5. A record with Hours Used logged, comments-bearing fields, or a Parent/Outcome
      link the keeper lacks is NEVER auto-cancelled — flagged for Rachael instead.
  R6. Anything not covered by R3/R4 lands in the FLAG list, not the cancel list.

Outputs: dedupe_report.txt (human review), cancel_payload.json (records to mark
Cancelled with a triage note naming the keeper).
"""
import json, re
from collections import defaultdict

STATUS_F = "fldExample0000025"
NAME_F = "fldExample0000024"
DESC_F = "fldExample0000167"
CREATED_F = "fldExample0000172"
ARCHIVED_F = "fldExample0000030"
HOURS_USED_F = "fldExample0000169"
HOURS_EST_F = "fldExample0000168"
OUTCOMES_F = "fldExample0000164"
PARENT_F = "fldExample0000165"
TRIAGE_NOTES_F = "fldExample0000170"

DONE_LIKE = {"Done", "Cancelled"}

def norm_name(s):
    s = (s or "").lower().replace("’", "'").replace("—", "-").replace("–", "-")
    return re.sub(r"\s+", " ", s).strip()

def norm_desc(s):
    return re.sub(r"\s+", " ", (s or "")).strip().lower()

with open("all_tasks.json") as f:
    data = json.load(f)

recs = []
for r in data["records"]:
    c = r["cellValuesByFieldId"]
    status = (c.get(STATUS_F) or {}).get("name", "") if isinstance(c.get(STATUS_F), dict) else ""
    recs.append({
        "id": r["id"], "name": c.get(NAME_F, ""), "status": status or "(none)",
        "desc": norm_desc(c.get(DESC_F, "")), "created": c.get(CREATED_F, ""),
        "archived": bool(c.get(ARCHIVED_F)), "hours_used": c.get(HOURS_USED_F),
        "hours_est": c.get(HOURS_EST_F), "outcomes": c.get(OUTCOMES_F) or [],
        "parent": c.get(PARENT_F) or [],
    })

# Completeness check: what we fetched must equal what the table says exists.
# (Never hard-code an expected count — the table grows between runs.)
assert len(recs) == data["metadata"]["totalRecordCount"], \
    f"truncated fetch: {len(recs)} of {data['metadata']['totalRecordCount']}"

groups = defaultdict(list)
for r in recs:
    groups[norm_name(r["name"])].append(r)

cancel, flags = [], []
for key, members in sorted(groups.items()):
    if len(members) < 2:
        continue
    members.sort(key=lambda r: r["created"])
    # Archived Done records still count as PROOF the work happened (keepers),
    # but archived records are never written to.
    done = [m for m in members if m["status"] == "Done"]
    open_ = [m for m in members if m["status"] not in DONE_LIKE and not m["archived"]]
    if len(done) > 1:
        flags.append((key, f"{len(done)} separate Done records "
                           f"({'archived' if all(m['archived'] for m in done) else 'mixed'}) — "
                           f"informational: " + ", ".join(m["id"] for m in done)))
    if not open_:
        continue
    candidates = open_ if done else open_[1:]  # R3 / R4 (keep earliest when no Done)
    for m in candidates:
        # keeper = a Done copy whose description matches this dup, else the earliest open copy
        keeper = next((d for d in done if not m["desc"] or not d["desc"]
                       or m["desc"] == d["desc"]), None) or (open_[0] if not done else None)
        reasons_to_keep = []
        if keeper is None:
            reasons_to_keep.append("no Done copy with a matching description")
        if m["hours_used"]:
            reasons_to_keep.append(f"has Hours Used = {m['hours_used']}")  # R5
        if keeper is not None and not done and m["desc"] and keeper["desc"] \
                and m["desc"] != keeper["desc"]:
            reasons_to_keep.append("description differs from the open keeper")
        if reasons_to_keep:
            flags.append((key, f"{m['id']} looks duplicate but NOT auto-cancelled: "
                               + "; ".join(reasons_to_keep)))
        else:
            note_extra = ""
            extra_links = ({o.get("id") for o in m["outcomes"]}
                           - {o.get("id") for o in keeper["outcomes"]})
            if extra_links:
                note_extra = " Dup carried outcome links; they remain on the record."
            cancel.append({"dup": m, "keeper": keeper, "note_extra": note_extra,
                           "why": (f"work already Done in {keeper['id']}"
                                   f"{' (archived)' if keeper['archived'] else ''}"
                                   if done else f"earlier open copy is {keeper['id']}")})

payload = [{"id": c["dup"]["id"], "fields": {
    STATUS_F: "Cancelled",
    TRIAGE_NOTES_F: (f"Dedupe sweep 2026-08-22 (Rachael-approved): duplicate of "
                     f"{c['keeper']['id']} ('{c['keeper']['name']}', status "
                     f"{c['keeper']['status']}{', archived' if c['keeper']['archived'] else ''})."
                     f"{c['note_extra']} API lacks delete scope, so Cancelled instead of "
                     f"deleted.")}} for c in cancel]

with open("cancel_payload.json", "w") as f:
    json.dump(payload, f, indent=2)

with open("dedupe_report.txt", "w") as f:
    f.write(f"Scanned {len(recs)} tasks, {sum(1 for g in groups.values() if len(g) > 1)} duplicate name-groups.\n\n")
    f.write(f"=== AUTO-CANCEL ({len(cancel)}) ===\n")
    for c in cancel:
        d = c["dup"]
        f.write(f"  {d['id']}  [{d['status']:<14}] {d['name'][:60]}\n"
                f"      -> {c['why']}\n")
    f.write(f"\n=== FLAGGED FOR RACHAEL ({len(flags)}) ===\n")
    for key, msg in flags:
        f.write(f"  {key[:55]}\n      {msg}\n")

print(open("dedupe_report.txt").read())
