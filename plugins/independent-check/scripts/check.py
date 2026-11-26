#!/usr/bin/env python3
"""Independent Check: the gate executable.

Reads a check config (JSON), loads the product and the external standard, runs
each assertion, and exits non-zero on failure. A failing `gate: true`
assertion (the "never sentence" gate) exits 2 so a caller can tell it apart
from a plain quality miss (exit 1).

Design rules (from the workshop):
- The checker reads the product itself (text/JSON/CSV/Markdown), not a
  maker's summary of it.
- Every number and date in the product must trace to a value in the
  standard, or it is called out.
- Exit code is the machine-readable result. Stdout carries a short report.
- On failure, a blocker alert is written to ./alerts/ unless --no-alert.

No external dependencies. Python 3.9+.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys
from typing import Any

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_GATE = 2
EXIT_CONFIG = 3


# ---------- loaders ----------

def load_config(path: pathlib.Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_standard(spec: dict, base: pathlib.Path) -> Any:
    kind = spec.get("type", "json")
    path = (base / spec["path"]).resolve()
    text = path.read_text(encoding="utf-8")
    if kind == "json":
        return json.loads(text)
    if kind == "text":
        return text
    raise ValueError(f"unsupported standard type: {kind}")


def load_product(spec: dict, base: pathlib.Path) -> str:
    kind = spec.get("type", "text")
    path = (base / spec["path"]).resolve()
    text = path.read_text(encoding="utf-8")
    if kind in ("text", "markdown", "md"):
        return text
    if kind == "json":
        return text
    raise ValueError(f"unsupported product type: {kind}")


# ---------- value extraction ----------

CURRENCY_RE = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]+)?)")
PERCENT_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)\s?%")
ISO_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
LONG_DATE_RE = re.compile(
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b"
)
SHORT_MONTH_RE = re.compile(
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+(\d{1,2}),?\s+(\d{4})\b"
)

LONG_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7,
    "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _normalize_currency(raw: str) -> str:
    return raw.replace(",", "").rstrip(".")


def extract_currency(text: str) -> list[str]:
    return sorted({_normalize_currency(m.group(1)) for m in CURRENCY_RE.finditer(text)})


def extract_percent(text: str) -> list[str]:
    return sorted({m.group(1) for m in PERCENT_RE.finditer(text)})


def extract_dates(text: str) -> list[str]:
    """Return a de-duped list of ISO dates found in the product.

    Catches `YYYY-MM-DD`, `Month D, YYYY`, and `Mon D, YYYY`. All are reported
    in ISO form so the standard can match by canonical value.
    """
    seen: set[str] = set()
    for m in ISO_DATE_RE.finditer(text):
        seen.add(m.group(1))
    for m in LONG_DATE_RE.finditer(text):
        month = LONG_MONTHS[m.group(1).lower()]
        day = int(m.group(2))
        year = int(m.group(3))
        seen.add(f"{year:04d}-{month:02d}-{day:02d}")
    for m in SHORT_MONTH_RE.finditer(text):
        month = LONG_MONTHS[m.group(1).lower()]
        day = int(m.group(2))
        year = int(m.group(3))
        seen.add(f"{year:04d}-{month:02d}-{day:02d}")
    return sorted(seen)


def _flatten_standard_values(standard: Any) -> list[str]:
    out: list[str] = []
    if isinstance(standard, dict):
        for v in standard.values():
            out.extend(_flatten_standard_values(v))
    elif isinstance(standard, list):
        for v in standard:
            out.extend(_flatten_standard_values(v))
    elif standard is None:
        return []
    else:
        out.append(str(standard))
    return out


def standard_currency_values(standard: Any) -> set[str]:
    out: set[str] = set()
    for raw in _flatten_standard_values(standard):
        for m in CURRENCY_RE.finditer(raw):
            out.add(_normalize_currency(m.group(1)))
        # bare numeric fields, e.g. amount: 4800
        bare = raw.strip()
        if re.fullmatch(r"[0-9][0-9,]*(?:\.[0-9]+)?", bare):
            out.add(_normalize_currency(bare))
    return out


def standard_date_values(standard: Any) -> set[str]:
    out: set[str] = set()
    for raw in _flatten_standard_values(standard):
        for m in ISO_DATE_RE.finditer(raw):
            out.add(m.group(1))
    return out


# ---------- assertions ----------

def assert_all_currency_in_standard(product: str, standard: Any) -> tuple[bool, str]:
    product_values = extract_currency(product)
    standard_values = standard_currency_values(standard)
    missing = [v for v in product_values if v not in standard_values]
    if missing:
        return False, f"currency values in product with no receipt in standard: {missing}"
    if not product_values:
        return True, "no currency values in product"
    return True, f"all {len(product_values)} currency value(s) traced to standard"


def assert_all_dates_in_standard(product: str, standard: Any) -> tuple[bool, str]:
    product_values = extract_dates(product)
    standard_values = standard_date_values(standard)
    missing = [v for v in product_values if v not in standard_values]
    if missing:
        return False, f"dates in product with no receipt in standard: {missing}"
    if not product_values:
        return True, "no dates in product"
    return True, f"all {len(product_values)} date(s) traced to standard"


def assert_mentions_only_named_job(product: str, standard: Any, config: dict) -> tuple[bool, str]:
    job_field = config.get("standard_field", "job_name")
    forbid = config.get("forbid_other_jobs", []) or []
    job_name = None
    if isinstance(standard, dict):
        job_name = standard.get(job_field)
    found_forbidden = [j for j in forbid if j.lower() in product.lower()]
    if found_forbidden:
        return False, f"product mentions other customer jobs: {found_forbidden}"
    if job_name and job_name.lower() not in product.lower():
        return False, f"product does not name the customer job '{job_name}'"
    return True, f"product names the job '{job_name}' and no forbidden others"


def assert_required_phrases(product: str, phrases: list[str]) -> tuple[bool, str]:
    missing = [p for p in phrases if p.lower() not in product.lower()]
    if missing:
        return False, f"missing required phrases: {missing}"
    return True, f"all {len(phrases)} required phrase(s) present"


def assert_forbidden_phrases(product: str, phrases: list[str]) -> tuple[bool, str]:
    present = [p for p in phrases if p.lower() in product.lower()]
    if present:
        return False, f"forbidden phrases present: {present}"
    return True, f"no forbidden phrases present"


ASSERTIONS = {
    "all-currency-in-standard": lambda p, s, c: assert_all_currency_in_standard(p, s),
    "all-dates-in-standard": lambda p, s, c: assert_all_dates_in_standard(p, s),
    "mentions-only-named-job": assert_mentions_only_named_job,
    "required-phrases": lambda p, s, c: assert_required_phrases(p, c.get("phrases", [])),
    "forbidden-phrases": lambda p, s, c: assert_forbidden_phrases(p, c.get("phrases", [])),
}


# ---------- runner ----------

def run_check(config_path: pathlib.Path) -> tuple[int, dict]:
    config = load_config(config_path)
    base = config_path.parent
    standard = load_standard(config["standard"], base)
    product = load_product(config["product"], base)

    results: list[dict] = []
    overall_pass = True
    gate_tripped = False

    for assertion in config.get("assertions", []):
        kind = assertion.get("kind")
        assertion_id = assertion.get("id", kind)
        is_gate = bool(assertion.get("gate", False))
        if kind not in ASSERTIONS:
            results.append({
                "id": assertion_id,
                "kind": kind,
                "gate": is_gate,
                "pass": False,
                "detail": f"unknown assertion kind: {kind}",
            })
            overall_pass = False
            if is_gate:
                gate_tripped = True
            continue
        ok, detail = ASSERTIONS[kind](product, standard, assertion)
        results.append({
            "id": assertion_id,
            "kind": kind,
            "gate": is_gate,
            "pass": ok,
            "detail": detail,
        })
        if not ok:
            overall_pass = False
            if is_gate:
                gate_tripped = True

    report = {
        "job": config.get("job", "unnamed job"),
        "acceptance": config.get("acceptance"),
        "never": config.get("never"),
        "config": str(config_path),
        "ran_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "results": results,
        "pass": overall_pass,
        "gate_tripped": gate_tripped,
    }

    if gate_tripped:
        return EXIT_GATE, report
    if not overall_pass:
        return EXIT_FAIL, report
    return EXIT_PASS, report


def write_alert(report: dict, alert_dir: pathlib.Path) -> pathlib.Path:
    alert_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    path = alert_dir / f"{stamp}-blocker.md"
    lines = [
        f"# Independent check tripped: {report['job']}",
        "",
        f"- Checked at (UTC): {report['ran_at']}",
        f"- Config: {report['config']}",
        f"- Overall pass: {report['pass']}",
        f"- Gate tripped: {report['gate_tripped']}",
        "",
        f"**Acceptance sentence:** {report.get('acceptance') or '(not set)'}",
        "",
        f"**Never sentence:** {report.get('never') or '(not set)'}",
        "",
        "## Failing assertions",
        "",
    ]
    failing = [r for r in report["results"] if not r["pass"]]
    if not failing:
        lines.append("_(none)_")
    for r in failing:
        gate_mark = " (GATE)" if r["gate"] else ""
        lines.append(f"- **{r['id']}**{gate_mark}: {r['detail']}")
    lines += [
        "",
        "## Passing assertions",
        "",
    ]
    passing = [r for r in report["results"] if r["pass"]]
    if not passing:
        lines.append("_(none)_")
    for r in passing:
        lines.append(f"- {r['id']}: {r['detail']}")
    lines += [
        "",
        "## What was checked",
        "",
        "This report measures the product file directly against the external standard file.",
        "It does not read the maker's summary of its own work. A later run can rehearse this",
        "same assertion set against a planted bad example (see scripts/rehearse.sh).",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run an independent check against a product.")
    parser.add_argument("--config", required=True, help="Path to check.json")
    parser.add_argument("--alert-dir", default="alerts", help="Where to write blocker reports")
    parser.add_argument("--no-alert", action="store_true", help="Do not write a blocker file on fail")
    parser.add_argument("--json", action="store_true", help="Print the full JSON report on stdout")
    args = parser.parse_args(argv)

    config_path = pathlib.Path(args.config).resolve()
    if not config_path.exists():
        print(f"config not found: {config_path}", file=sys.stderr)
        return EXIT_CONFIG

    try:
        exit_code, report = run_check(config_path)
    except Exception as exc:
        print(f"check errored: {exc}", file=sys.stderr)
        return EXIT_CONFIG

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        verdict = "PASS" if exit_code == EXIT_PASS else ("GATE TRIPPED" if exit_code == EXIT_GATE else "FAIL")
        print(f"Independent check on '{report['job']}': {verdict}")
        for r in report["results"]:
            mark = "ok" if r["pass"] else "FAIL"
            gate_mark = " [GATE]" if r["gate"] else ""
            print(f"  - {r['id']}{gate_mark}: {mark} - {r['detail']}")

    if exit_code != EXIT_PASS and not args.no_alert:
        alert_dir = pathlib.Path(args.alert_dir).resolve()
        alert_path = write_alert(report, alert_dir)
        print(f"blocker report written: {alert_path}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
