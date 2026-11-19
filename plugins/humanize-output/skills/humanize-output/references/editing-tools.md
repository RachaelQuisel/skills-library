# Editing tool reference

## Commands

- Replace `<skill-dir>` with this installed skill folder.
- Use `--data-dir` before the command to select another profile storage location.

```text
python3 <skill-dir>/scripts/deslop.py [--data-dir <directory>] profile-save --input <profile.json>
python3 <skill-dir>/scripts/deslop.py [--data-dir <directory>] profile-get --id <profile_id>
python3 <skill-dir>/scripts/deslop.py [--data-dir <directory>] scan --draft <draft.txt> [--profile <profile_id>]
python3 <skill-dir>/scripts/deslop.py apply --draft <draft.txt> --edits <edits.json> --output <revised.txt>
```

## Saved checklist

- The profile uses JSON, a text format for named fields and lists.
- `profile_id` identifies the checklist. Use 1 to 64 characters. Start with a letter or number. Use only letters, numbers, underscores, or hyphens.
- `rules` lists the reviewed writing preferences. Claude uses these rules when proposing changes. The phrase scan does not interpret them.
- `disliked_phrases` lists wording to flag.
- `exceptions` lists wording to leave unflagged.
- `reviewed` must be `true` after user review. An explicit instruction to save supplied rules counts as review.
- The three list fields can be empty. Each listed value must contain text.
- Saving an existing `profile_id` replaces that checklist.

## Edit decisions

- The edits file is a JSON object. An object stores named fields.
- `protected_phrases` lists exact wording to preserve.
- `edits` lists proposed changes.
- `start` and `end` are character positions in the exact source draft. Counting starts at zero. The end position is excluded.
- `original` must match the selected source text.
- `replacement` contains the proposed new text.
- `accepted` is `true` or `false`. The tool applies only `true` edits.

```json
{"protected_phrases":["Alex"],"edits":[{"start":0,"end":4,"original":"Read","replacement":"Review","accepted":true}]}
```

## Checks and errors

- The tool validates every edit record, including rejected edits.
- The phrase scan ignores letter case. It flags whole phrases and respects matching exceptions.
- Number and quotation checks compare the original sequence with the revised sequence.
- Protected phrases must keep the same occurrence counts.
- These checks do not prove that meaning or factual accuracy stayed the same. Review those separately.
- The output folder must already exist. The tool does not create it.
- Errors use `error:` and return exit code `1`. A successful command returns exit code `0`.
- Missing files, invalid JSON, invalid profiles, changed source text, overlapping accepted edits, or protected-detail changes stop the operation.
