#!/usr/bin/env python3
"""
Validate an interfaces_audit.md document.

Checks:
  * Every Markdown table is well-formed (each body row has the same column count as its
    header, accounting for escaped pipes).
  * Reports counts of unresolved IDs (⚠️DELETED …) and orphaned trigger buttons
    (NO CONNECTION) so the reader can confirm those are real findings, not capture gaps.

Exit code 0 if no structural issues; 1 otherwise. Findings (deleted refs / orphans) do not
fail the run — they are surfaced for review.

Usage: python check_pages.py interfaces_audit.md
"""
import re, sys

def col_count(line):
    # split on unescaped pipes; drop leading/trailing empties from the border pipes
    cells = re.split(r"(?<!\\)\|", line)
    if cells and cells[0].strip() == "":
        cells = cells[1:]
    if cells and cells[-1].strip() == "":
        cells = cells[:-1]
    return len(cells)

def main(path):
    lines = open(path).read().splitlines()
    issues = []
    i = 0
    n_tables = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1]):
            # table header at i, separator at i+1
            n_tables += 1
            hdr = col_count(line)
            sep = col_count(lines[i + 1])
            if sep != hdr:
                issues.append(f"line {i+2}: separator has {sep} cols, header has {hdr}")
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                c = col_count(lines[j])
                if c != hdr:
                    issues.append(f"line {j+1}: row has {c} cols, header has {hdr}: {lines[j][:80]}")
                j += 1
            i = j
        else:
            i += 1

    text = "\n".join(lines)
    deleted_tbl = len(re.findall(r"DELETED TABLE", text))
    deleted_fld = len(re.findall(r"DELETED FIELD", text))
    orphans = len(re.findall(r"NO CONNECTION", text))

    print(f"tables checked: {n_tables}")
    print(f"findings (not errors): DELETED TABLE refs={deleted_tbl}, "
          f"DELETED FIELD refs={deleted_fld}, orphaned trigger buttons={orphans}")
    if issues:
        print(f"\n{len(issues)} STRUCTURAL ISSUE(S):")
        for m in issues[:50]:
            print("  -", m)
        return 1
    print("OK — all tables well-formed.")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python check_pages.py interfaces_audit.md")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
