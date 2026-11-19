#!/usr/bin/env python3
"""
eval_helper.py — companion utility for the workflow-eval skill.

Subcommands:
  snapshot   Pull Airtable record state into a JSON file.
  diff       Diff two snapshot JSON files; produce a structured diff JSON.
  render     Render an eval result JSON into a Markdown post-run analysis.

Snapshot requires AIRTABLE_PAT env var. Diff and render are pure local.
Stdlib only — no third-party deps.
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


AIRTABLE_API_BASE = "https://api.airtable.com/v0"
VALID_VERDICTS = ("PASS", "FAIL", "UNVERIFIED")


def _utc_now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _airtable_get(url, headers, max_retries=3):
    attempt = 0
    while True:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries:
                retry_after = e.headers.get("Retry-After")
                wait = float(retry_after) if retry_after else (2 ** attempt)
                time.sleep(wait)
                attempt += 1
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                attempt += 1
                continue
            raise


def _list_records(base_id, table_id, pat, since=None):
    headers = {"Authorization": f"Bearer {pat}"}
    records = []
    offset = None
    while True:
        params = {"pageSize": "100"}
        if since:
            params["filterByFormula"] = (
                f"IS_AFTER(LAST_MODIFIED_TIME(), '{since}')"
            )
        if offset:
            params["offset"] = offset
        url = (
            f"{AIRTABLE_API_BASE}/{base_id}/{table_id}?"
            + urllib.parse.urlencode(params)
        )
        data = _airtable_get(url, headers)
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break
        time.sleep(0.25)  # stay under Airtable's 5 req/sec/base rate limit
    return records


def _validate_since(since):
    if since is None:
        return None
    if "'" in since or "\\" in since:
        sys.exit("ERROR: --since must not contain quote or backslash characters")
    try:
        datetime.fromisoformat(since.replace("Z", "+00:00"))
    except ValueError:
        sys.exit(
            f"ERROR: --since must be ISO 8601 (e.g. 2026-06-06T14:00:00Z); got {since!r}"
        )
    return since


def cmd_snapshot(args):
    pat = os.environ.get("AIRTABLE_PAT")
    if not pat:
        sys.exit("ERROR: AIRTABLE_PAT env var not set")
    tables = [t.strip() for t in args.tables.split(",") if t.strip()]
    if not tables:
        sys.exit("ERROR: --tables must list at least one table ID")
    since = _validate_since(args.since)
    snapshot = {
        "captured_at": _utc_now_iso(),
        "base": args.base,
        "since": since,
        "tables": {},
    }
    for table in tables:
        try:
            records = _list_records(args.base, table, pat, since=since)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8") if hasattr(e, "read") else ""
            sys.exit(f"ERROR: Airtable returned {e.code} for {table}: {body[:200]}")
        except (urllib.error.URLError, TimeoutError) as e:
            sys.exit(f"ERROR: Network error pulling {table}: {e}")
        snapshot["tables"][table] = {
            "record_count": len(records),
            "records": records,
        }
        print(f"  {table}: {len(records)} records", file=sys.stderr)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(snapshot, indent=2))
    print(f"Snapshot written to {out_path}", file=sys.stderr)


def _index_records(snapshot_tables):
    return {
        t: {r["id"]: r for r in payload.get("records", [])}
        for t, payload in snapshot_tables.items()
    }


def _diff_record_fields(before_fields, after_fields):
    changes = {}
    all_keys = set(before_fields.keys()) | set(after_fields.keys())
    for k in all_keys:
        b = before_fields.get(k)
        a = after_fields.get(k)
        if b != a:
            changes[k] = {"before": b, "after": a}
    return changes


def cmd_diff(args):
    before = json.loads(Path(args.before).read_text())
    after = json.loads(Path(args.after).read_text())
    before_idx = _index_records(before.get("tables", {}))
    after_idx = _index_records(after.get("tables", {}))
    diff = {
        "before_captured_at": before.get("captured_at"),
        "after_captured_at": after.get("captured_at"),
        "tables": {},
    }
    tables = set(before_idx.keys()) | set(after_idx.keys())
    for table in sorted(tables):
        before_recs = before_idx.get(table, {})
        after_recs = after_idx.get(table, {})
        added_ids = sorted(set(after_recs) - set(before_recs))
        deleted_ids = sorted(set(before_recs) - set(after_recs))
        updated = []
        for rid in sorted(set(before_recs) & set(after_recs)):
            field_changes = _diff_record_fields(
                before_recs[rid].get("fields", {}),
                after_recs[rid].get("fields", {}),
            )
            if field_changes:
                updated.append({"id": rid, "changes": field_changes})
        diff["tables"][table] = {
            "added": [after_recs[rid] for rid in added_ids],
            "deleted": [before_recs[rid] for rid in deleted_ids],
            "updated": updated,
            "summary": {
                "added": len(added_ids),
                "deleted": len(deleted_ids),
                "updated": len(updated),
            },
        }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(diff, indent=2))
    print(f"Diff written to {out_path}", file=sys.stderr)
    for table, payload in diff["tables"].items():
        s = payload["summary"]
        print(
            f"  {table}: +{s['added']} ~{s['updated']} -{s['deleted']}",
            file=sys.stderr,
        )


def _verdict_summary(result):
    counts = {"PASS": 0, "FAIL": 0, "UNVERIFIED": 0}
    for c in result.get("cases", []):
        v = c.get("verdict", "UNVERIFIED")
        counts[v] = counts.get(v, 0) + 1
    parts = [f"{n} {k}" for k, n in counts.items() if n]
    return " / ".join(parts) if parts else "no cases"


def _render_diff_block(diff):
    if not diff:
        return "(no diff captured)"
    lines = []
    for table, payload in diff.get("tables", {}).items():
        s = payload["summary"]
        if not (s["added"] or s["updated"] or s["deleted"]):
            continue
        lines.append(
            f"**{table}** — added {s['added']}, updated {s['updated']}, deleted {s['deleted']}"
        )
        for rec in payload["added"][:5]:
            fields_preview = json.dumps(rec.get("fields", {}))[:120]
            lines.append(f"  - ADDED `{rec['id']}` — {fields_preview}")
        if len(payload["added"]) > 5:
            lines.append(f"  - ... and {len(payload['added']) - 5} more added")
        for upd in payload["updated"][:5]:
            change_keys = ", ".join(sorted(upd["changes"].keys()))
            lines.append(f"  - UPDATED `{upd['id']}` — fields: {change_keys}")
        if len(payload["updated"]) > 5:
            lines.append(f"  - ... and {len(payload['updated']) - 5} more updated")
        for rec in payload["deleted"][:5]:
            lines.append(f"  - DELETED `{rec['id']}`")
        if len(payload["deleted"]) > 5:
            lines.append(f"  - ... and {len(payload['deleted']) - 5} more deleted")
    return "\n".join(lines) if lines else "(no observed changes)"


def _validate_result(result):
    errs = []
    for i, case in enumerate(result.get("cases", [])):
        name = case.get("name", f"(case #{i})")
        verdict = case.get("verdict")
        if verdict not in VALID_VERDICTS:
            errs.append(
                f"case {name!r} has invalid verdict {verdict!r}; must be one of {list(VALID_VERDICTS)}"
            )
            continue
        if verdict == "FAIL" and not case.get("failure_reasons"):
            errs.append(f"case {name!r} is FAIL but has no failure_reasons")
        if verdict == "UNVERIFIED" and not case.get("unverified_reasons"):
            errs.append(
                f"case {name!r} is UNVERIFIED but has no unverified_reasons"
            )
    if errs:
        msg = "ERROR: result.json validation failed:\n  - " + "\n  - ".join(errs)
        sys.exit(msg)


def cmd_render(args):
    result = json.loads(Path(args.result).read_text())
    _validate_result(result)
    workflow = result.get("workflow", "(unknown workflow)")
    run_date = result.get(
        "run_date", datetime.now(timezone.utc).strftime("%Y-%m-%d")
    )
    summary = _verdict_summary(result)
    lines = [
        f"# Post-Run Analysis — {workflow}",
        "",
        f"**Run date:** {run_date}",
        f"**Summary:** {summary}",
        "",
    ]
    if result.get("inventory_notes"):
        lines.extend(["## Inventory notes", "", result["inventory_notes"], ""])
    lines.extend(["## Cases", ""])
    for case in result.get("cases", []):
        verdict = case.get("verdict", "UNVERIFIED")
        lines.append(f"### {case.get('name', '(unnamed)')} — {verdict}")
        lines.append("")
        if case.get("description"):
            lines.append(case["description"])
            lines.append("")
        if case.get("expected_outcomes"):
            lines.append("**Expected:**")
            for eo in case["expected_outcomes"]:
                lines.append(f"- {eo}")
            lines.append("")
        if case.get("actual_outcomes"):
            lines.append("**Actual:**")
            for ao in case["actual_outcomes"]:
                lines.append(f"- {ao}")
            lines.append("")
        if case.get("diff"):
            lines.append("**Observed state changes:**")
            lines.append("")
            lines.append(_render_diff_block(case["diff"]))
            lines.append("")
        if verdict == "FAIL" and case.get("failure_reasons"):
            lines.append("**Why FAIL:**")
            for r in case["failure_reasons"]:
                lines.append(f"- {r}")
            lines.append("")
        if verdict == "UNVERIFIED" and case.get("unverified_reasons"):
            lines.append("**Why UNVERIFIED:**")
            for r in case["unverified_reasons"]:
                lines.append(f"- {r}")
            lines.append("")
        if case.get("notes"):
            lines.append(f"**Notes:** {case['notes']}")
            lines.append("")
    if result.get("unexpected_writes"):
        lines.append("## Unexpected writes (not predicted by any case)")
        lines.append("")
        for uw in result["unexpected_writes"]:
            lines.append(f"- {uw}")
        lines.append("")
    if result.get("followups"):
        lines.append("## Follow-ups")
        lines.append("")
        for f in result["followups"]:
            lines.append(f"- {f}")
        lines.append("")
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))
    print(f"Report written to {out_path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_snap = sub.add_parser("snapshot", help="Pull Airtable record state into JSON")
    p_snap.add_argument("--base", required=True, help="Airtable base ID (appXXX)")
    p_snap.add_argument(
        "--tables",
        required=True,
        help="Comma-separated table IDs (tblXXX,tblYYY) or table names",
    )
    p_snap.add_argument(
        "--since",
        help="Optional ISO 8601 timestamp; if set, only records modified after this time are pulled",
    )
    p_snap.add_argument("--out", required=True, help="Output JSON path")
    p_snap.set_defaults(func=cmd_snapshot)

    p_diff = sub.add_parser("diff", help="Diff two snapshot JSON files")
    p_diff.add_argument("--before", required=True, help="Before snapshot JSON path")
    p_diff.add_argument("--after", required=True, help="After snapshot JSON path")
    p_diff.add_argument("--out", required=True, help="Output diff JSON path")
    p_diff.set_defaults(func=cmd_diff)

    p_render = sub.add_parser(
        "render",
        help="Render eval result JSON to Markdown post-run analysis",
    )
    p_render.add_argument("--result", required=True, help="Result JSON path")
    p_render.add_argument("--out", required=True, help="Output Markdown path")
    p_render.set_defaults(func=cmd_render)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
