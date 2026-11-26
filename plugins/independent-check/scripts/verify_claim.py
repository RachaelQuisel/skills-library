#!/usr/bin/env python3
"""Verification-before-completion gate.

A claim is "the tests pass", "the migration is done", "the deploy worked".
Words like `should`, `probably`, and `seems to` stop the claim. A previous
run, a partial check, or another agent's success report is never sufficient
evidence. The claim is approved only when:

- An evidence file is provided with the proof command's exit code, output,
  and a recent timestamp (default: within 5 minutes).
- The claim text contains no hedge words.
- The observed exit code matches the expected exit code for the claim.

This script does not run the proof command itself. The agent runs it fresh,
redirects stdout and stderr and the exit code into a JSON evidence file, and
then this script reads that evidence and approves or refuses the claim.

Adapted from https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
from typing import Any

HEDGE_PATTERNS = [
    re.compile(r"\bshould\b", re.IGNORECASE),
    re.compile(r"\bprobably\b", re.IGNORECASE),
    re.compile(r"\bseems to\b", re.IGNORECASE),
    re.compile(r"\bappears to\b", re.IGNORECASE),
    re.compile(r"\blikely\b", re.IGNORECASE),
    re.compile(r"\bmight (?:be|have)\b", re.IGNORECASE),
    re.compile(r"\bI think\b", re.IGNORECASE),
]

EXIT_APPROVED = 0
EXIT_REFUSED = 1
EXIT_CONFIG = 3


def parse_timestamp(raw: str) -> dt.datetime:
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    return dt.datetime.fromisoformat(raw)


def find_hedges(text: str) -> list[str]:
    found: list[str] = []
    for pat in HEDGE_PATTERNS:
        m = pat.search(text)
        if m:
            found.append(m.group(0))
    return found


def verify(evidence: dict, claim: str, expected_exit: int, max_age_seconds: int) -> tuple[int, list[str], list[str]]:
    failures: list[str] = []
    notes: list[str] = []

    hedges = find_hedges(claim)
    if hedges:
        failures.append(f"claim contains hedge words: {hedges}")

    exit_code = evidence.get("exit_code")
    if exit_code is None:
        failures.append("evidence is missing 'exit_code'")
    elif exit_code != expected_exit:
        failures.append(f"evidence exit_code={exit_code}, expected {expected_exit}")
    else:
        notes.append(f"exit_code matches expected ({expected_exit})")

    ts_raw = evidence.get("timestamp")
    if not ts_raw:
        failures.append("evidence is missing 'timestamp'")
    else:
        try:
            ts = parse_timestamp(ts_raw)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=dt.timezone.utc)
            age = (dt.datetime.now(dt.timezone.utc) - ts).total_seconds()
            if age > max_age_seconds:
                failures.append(f"evidence is {int(age)}s old (max {max_age_seconds}s); re-run fresh")
            elif age < 0:
                failures.append(f"evidence timestamp is in the future ({ts_raw})")
            else:
                notes.append(f"evidence is {int(age)}s old (within {max_age_seconds}s)")
        except Exception as exc:
            failures.append(f"evidence timestamp unreadable: {exc}")

    if not evidence.get("proof_command"):
        failures.append("evidence is missing 'proof_command'")

    if "stdout" not in evidence and "stderr" not in evidence:
        failures.append("evidence has no stdout or stderr capture; the proof command was not actually run")

    if failures:
        return EXIT_REFUSED, failures, notes
    return EXIT_APPROVED, failures, notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gate a completion claim behind fresh verification evidence.")
    parser.add_argument("--claim", required=True, help="The completion claim (plain text).")
    parser.add_argument("--evidence", required=True, help="Path to JSON evidence file.")
    parser.add_argument("--expected-exit", type=int, default=0, help="Exit code the proof command must have returned.")
    parser.add_argument("--max-age-seconds", type=int, default=300, help="Reject evidence older than this.")
    args = parser.parse_args(argv)

    evidence_path = pathlib.Path(args.evidence).resolve()
    if not evidence_path.exists():
        print(f"REFUSED: evidence file not found: {evidence_path}", file=sys.stderr)
        print("Run the proof command fresh and capture exit_code + stdout + timestamp first.")
        return EXIT_REFUSED

    try:
        with evidence_path.open("r", encoding="utf-8") as fh:
            evidence = json.load(fh)
    except Exception as exc:
        print(f"REFUSED: could not read evidence JSON: {exc}", file=sys.stderr)
        return EXIT_CONFIG

    exit_code, failures, notes = verify(evidence, args.claim, args.expected_exit, args.max_age_seconds)

    if exit_code == EXIT_APPROVED:
        print(f"APPROVED: '{args.claim}'")
        for n in notes:
            print(f"  - {n}")
    else:
        print(f"REFUSED: '{args.claim}'")
        for f in failures:
            print(f"  - {f}")
        for n in notes:
            print(f"  (note) {n}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
