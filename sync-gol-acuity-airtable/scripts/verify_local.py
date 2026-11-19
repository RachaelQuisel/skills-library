#!/usr/bin/env python3
"""Run canonical GoL unit tests offline and report sanitized verification."""

import argparse
from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import unittest


DEFAULT_AUTOMATION = Path(
    "/Users/rachaelquisel/RachaelQuisel/Codex Work/Client/GOL/Documents/"
    "Repositories/GUARDIANS-OF-LOVE/projects/2026-08-acuity-cloud-sync/automation"
)
REQUIRED = (
    "acuity_new_base_sync.py",
    "applicant_training_requirement_ledger.py",
    "acuity_historical_backfill.py",
    "test_acuity_new_base_sync.py",
    "test_applicant_training_requirement_ledger.py",
    "test_acuity_historical_backfill.py",
    "test_cloud_workflow.py",
)


def inspected_files(root):
    files = set(root.glob("*.py")) | set(root.glob("*.md"))
    for file in (root / "package.json", root / "package-lock.json",
                 root.parents[2] / ".github/workflows/gol-acuity-sync.yml"):
        if file.is_file():
            files.add(file)
    return sorted(files)


def hashes(files, root):
    return {
        os.path.relpath(file, root): hashlib.sha256(file.read_bytes()).hexdigest()
        for file in files
    }


def run(root):
    root = root.resolve(strict=True)
    missing = [name for name in REQUIRED if not (root / name).is_file()]
    if missing:
        return {"success": False, "missing_files": missing}, 2
    before = hashes(inspected_files(root), root)
    blocked = Counter()
    private_config = (Path.home() / ".config/xray").resolve()

    def guard(event, args):
        category = None
        if event.startswith("socket."):
            category = "network"
        elif event in {"subprocess.Popen", "os.system", "os.posix_spawn",
                       "os.posix_spawnp", "os.exec", "os.fork", "os.forkpty"}:
            category = "process"
        elif event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
            candidate = Path(os.fsdecode(args[0])).expanduser().resolve()
            if candidate == private_config or private_config in candidate.parents:
                category = "credential_file"
        if category:
            blocked[category] += 1
            raise RuntimeError("Offline verification blocked " + category + " access")

    for name in ("ACUITY_USER_ID", "ACUITY_API_KEY", "AIRTABLE_PAT", "AIRTABLE_TOKEN"):
        os.environ.pop(name, None)
    sys.dont_write_bytecode = True
    sys.addaudithook(guard)
    sys.path.insert(0, str(root))
    os.chdir(root)
    captured = io.StringIO()
    result = None
    harness_error = None
    try:
        with redirect_stdout(captured), redirect_stderr(captured):
            suite = unittest.defaultTestLoader.discover(str(root), pattern="test_*.py")
            result = unittest.TextTestRunner(stream=captured, verbosity=0).run(suite)
    except Exception as exc:
        harness_error = type(exc).__name__
    # Never emit captured output: test diagnostics can contain real fixture PII.
    after = hashes(inspected_files(root), root)
    changed = sorted(name for name in before.keys() | after.keys()
                     if before.get(name) != after.get(name))
    failures = [] if result is None else [test.id() for test, _ in result.failures]
    errors = [] if result is None else [test.id() for test, _ in result.errors]
    successful = bool(result is not None and result.wasSuccessful()
                      and result.testsRun > 0 and not blocked and not changed
                      and not result.skipped and not result.expectedFailures)
    summary = {
        "automation_dir": str(root),
        "success": successful,
        "tests_run": 0 if result is None else result.testsRun,
        "failures": failures,
        "errors": errors,
        "skipped": [] if result is None else [test.id() for test, _ in result.skipped],
        "expected_failures": [] if result is None else [test.id() for test, _ in result.expectedFailures],
        "blocked_accesses": dict(blocked),
        "changed_inspected_files": changed,
        "source_sha256": before,
    }
    if harness_error:
        summary["harness_error_type"] = harness_error
    return summary, 0 if successful else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--automation-dir", type=Path, default=DEFAULT_AUTOMATION)
    args = parser.parse_args()
    try:
        summary, status = run(args.automation_dir)
    except (OSError, ValueError) as exc:
        summary, status = {"success": False, "harness_error_type": type(exc).__name__}, 2
    print(json.dumps(summary, indent=2, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
