#!/usr/bin/env python3
"""
update_mcs_fields.py — Create new MCS table fields and patch SKILL.md mapping table.

Adds four fields to the MCS table (base appExample0000047, table tblExample0000061):
  - Engineer                      (collaborator / single user)
  - Build Time                    (single select: 2-4, 5-10, 11-20, 21+ hours)
  - Industry (single-select)      (single select, 18 options)
  - Result 2 (independent)        (single-line text)

Does NOT touch existing fields (Industry fldExample0000050, Result 2 fldExample0000051).
Restores SKILL.md from SKILL.md.bak, then patches ONLY the mapping table region.
Deletes update_skill.py (obsolete from prior run).

Idempotent. Supports --dry-run.

Usage:
    export AIRTABLE_PAT=patXXXXXX.XXXX   # needs schema.bases:write + data scopes
    python update_mcs_fields.py --dry-run
    python update_mcs_fields.py
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

BASE_ID = "appExample0000047"
TABLE_ID = "tblExample0000061"
META_URL = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"

SKILL_DIR = Path(__file__).parent
SKILL_PATH = SKILL_DIR / "SKILL.md"
BACKUP_PATH = SKILL_DIR / "SKILL.md.bak"
OBSOLETE_SCRIPT = SKILL_DIR / "update_skill.py"

INDUSTRY_OPTIONS = [
    "Finance", "Insurance", "Manufacturing", "Technology", "Healthcare",
    "Life Sciences", "Professional Services", "Agencies", "Media",
    "Retail & E-commerce", "Logistics & Supply Chain", "Hospitality",
    "Real Estate", "Construction", "Energy & Utilities", "Nonprofits",
    "Education", "Government",
]
BUILD_TIME_OPTIONS = ["2-4 hours", "5-10 hours", "11-20 hours", "21+ hours"]

NEW_FIELDS = [
    {
        "display": "Engineer",
        "name": "Engineer",
        "spec": {
            "name": "Engineer",
            "type": "singleCollaborator",
            "description": "Who built or will build this MCS. Defaults to the submitter.",
        },
    },
    {
        "display": "Build Time",
        "name": "Build Time",
        "spec": {
            "name": "Build Time",
            "type": "singleSelect",
            "description": "Approximate build effort bucket.",
            "options": {"choices": [{"name": n} for n in BUILD_TIME_OPTIONS]},
        },
    },
    {
        "display": "Industry (new)",
        "name": "Industry (single-select)",
        "spec": {
            "name": "Industry (single-select)",
            "type": "singleSelect",
            "description": (
                "Primary industry. New canonical single-select. "
                "Replaces free-text Industry field for new records. "
                "Existing Industry (fldExample0000050) kept intact for legacy data."
            ),
            "options": {"choices": [{"name": n} for n in INDUSTRY_OPTIONS]},
        },
    },
    {
        "display": "Result 2 (new)",
        "name": "Result 2 (independent)",
        "spec": {
            "name": "Result 2 (independent)",
            "type": "singleLineText",
            "description": (
                "Second quantifiable outcome, entered independently. "
                "Replaces auto-mirrored Result 2 (fldExample0000051) for new records."
            ),
        },
    },
]


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _request(method: str, url: str, pat: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {pat}")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} {method} {url}\n{detail}") from None


def describe_table(pat: str) -> dict:
    payload = _request("GET", META_URL, pat)
    for t in payload.get("tables", []):
        if t.get("id") == TABLE_ID:
            return t
    raise RuntimeError(f"Table {TABLE_ID} not found in base {BASE_ID}")


def create_field(pat: str, spec: dict) -> dict:
    url = f"{META_URL}/{TABLE_ID}/fields"
    return _request("POST", url, pat, spec)


# ---------------------------------------------------------------------------
# SKILL.md patching
# ---------------------------------------------------------------------------

# Target rows in the mapping table (order preserved where already present).
MAPPING_ROW_PATTERNS = {
    "Engineer": re.compile(r"^\| Engineer \|.*\|.*\|\s*$", re.MULTILINE),
    "Build Time": re.compile(r"^\| Build Time \|.*\|.*\|\s*$", re.MULTILINE),
    "Industry": re.compile(r"^\| Industry \|.*\|.*\|\s*$", re.MULTILINE),
    "Result 2": re.compile(
        r"^\| Value \| \*\*Result 1\*\* \|.*\|\s*$|^\| Result 2 \|.*\|.*\|\s*$",
        re.MULTILINE,
    ),
}


def _build_mapping_rows(created_ids: dict[str, str]) -> dict[str, str]:
    """Produce replacement/insert rows for the mapping table, using new field IDs."""
    def fid(key: str) -> str:
        return f"`{created_ids[key]}`" if created_ids.get(key) else "(pending create)"

    return {
        "Engineer": f"| Engineer | Engineer | {fid('Engineer')} |",
        "Build Time": f"| Build Time | Build Time | {fid('Build Time')} |",
        "Industry": (
            f"| Industry | Industry (single-select) | {fid('Industry (single-select)')} "
            f"(new; legacy free-text `fldExample0000050` kept intact) |"
        ),
        "Result 2": (
            f"| Result 2 | Result 2 (independent) | {fid('Result 2 (independent)')} "
            f"(new; legacy auto-mirror `fldExample0000051` kept intact) |"
        ),
    }


def _patch_mapping_table(content: str, new_rows: dict[str, str]) -> str:
    """Replace or insert the four rows in the 'Where to Store MCS Records' mapping table only."""
    # Narrow to the mapping-table region to avoid edits elsewhere.
    start_marker = "## Where to Store MCS Records"
    end_marker = "## Visual Assets"
    start = content.find(start_marker)
    end = content.find(end_marker, start + 1) if start != -1 else -1
    if start == -1 or end == -1:
        raise RuntimeError("Could not locate mapping table region in SKILL.md")

    head = content[:start]
    region = content[start:end]
    tail = content[end:]

    # Engineer row — backup has no Engineer row; insert after Result 2 Icon line.
    # Idempotent: skip insert if already present.
    if re.search(r"^\| Engineer \| Engineer \|", region, flags=re.MULTILINE) is None:
        region = re.sub(
            r"(^\| Result 2 Icon \| Result 2 Icon \| `fldExample0000059` \|\s*$)",
            r"\1\n" + new_rows["Engineer"],
            region,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        region = re.sub(
            r"^\| Engineer \| Engineer \|[^\n]*\|\s*$",
            new_rows["Engineer"],
            region,
            count=1,
            flags=re.MULTILINE,
        )
    # Build Time row — backup has no Build Time row; insert after Engineer row.
    if re.search(r"^\| Build Time \| Build Time \|", region, flags=re.MULTILINE) is None:
        region = re.sub(
            r"(^\| Engineer \| Engineer \|[^\n]*\|\s*$)",
            r"\1\n" + new_rows["Build Time"],
            region,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        region = re.sub(
            r"^\| Build Time \| Build Time \|[^\n]*\|\s*$",
            new_rows["Build Time"],
            region,
            count=1,
            flags=re.MULTILINE,
        )
    # Industry row — replace the existing Industry line that points at fldExample0000050.
    region = re.sub(
        r"^\| Industry \| Industry \| `fldExample0000050` \|\s*$",
        new_rows["Industry"],
        region,
        count=1,
        flags=re.MULTILINE,
    )
    # Result 2 row — the current mapping lists Value→Result 1 but no explicit Result 2
    # row in the mapping table. Insert the Result 2 row directly after the Value row
    # (idempotent: skip insert if row already present).
    if "| Result 2 | Result 2 (independent) |" not in region:
        region = re.sub(
            r"(^\| Value \| \*\*Result 1\*\* \| `fldExample0000056` \|\s*$)",
            r"\1\n" + new_rows["Result 2"],
            region,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        # Already present — make sure it points at the right field ID (replace in place).
        region = re.sub(
            r"^\| Result 2 \| Result 2 \(independent\) \|[^\n]*\|\s*$",
            new_rows["Result 2"],
            region,
            count=1,
            flags=re.MULTILINE,
        )

    return head + region + tail


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Describe actions, no writes.")
    parser.add_argument(
        "--skip-api", action="store_true",
        help="Skip Airtable API calls (SKILL.md patch + file cleanup only). "
             "Uses placeholder field IDs. Useful when AIRTABLE_PAT is unavailable.",
    )
    args = parser.parse_args()

    pat = os.environ.get("AIRTABLE_PAT", "")
    if not args.skip_api and not pat:
        print("ERROR: AIRTABLE_PAT not set. Use --skip-api to skip Airtable calls.",
              file=sys.stderr)
        return 2

    report: list[str] = []
    created_ids: dict[str, str] = {}

    # ---------- Step 1: restore SKILL.md from SKILL.md.bak ----------
    if not BACKUP_PATH.exists():
        print(f"ERROR: backup {BACKUP_PATH} missing — cannot restore", file=sys.stderr)
        return 3
    original_skill = SKILL_PATH.read_text() if SKILL_PATH.exists() else ""
    backup_skill = BACKUP_PATH.read_text()

    if args.dry_run:
        report.append(f"[dry-run] would restore {SKILL_PATH.name} from {BACKUP_PATH.name}")
    else:
        SKILL_PATH.write_text(backup_skill)
        # Re-seed the backup so subsequent runs still have a restore target.
        # (file content unchanged; no-op, but keep explicit for clarity)
        report.append(f"restored {SKILL_PATH.name} from {BACKUP_PATH.name}")

    # ---------- Step 2: describe the MCS table ----------
    existing_field_names: set[str] = set()
    if args.skip_api:
        report.append("[skip-api] skipping describe_table")
    else:
        table = describe_table(pat)
        existing_field_names = {f["name"] for f in table.get("fields", [])}
        report.append(
            f"describe_table ok — {len(existing_field_names)} fields in {table.get('name')}"
        )
        # Also grab existing IDs for our new field names in case they were pre-created.
        for f in table.get("fields", []):
            if f["name"] in {nf["name"] for nf in NEW_FIELDS}:
                created_ids[f["name"]] = f["id"]

    # ---------- Steps 3-6: create fields (idempotent) ----------
    for spec_entry in NEW_FIELDS:
        target_name = spec_entry["name"]
        display = spec_entry["display"]
        if target_name in existing_field_names:
            report.append(f"  [no-op] field already exists: {target_name} "
                          f"(id={created_ids.get(target_name, '?')})")
            continue
        if args.dry_run or args.skip_api:
            report.append(f"  [{'dry-run' if args.dry_run else 'skip-api'}] "
                          f"would create {display}: {target_name} "
                          f"type={spec_entry['spec']['type']}")
            # Placeholder id for SKILL.md patch preview
            created_ids.setdefault(target_name, f"fldPENDING_{target_name.replace(' ', '_')}")
            continue
        result = create_field(pat, spec_entry["spec"])
        created_ids[target_name] = result["id"]
        report.append(f"  created {display}: {target_name} id={result['id']}")

    # ---------- Step 7: patch SKILL.md mapping table ----------
    id_map = {
        "Engineer": created_ids.get("Engineer", "fldPENDING_Engineer"),
        "Build Time": created_ids.get("Build Time", "fldPENDING_Build_Time"),
        "Industry (single-select)": created_ids.get(
            "Industry (single-select)", "fldPENDING_Industry"
        ),
        "Result 2 (independent)": created_ids.get(
            "Result 2 (independent)", "fldPENDING_Result_2"
        ),
    }
    new_rows = _build_mapping_rows(id_map)
    patched = _patch_mapping_table(backup_skill, new_rows)

    if args.dry_run:
        report.append("[dry-run] SKILL.md mapping-table patch preview only")
    else:
        SKILL_PATH.write_text(patched)
        report.append(f"patched {SKILL_PATH.name} mapping table")

    # ---------- Step 8: delete obsolete update_skill.py ----------
    if OBSOLETE_SCRIPT.exists():
        if args.dry_run:
            report.append(f"[dry-run] would delete {OBSOLETE_SCRIPT.name}")
        else:
            OBSOLETE_SCRIPT.unlink()
            report.append(f"deleted {OBSOLETE_SCRIPT.name}")
    else:
        report.append(f"  [no-op] {OBSOLETE_SCRIPT.name} already absent")

    # ---------- Step 9: print unified diff of SKILL.md changes ----------
    diff = list(difflib.unified_diff(
        backup_skill.splitlines(keepends=True),
        patched.splitlines(keepends=True),
        fromfile="SKILL.md.bak",
        tofile="SKILL.md (patched)",
    ))

    print("=" * 72)
    print("Report")
    print("=" * 72)
    for line in report:
        print(line)
    print()
    print("=" * 72)
    print("SKILL.md diff (from SKILL.md.bak)")
    print("=" * 72)
    if diff:
        sys.stdout.writelines(diff)
    else:
        print("(no SKILL.md changes)")
    print()

    # ---------- Step 10: verification checklist ----------
    print("=" * 72)
    print("Verification checklist")
    print("=" * 72)
    print("[ ] 1. describe_table on MCS — confirm 4 new fields with expected types/options")
    print("[ ] 2. diff SKILL.md SKILL.md.bak — only mapping table region changed")
    print("[ ] 3. Re-run script — every step reports no-op (idempotency)")
    print("[ ] 4. Grep SKILL.md for fldExample0000048 (Zoom Transcript 1) "
          "and appExample0000049 (CRM Enriched Debriefs) — still present")
    print("[ ] 5. Existing Industry (fldExample0000050) and "
          "Result 2 (fldExample0000051) unchanged")

    return 0


if __name__ == "__main__":
    sys.exit(main())
