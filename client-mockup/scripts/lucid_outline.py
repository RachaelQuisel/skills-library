#!/usr/bin/env python3
"""Print a Lucidchart JSON export as a plain outline, so the mock-up diagram can be redrawn exactly.

Usage:
    python3 -I lucid_outline.py /path/to/Chart.json

What it prints:
    1. Every shape, numbered in process order (starting shapes first, then following the arrows),
       with its Lucid type and its exact text.
    2. Every line: from-shape -> to-shape (the arrowhead marks "to"), with the line's label.
    3. Sticky notes, listed separately.
    4. Things to report to Rachael. Draw the chart as exported and report these; never fix them silently:
       - more than one starting shape (a shape no arrow points into)
       - shapes with no lines at all
       - decision shapes with no line coming in, or with an outgoing line that has no label
       - decision shapes with two outgoing lines that have the same label (for example two "Yes")
       - lines that loop back to an earlier step
       - lines with an arrowhead on both ends or on neither end
       - lines connected to something that is not a shape in the export
       - text that looks like a typo (common patterns only; read every box yourself too)

The Lucid JSON export has no x/y positions. Lay the diagram out from the connections:
left to right and top to bottom, in the order this script prints.

Reads the file only. Writes nothing. Exits with an error message (never silently) if the
file is missing, is not JSON, or has no shapes.
"""
import json
import re
import sys
from collections import deque

TYPO_PATTERNS = [
    (r"\bwe're hold\b", "\"we're hold\" (probably \"we're holding\")"),
    (r"\b(\w+) \1\b", "a repeated word"),
    (r"\s{2,}", "double spaces"),
]


def text_of(item):
    parts = [t.get("text", "").strip() for t in item.get("textAreas", []) if t.get("text")]
    return " / ".join(p for p in parts if p)


