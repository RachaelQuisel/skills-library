#!/usr/bin/env python3
"""Validate markdown tables: every row in a table block must have the same
number of cells as its header. Counts only UNescaped pipes."""
import re, sys, glob

def count_cells(line):
    # split on unescaped pipes
    parts = re.split(r"(?<!\\)\|", line.strip())
    # leading/trailing empty from outer pipes
    if parts and parts[0] == "": parts = parts[1:]
    if parts and parts[-1] == "": parts = parts[:-1]
    return len(parts)

def check(path):
    lines = open(path).read().split("\n")
    issues = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].strip()
        # table starts: a | line followed by a separator |---|---| line
        if line.startswith("|") and i+1 < n and re.match(r"^\|?[\s:|-]+\|[\s:|-]+$", lines[i+1].strip()):
            header_cells = count_cells(line)
            sep_cells = count_cells(lines[i+1])
            block_start = i+1
            if sep_cells != header_cells:
                issues.append((i+1, f"separator has {sep_cells} cells, header has {header_cells}", lines[i+1].strip()[:80]))
            j = i+2
            while j < n and lines[j].strip().startswith("|"):
                c = count_cells(lines[j])
                if c != header_cells:
                    issues.append((j+1, f"row has {c} cells, header has {header_cells}", lines[j].strip()[:90]))
                j += 1
            i = j
        else:
            i += 1
    return issues

files = sorted(glob.glob("**/*.md", recursive=True))
total = 0
for f in files:
    iss = check(f)
    status = "OK" if not iss else f"{len(iss)} ISSUE(S)"
    print(f"{status:14} {f}")
    for ln, msg, snippet in iss[:8]:
        print(f"    line {ln}: {msg}\n      {snippet}")
        total += 1
print(f"\nTotal table-row issues: {total}")
