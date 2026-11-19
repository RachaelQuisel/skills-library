#!/usr/bin/env python3
"""
format.py — Clean pasted messy text (terminal wrap artifacts, em dashes,
trailing whitespace, collapsed blank lines) and save as a .txt file.

Usage:
    python3 format.py --input input.md --output /path/to/out.txt
    python3 format.py --stdin --output /path/to/out.txt
    python3 format.py --input raw.txt   # prints cleaned text to stdout

Designed to be invoked by the /format skill in Claude Code. Handles:
  - Wonky terminal-wrap artifacts (lines broken at 80/120 chars mid-sentence,
    each line prefixed with one or more spaces from a box-drawn quote)
  - Leading indentation applied uniformly to every line
  - Trailing whitespace on every line
  - Runs of 3+ blank lines collapsed to one
  - Stray UI glyphs like the Claude prompt marker (⏺)
  - Em dashes replaced with ": " / ", " / ". " per Rachael's feedback memory
  - Bullet markers preserved ( -, *, +, numbered )
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# -- Constants ---------------------------------------------------------------

# Characters that are safe replacements for em/en dashes depending on context.
# Rachael's rule: no em dashes. Prefer colon, comma, or a new sentence.
EM_DASH = "\u2014"   # —
EN_DASH = "\u2013"   # –

# Claude Code CLI artifacts sometimes appear at the start of a paste.
PROMPT_GLYPHS = ("\u23fa", "\u25cf", "\u2022\u2022", "> ")

BULLET_RE = re.compile(r"^\s*([-*+]|\d+[.)])\s+")
HEADER_RE = re.compile(r"^#{1,6}\s+")


# -- Cleaning steps ----------------------------------------------------------

def strip_prompt_glyphs(text: str) -> str:
    """Remove CLI prompt markers like ⏺ that stick around after a copy-paste."""
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.lstrip()
        for g in PROMPT_GLYPHS:
            if stripped.startswith(g):
                stripped = stripped[len(g):].lstrip()
        # Preserve original leading whitespace intent by writing stripped
        # version; we'll dedent later anyway.
        cleaned.append(stripped if stripped != line.lstrip() else line)
    return "\n".join(cleaned)


def strip_trailing_whitespace(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines())


def remove_common_leading_indent(text: str) -> str:
    """If most non-empty lines share the same run of leading spaces, strip it.

    Uses the mode of leading-space counts (not min) so one outlier line with
    no indent, e.g. a glyph-stripped first line, doesn't block dedent.
    """
    from collections import Counter

    lines = text.splitlines()
    non_empty = [ln for ln in lines if ln.strip()]
    if len(non_empty) < 2:
        return text

    def leading_spaces(s: str) -> int:
        n = 0
        for ch in s:
            if ch == " ":
                n += 1
            else:
                break
        return n

    counts = [leading_spaces(ln) for ln in non_empty]
    mode, mode_count = Counter(counts).most_common(1)[0]
    # Require majority of non-empty lines to share the indent before stripping
    if mode == 0 or mode_count < max(2, len(non_empty) // 2 + 1):
        return text
    return "\n".join(
        ln[mode:] if ln.strip() and leading_spaces(ln) >= mode else ln.lstrip()
        for ln in lines
    )


def unwrap_terminal_lines(text: str) -> str:
    """Merge lines that were broken by terminal word-wrap mid-paragraph.

    Heuristic: inside a paragraph (bounded by blank lines), if a line does
    NOT end in sentence-ending punctuation and the next line does NOT start
    with a bullet, heading, or blank, join them with a single space.

    Keeps bullets, numbered lists, and headings on their own lines.
    """
    paragraphs = re.split(r"\n\s*\n", text)
    out_paragraphs = []
    for para in paragraphs:
        lines = para.splitlines()
        if not lines:
            out_paragraphs.append("")
            continue

        merged = [lines[0]]
        for line in lines[1:]:
            prev = merged[-1]
            prev_ends_sentence = bool(re.search(r"[.!?:;]['\"\)]?\s*$", prev))
            starts_structure = (
                BULLET_RE.match(line)
                or HEADER_RE.match(line)
                or line.strip().startswith(">")
                or line.strip().startswith("```")
            )
            prev_is_code_or_quote = (
                prev.strip().startswith(">") or prev.strip().startswith("```")
            )

            # If current line starts a new structural element, break.
            # If previous line was code/quote, also break.
            # Otherwise, join — including wrapped bullet continuations.
            if starts_structure or prev_is_code_or_quote or prev_ends_sentence:
                merged.append(line)
            else:
                merged[-1] = prev.rstrip() + " " + line.strip()
        out_paragraphs.append("\n".join(merged))
    return "\n\n".join(out_paragraphs)


def replace_em_dashes(text: str) -> str:
    """Replace em/en dashes with context-appropriate punctuation.

    Rules (best effort):
      - " — " or " – " between clauses -> ": " if the left side is a label,
        otherwise ", ". We keep it simple: default to ": " when the left
        side is <= 3 words, else ", ".
      - Leading "— " at start of a line -> "" (just drop it, likely a quote).
      - "word—word" (no spaces) -> "word, word".
    """
    def replace(match: re.Match) -> str:
        left, dash, right = match.group(1), match.group(2), match.group(3)
        left_words = left.strip().split()
        if len(left_words) <= 3 and left.strip():
            return f"{left}: {right.lstrip()}"
        return f"{left}, {right.lstrip()}"

    # Spaced dashes
    text = re.sub(
        r"([^\n]*?)(\s+[" + EM_DASH + EN_DASH + r"]\s+)(.*)",
        replace,
        text,
    )
    # Un-spaced dashes -> ", "
    text = re.sub(r"[" + EM_DASH + EN_DASH + r"]", ", ", text)
    return text


def collapse_blank_lines(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


# -- Orchestration -----------------------------------------------------------

def clean(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = strip_prompt_glyphs(text)
    text = strip_trailing_whitespace(text)
    text = remove_common_leading_indent(text)
    text = unwrap_terminal_lines(text)
    text = replace_em_dashes(text)
    text = collapse_blank_lines(text)
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Clean messy pasted text into .txt")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", "-i", help="Input file path (.txt or .md)")
    src.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("--output", "-o", help="Output .txt path (omit to print)")
    args = parser.parse_args(argv)

    if args.stdin:
        raw = sys.stdin.read()
    else:
        raw = Path(args.input).read_text(encoding="utf-8")

    cleaned = clean(raw)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(cleaned, encoding="utf-8")
        sys.stderr.write(f"Wrote {out_path}\n")
    else:
        sys.stdout.write(cleaned)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
