# Post-Run Analysis: /format skill (first build + end-to-end test)

Date: 2026-04-22

## What shipped

`~/.claude/skills/format/`:

| File | Purpose |
| --- | --- |
| `SKILL.md` | Skill manifest Claude reads to pick this up when invoked |
| `format.py` | Pure stdlib Python cleaner |
| `README.md` | Human-readable doc with rationale and examples |
| `tests/input.messy.txt` | Real-world messy paste (the AYMG recap from earlier) |
| `tests/expected.txt` | Golden output for regression checks |
| `POST-RUN-ANALYSIS.md` | This file |

XRAY task created, accepted, and linked to Internal Operations:
[rec8uk0HsB8o7A0fm](https://airtable.com/appQAdxI2hDNJj1g5/pag9JHVBBRBOfi8lS/rec8uk0HsB8o7A0fm)

## End-to-end result

Input: the AYMG terminal-wrapped paste with ⏺ glyph, 1-space uniform indent,
em dashes, mid-paragraph line wraps, and a trailing bullet continuation.

Output (after `format.py`):
```
Spent most of the week deep in AYMG's database cleanup. Here's where it landed:

- Split line items out from contracts so each one is its own record
- Stood up two new tables: Agencies and Advertisers, both linked to Contacts
- Linked contacts to contracts (and through that, to the right agency/advertiser)
- Blew up the "production + billing" combo chip into separate contact types, production, billing, and the 4-5 other types I found hiding in there once I actually looked

The old setup had every contact dumped in one table, which was killing any automation that wanted to pull "send this to billing" or "send this to the advertiser." Now those routes actually exist.

Numbers: 15,000+ contacts, 14,000 linked to the correct contact via script. Pretty hyped about that hit rate tbh.

Next mountain is linking contracts to products. This one's gnarly, product depends on a bunch of overlapping categories, and I've already done several Python passes without a clean answer. Historical contracts are not product-linked yet. Happy to walk through the logic
```

Final diff against golden file: **PASS** (exit code 0, zero differences).

## Bugs caught during testing

**Bug 1: dedent blocked by glyph-stripped first line.**
`remove_common_leading_indent()` used `min(leading_spaces)` across non-empty
lines. The first line had 0 leading spaces after the ⏺ glyph was stripped,
while every other line had 1, so `min` was 0 and no dedent happened.
Symptom: every bullet in the output still had a leading space.
Fix: switched to mode (most common leading-space count) with a majority-vote
threshold so one outlier doesn't block the strip.

**Bug 2: wrapped bullet continuation not joined.**
`unwrap_terminal_lines()` treated "previous line is a bullet" as a reason
NOT to merge the next line, which meant the continuation " hiding in there
once I actually looked" got stranded as its own line under the last bullet.
Fix: removed the `prev_is_structure` short-circuit. Now a wrapped bullet
continuation joins the bullet above it. We still bail if the current line
starts a new structure or the previous line is a quote/code-fence.

**Non-bug: CRLF in the first golden file.**
First pass: `diff` showed every line differed. `od -c` revealed `\r` line
terminators in the Write-tool-produced `expected.txt`. Regenerated the
golden by `cp`ing directly from the LF output. Not a `format.py` issue,
but worth noting if anyone re-creates the golden by hand.

## Design decisions

- **Pure stdlib** — no `pip install` needed. Runs under any `python3` on
  Rachael's box.
- **Dash replacement is context-sensitive.** Short left side (≤3 words) gets
  `: `, longer clauses get `, `. Un-spaced dashes (`word—word`) always get
  `, `. This follows the "no em dashes" feedback rule.
- **Doesn't invent folders.** The skill file explicitly tells Claude to
  search `CLIENTS/` and `PROJECTS/` first and ask before creating anything
  new. Ties back to Rachael's filing preference.
- **Tests are real messy input**, not synthetic. The golden was produced
  from the actual AYMG paste, so regressions will show up against real data.

## How to regression-test in one line

```bash
python3 ~/.claude/skills/format/format.py \
    -i ~/.claude/skills/format/tests/input.messy.txt \
    -o /tmp/format-test.txt \
  && diff /tmp/format-test.txt ~/.claude/skills/format/tests/expected.txt \
  && echo "PASS"
```

## Known limitations / future work

- **No markdown-to-txt rendering.** `.md` input is treated as plain text.
  If a real conversion (stripping `**bold**`, `` `code` `` backticks,
  resolving headings to ALL CAPS, etc.) becomes needed, add a `--markdown`
  flag that runs a second pass.
- **Only spaces, not tabs.** If a paste ever has tab indents, the dedent
  won't catch them. Easy extension but not worth doing speculatively.
- **Single test case.** Add more `tests/inputN.messy.txt` / `expectedN.txt`
  pairs as new paste shapes come up (code fences, nested bullets, numbered
  lists spanning pages).
- **No `pbpaste` shortcut in `format.py`.** The skill relies on Claude to
  write the paste to a temp file first. If Rachael wants a shell alias like
  `fmt` that reads from the clipboard directly, add one.

## Checklist

- [x] Skill registered and picked up by Claude (confirmed via skill list)
- [x] Python script is stdlib-only and runs cleanly
- [x] Tests exist with real-world input and a golden file
- [x] `diff` against golden file is empty
- [x] README documents rules and how to run manually
- [x] SKILL.md tells Claude to search existing folders and never invent new ones
- [x] XRAY task created and accepted in Internal Operations
