## Trigger

- The user invokes Humanize Output or asks it to improve an existing draft.
- The workflow runs in Claude Code with Python 3.10 or later.

## Inputs

- The user supplies pasted text or a selected text file.
- The reader, tone, and editing depth guide the suggestions.
- An optional saved checklist provides reviewed writing preferences, unwanted phrases, and allowed exceptions.
- Optional writing samples help propose new preferences.
- Names, dates, numbers, quotations, and required wording identify details to preserve.
- Edit decisions identify the suggestions to apply.
- A new output path identifies where to save the revision.

## What happens

1. If the draft is missing, the plugin requests it. If a selected file cannot be read, the plugin reports the error and stops.
2. The plugin checks answers already supplied. It asks one missing setup question at a time. It acknowledges each answer before continuing.
3. The questions cover the reader, tone, and editing depth. Light cleanup keeps the structure. Sentence revisions can change sentence wording. Structural changes can reorganize the draft.
4. If the user asks to skip questions, the plugin labels any remaining defaults. If the user cancels, it ends the edit pass without applying changes.
5. If a saved checklist is selected, the plugin loads it. A missing or unreadable checklist stops the workflow. Current answers override its preferences for this draft.
6. If the user wants to save preferences, the plugin obtains review of the rules. It saves them only after an explicit request. Saving an existing checklist identifier replaces that checklist.
7. The tool scans common phrases and saved unwanted phrases. Matching exceptions suppress their flags. Claude can add separate editorial observations.
8. The plugin shows numbered edits with the original wording, proposed wording, and a reason. A requested rewrite appears as a preview. It checks meaning and identifies protected details.
9. The plugin waits for edit decisions. Numbered acceptance approves only those suggestions. Explicit approval of the displayed rewrite approves that version. Rejection keeps the source wording.
10. If preferences or source text change, the plugin creates new suggestions. Earlier approval does not cover them.
11. The tool checks edit fields, character positions, source matches, overlaps, and protected details. Invalid records or changed source text stop the operation. Literal checks do not prove that every nuance stayed the same.
12. The tool applies accepted edits. It refuses the original path or an existing output file. If the destination cannot be written, it reports the cause and stops.
13. The plugin scans the saved revision for remaining issues. Rejected phrases can remain flagged.

## Outputs

- Setup questions and review suggestions appear in the conversation.
- A revised draft is saved as a new file in the selected output location.
- A text comparison shows accepted changes in the conversation.
- Remaining writing flags appear with the final result.
- An explicitly requested checklist is saved under `~/.local/share/de-slop/profiles/` or the selected data directory.
- A failed operation returns its cause and the next action needed.
