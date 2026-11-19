---
name: format
version: 1.0.1
description: Cleans up messy pasted text (terminal word-wrap artifacts, trailing spaces, em dashes, collapsed blank lines) or a .md document and saves it as a well-formatted .txt file in the right folder under /Users/rachaelquisel/Claude-work/. Use when the user says "format this", "/format", "clean up this text", "turn this into a txt", "remove terrible spacing", or pastes output with obvious wrap artifacts and asks for a file.
tags:
  - skill
---

# /format

## Purpose in plain English

This skill helps you clean up pasted text or a Markdown document so its spacing and layout are readable.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Takes pasted messy text or a `.md` file, strips the garbage, and files a clean `.txt` in the right place under `/Users/rachaelquisel/Claude-work/`.

## When to run this

- User says `/format`, "format this", "clean up this text", "turn this into a txt", "remove terrible spacing", or similar.
- A paste has obvious terminal-wrap artifacts (lines broken mid-sentence, leading spaces on every line, `⏺` prompt glyphs, runs of blank lines).
- User wants a `.md` converted to a clean `.txt`.

## What it does

1. Saves the raw input to a temp file.
2. Runs `format.py` to clean it:
   - Strips terminal prompt glyphs (`⏺`, `●`, leading `> `).
   - Removes trailing whitespace on every line.
   - Removes uniform leading indent (e.g., every line starts with two spaces).
   - Unwraps lines broken mid-paragraph by terminal word-wrap (respects bullets, headings, code fences).
   - Replaces em/en dashes with `:`, `,`, or a sentence break (per Rachael's feedback memory — no em dashes).
   - Collapses runs of 3+ blank lines down to one.
3. Finds the right destination folder by searching `Claude-work/CLIENTS/` and `Claude-work/PROJECTS/` for a folder matching the subject of the text.
4. Names the file with a date stamp matching the convention already in use in the target folder (e.g., `aymg-update-2026-04-22.txt`).
5. Writes the cleaned `.txt` and reports back the filename and path.

## Filing rules (important)

- **Never create a new folder.** Search existing `CLIENTS/` and `PROJECTS/` subfolders first.
- If nothing fits, **ask the user** where to file it instead of inventing a folder.
- Match the filename convention already in the target folder (date stamp, kebab-case).
- If a file of the same name exists, bump the name with a suffix (`-v2`, or a time stamp) — never overwrite.

## Subfolder routing (do this before writing the output path)

Once you've identified the target client or project folder, check whether it already has subfolders that match the file's content type. If a matching subfolder exists, route the file into it. If no matching subfolder exists, fall back to the folder root.

Detection rules:

| File looks like | Detection signals | Subfolder to route into (case-insensitive match) |
|---|---|---|
| Email | filename starts with `email-` or `email_`, content opens "Hi <Name>," / "Hey <Name>:" | `Emails/` |
| Transcript | filename starts with `transcript-`, content is a meeting / call dialogue | `Transcripts/`, or any folder starting with `Transcripts_` |
| Data export | `.csv`, `.tsv`, `.xlsx`, or filename mentions a data source (binti, blackboard, quickbooks) | `Exports/` (and within it, a `<Source>/` subfolder if one exists) |
| Living project doc | filename matches `vision-and-scope`, `proposal-and-prd`, `performance`, `projects-outcomes-tasks` | `Project Documentation/` or `project-docs/` |
| Python script tied to an export | `.py` operating on a known export data source | `Exports/<Source>/` if it exists, else `Code/<Source>/` |
| General script | `.py`, `.js` not tied to a specific export | `Code/` or `code/` |

Routing procedure:

1. Decide content type from filename + first lines of content.
2. `ls` the target client folder and look for a subfolder matching the type (case-insensitive, allow suffixes like `Transcripts_GOL`).
3. If found, set the output path to `<client>/<subfolder>/<filename>`.
4. If not found, write to the client folder root.
5. **Never create a new subfolder** as part of routing. Folder structure is intentional and curated by Rachael.

## Naming convention by file type

- **Snapshots get a date stamp** (`-YYYY-MM-DD`): emails, transcripts, exports, call notes, point-in-time updates. These never get edited in place.
- **Living docs do not get a date stamp**: `vision-and-scope.md`, `proposal-and-prd.md`, `performance.md`, `projects-outcomes-tasks.md`. These get updated in place. The filesystem mtime is the timestamp.
- If unsure whether a doc is a snapshot or living, ask before writing.

## How to invoke

Worked example: cleaning the AYMG ad-to-editorial-linking teaching doc.

Source: `/Users/rachaelquisel/Claude-Work/CLIENTS/AY Media_Jay_Danzy/teaching/ad-to-editorial-linking-aymg-teaching-doc.md`
Output: `/Users/rachaelquisel/Claude-Work/CLIENTS/AY Media_Jay_Danzy/teaching/ad-to-editorial-linking-aymg-teaching-doc.txt`

The folder already exists (`teaching/` under the AYMG client folder), the slug is kebab-case, and the doc is a living teaching reference — no date stamp.

```bash
# From a file (the worked example above)
python3 /Users/rachaelquisel/.claude/skills/format/format.py \
    --input "/Users/rachaelquisel/Claude-Work/CLIENTS/AY Media_Jay_Danzy/teaching/ad-to-editorial-linking-aymg-teaching-doc.md" \
    --output "/Users/rachaelquisel/Claude-Work/CLIENTS/AY Media_Jay_Danzy/teaching/ad-to-editorial-linking-aymg-teaching-doc.txt"

# From stdin (paste piped through)
python3 /Users/rachaelquisel/.claude/skills/format/format.py \
    --stdin \
    --output "/Users/rachaelquisel/Claude-Work/CLIENTS/<client>/<slug>-YYYY-MM-DD.txt"

# Preview (stdout, no file written)
python3 /Users/rachaelquisel/.claude/skills/format/format.py --input /tmp/messy.md
```

Use the `Write` tool to dump the raw pasted text to a temp file first, then run the script via `Bash`. Read the output file back to confirm before reporting the final path to the user.

## Checklist before reporting done

- [ ] `.txt` exists at the reported path
- [ ] No trailing whitespace, no triple-blank runs
- [ ] No em dashes remain
- [ ] Filename matches convention in the target folder
- [ ] Location is an existing folder (not a newly created one)
- [ ] Reported the filename AND full path back to the user

## References

- `format.py` — the cleaner script
- `README.md` — longer-form usage, rule rationale, examples
- `tests/` — sample inputs and expected outputs for regression checks
