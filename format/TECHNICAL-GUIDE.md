# /format

Clean up messy pasted text and file it as a `.txt` under `Claude-work/`.

## Why this exists

Pasting from a terminal, Slack preview, or word-wrapped output produces junk:
trailing whitespace, lines broken mid-sentence at 80 chars, leading indent
on every line, prompt glyphs like `⏺`, stray em dashes. This skill wraps a
small Python script that reverses all of that.

## What's in this folder

- `SKILL.md` — skill manifest Claude reads when picking the skill.
- `format.py` — the actual cleaner, pure stdlib Python.
- `README.md` — this file.
- `tests/input.messy.txt` — a real example of messy input.
- `tests/expected.txt` — what we want out of the cleaner.

## Running it manually

```bash
# From a file
python3 ~/.claude/skills/format/format.py -i raw.md -o clean.txt

# From stdin
pbpaste | python3 ~/.claude/skills/format/format.py --stdin -o clean.txt

# Preview only (no file written)
python3 ~/.claude/skills/format/format.py -i raw.md
```

## The cleaning rules

1. Strip CLI prompt glyphs (`⏺`, `●`, `> `) from line starts.
2. `rstrip()` every line.
3. If every non-empty line shares a common leading indent, remove it.
4. Rejoin lines that were word-wrapped mid-paragraph. Bullets, numbered
   lists, headings, and code fences stay on their own lines.
5. Replace em/en dashes:
   - `"Label — detail"` (short left side) becomes `"Label: detail"`.
   - Longer clauses become `", "`.
   - Un-spaced dashes (`word—word`) become `", "`.
6. Collapse runs of 3+ blank lines down to a single blank line.
7. Ensure the file ends with exactly one newline.

## How Claude uses it

When invoked via `/format`:

1. Writes the raw pasted text to `/tmp/format-input-<timestamp>.txt`.
2. Runs `format.py` with `--input` and `--output` pointing at the chosen
   destination in `Claude-work/`.
3. Reads the output back to verify the cleanup looks right.
4. Reports the final filename and path.

## Destination folder rules

- Search `Claude-work/CLIENTS/` and `Claude-work/PROJECTS/` for a fit.
- **Never create a new folder.** If nothing fits, ask the user.
- Match the date-stamped naming convention already in use in the folder.
- If a collision happens, append `-v2` or a timestamp — never overwrite.

## Testing

From this folder:

```bash
python3 format.py -i tests/input.messy.txt -o /tmp/format-test.txt
diff /tmp/format-test.txt tests/expected.txt
```

Exit code `0` from `diff` means the run matches the golden file.

<!-- skill-maintenance:start -->
## Maintenance

### Trigger

- GitHub checks the collection when the main branch changes, when a pull request opens or changes, and every Monday at 15:30 UTC.
- A separate cloud task checks for failed or missing runs every hour. Your computer can stay off.

### Inputs

- Read [SKILL.md](SKILL.md) for this skill's instructions.
- Read the [collection register](../maintenance/collection.json) for its recorded version and owner.
- Use the saved check results and a made-up example of any reported failure.

### What happens

1. The routine checks that this skill is registered and has an owner and README.
2. It reruns the tests listed for this skill. This skill is registered, but its behavior is not yet covered by the scheduled test runner. A passing collection check does not prove this skill works.
3. If a check fails, gets stuck, or no successful collection run appears for eight days, the alert task tells Rachael in ChatGPT.
4. Rachael coordinates the fix. A confirmed fix gets a regression test so the same problem is checked again.
5. Rachael decides whether to adopt an update. Installed copies are not replaced automatically.

### Outputs

- Test results and failure details appear in [GitHub Actions](https://github.com/RachaelQuisel/Skills/actions/workflows/maintained-skills.yml).
- Actionable alerts appear in ChatGPT. They cover recorded check failures, not unrecorded live use.
- Use the [support form](https://github.com/RachaelQuisel/Skills/issues/new?template=skill-maintenance.yml) to report a live problem.
- Follow the [maintenance guide](../maintenance/README.md) to review changes or return to an earlier version.

**Owner:** Rachael Quisel. **Live compatibility:** unverified.
<!-- skill-maintenance:end -->