def main(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        sys.exit(f"ERROR: file not found: {path}")
    except json.JSONDecodeError as exc:
        sys.exit(f"ERROR: {path} is not valid JSON ({exc}). Ask for a fresh Lucid export (File > Export > JSON).")

    pages = data.get("pages", [])
    if not pages:
        sys.exit("ERROR: the export has no pages. Ask for a fresh Lucid export.")

    for page in pages:
        items = page.get("items", {})
        shapes = items.get("shapes", [])
        lines = items.get("lines", [])
        if not shapes:
            print(f"# Page {page.get('title', '')!r}: no shapes. Skipping.\n")
            continue

        stickies = [s for s in shapes if "Sticky" in s.get("class", "")]
        blocks = [s for s in shapes if "Sticky" not in s.get("class", "")]
        by_id = {s["id"]: s for s in blocks}
        flags = []

        edges = []  # (src, dst, label)
        for ln in lines:
            e1, e2 = ln.get("endpoint1", {}), ln.get("endpoint2", {})
            a, b = e1.get("connectedTo"), e2.get("connectedTo")
            s1, s2 = e1.get("style", "None"), e2.get("style", "None")
            if s2 != "None" and s1 == "None":
                src, dst = a, b
            elif s1 != "None" and s2 == "None":
                src, dst = b, a
            else:
                src, dst = a, b
                flags.append(("both", a, b, "both ends" if s1 != "None" else "neither end"))
            for end in (src, dst):
                if end not in by_id:
                    flags.append(("missing", end))
            edges.append((src, dst, text_of(ln)))

        incoming = {sid: 0 for sid in by_id}
        out = {sid: [] for sid in by_id}
        for src, dst, label in edges:
            if dst in incoming:
                incoming[dst] += 1
            if src in out:
                out[src].append((dst, label))

        # Process order: start at shapes nothing points into (in export order), then follow arrows.
        starts = [s["id"] for s in blocks if incoming[s["id"]] == 0]
        order, seen = [], set()
        queue = deque(starts or [blocks[0]["id"]])
        while queue or len(seen) < len(blocks):
            if not queue:
                queue.append(next(s["id"] for s in blocks if s["id"] not in seen))
            sid = queue.popleft()
            if sid in seen or sid not in by_id:
                continue
            seen.add(sid)
            order.append(sid)
            for dst, _ in out[sid]:
                if dst not in seen:
                    queue.append(dst)
        num = {sid: i + 1 for i, sid in enumerate(order)}

        def name(sid):
            return f"{num[sid]}" if sid in num else repr(sid)

        print(f"# Page: {page.get('title', '')}  (chart: {data.get('title', '')})\n")
        print("## Shapes, in process order")
        for sid in order:
            s = by_id[sid]
            print(f"{num[sid]}. [{s.get('class', '')}] {text_of(s)!r}")

        print("\n## Lines (from -> to)")
        for src, dst, label in sorted(edges, key=lambda e: (num.get(e[0], 999), num.get(e[1], 999))):
            print(f"{name(src)} -> {name(dst)}" + (f"   label: {label!r}" if label else ""))

        if stickies:
            print("\n## Sticky notes (not connected to any step unless a line says so)")
            for s in stickies:
                print(f"- {text_of(s)!r}")

        # Loops back: an arrow to a shape already on the current path.
        def dfs(sid, stack, visited):
            visited.add(sid)
            stack.add(sid)
            for dst, _ in out.get(sid, []):
                if dst in stack:
                    flags.append(("loop", sid, dst))
                elif dst in by_id and dst not in visited:
                    dfs(dst, stack, visited)
            stack.discard(sid)

        visited = set()
        for sid in order:
            if sid not in visited:
                dfs(sid, set(), visited)

        report = []
        if len(starts) > 1:
            report.append(f"There are {len(starts)} starting shapes ({', '.join(name(s) for s in starts)}). "
                          "A workflow usually has one. Check whether an arrow is missing into one of them.")
        for sid in order:
            s = by_id[sid]
            if incoming[sid] == 0 and not out[sid]:
                report.append(f"Shape {name(sid)} has no lines at all.")
            if s.get("class") == "DecisionBlock":
                if incoming[sid] == 0:
                    report.append(f"Decision {name(sid)} ({text_of(s)!r}) has no line coming in, so nothing leads to it.")
                labels = [lab for _, lab in out[sid]]
                if not labels:
                    report.append(f"Decision {name(sid)} has no lines going out.")
                elif any(not lab for lab in labels):
                    report.append(f"Decision {name(sid)} has an outgoing line with no label.")
                seen_labels = {}
                for lab in labels:
                    if lab:
                        seen_labels[lab.strip().lower()] = seen_labels.get(lab.strip().lower(), 0) + 1
                for lab, count in seen_labels.items():
                    if count > 1:
                        report.append(f"Decision {name(sid)} has {count} outgoing lines with the same label "
                                      f"({lab!r}). One of them is probably meant to say something else.")
                odd = [lab for lab in labels if lab and lab.lower() not in ("yes", "no")]
                if odd:
                    report.append(f"Decision {name(sid)} has an outgoing line labeled {odd} instead of Yes/No. "
                                  "Ask what it means and confirm its direction.")
            for pattern, desc in TYPO_PATTERNS:
                if re.search(pattern, text_of(s), flags=re.IGNORECASE):
                    report.append(f"Shape {name(sid)} may have a typo: {desc}.")
        for f in flags:
            if f[0] == "both":
                report.append(f"The line between {name(f[1])} and {name(f[2])} has arrowheads on {f[3]}.")
            elif f[0] == "missing":
                report.append(f"A line connects to {f[1]!r}, which is not a shape in this export.")
            elif f[0] == "loop":
                report.append(f"{name(f[1])} -> {name(f[2])} loops back to an earlier step. Confirm this is intended.")

        print("\n## Report to Rachael (draw as exported; do not fix silently)")
        for r in dict.fromkeys(report) or ["Nothing found."]:
            print(f"- {r}")
        print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
