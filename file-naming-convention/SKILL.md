---
name: file-naming-convention
version: 1.4.8
description: >
  Apply this canonical filename pattern any time you save an artifact under
  ~/Claude-Work/CLIENTS/client/, apply it by default, don't wait for the
  user to ask about naming. Pattern is
  CLIENT-Type-YYYY-MM-DD[-topic][-vn].ext. Trigger on saving transcripts,
  debriefs, call notes, meeting prep, summaries, session handoffs, post-run
  analyses, plans, briefs, or audit findings, any client-folder artifact that
  needs to be findable in Finder without opening. Also trigger when renaming
  an existing artifact saved with a vague name (e.g., "session_handoff.md",
  "notes.md", "transcript.txt"). Do NOT trigger for code files, scripts in
  scripts/ folders, config files, temp files in /tmp/, or anything outside
  ~/Claude-Work/CLIENTS/, those follow their own conventions.
---

# File Naming Convention

## Purpose in plain English

This skill helps you give saved client documents consistent names so their purpose and date are easy to recognize.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Every client-folder artifact gets a filename that tells the reader who it's about, what kind of artifact it is, when it was created, and which version they're looking at, all without opening it.

## The pattern

```
<CLIENT>-<Type>-YYYY-MM-DD[-topic][-v<n>].ext
```

Square brackets = optional. Drop `-topic` if the Type+date already disambiguates. Drop `-v1` unless a `v2` exists.

## When to use this

Use for any artifact saved under `~/Claude-Work/CLIENTS/<client>/`: transcripts, debriefs, call notes, meeting prep, summaries, session handoffs, post-run analyses, plans, briefs, audits, education docs.

## When NOT to use this

Skip the convention for:
- **Code files**: JavaScript, Python, TypeScript, etc. follow code conventions (e.g., `kickoff-dispatcher.js`, `backfill_field_descriptions_2026-06-08.py`)
- **Scripts** in `scripts/` folders, date-suffix is helpful (`...2026-06-08.py`) but `<CLIENT>-<Type>` prefix isn't
- **Config files**.`.env`, `package.json`, etc.
- **Temp files** in `/tmp/` - naming doesn't matter; they're disposable
- **Files outside `~/Claude-Work/CLIENTS/`**, personal projects, system configs, dotfiles all follow their own conventions

If the file's purpose is operational (a script that runs, a config that's read) rather than narrative (an artifact someone reads later to remember what happened), this convention probably doesn't apply.

## Where each artifact type lives

| Type | Subfolder | Notes |
|---|---|---|
| Transcript, Debrief | `Transcripts/` | One canonical subfolder per client, never `Transcripts_<CODE>` |
| CallNotes, MeetingPrep, Summary | `Transcripts/` or root | Use root for one-offs, `Transcripts/` if frequent |
| Handoff, POST_RUN, Plan | `tasks/` | Alongside `todo.md`, `lessons.md` |
| Audit, Brief, education docs | `Project Documentation/` | The reference shelf |
| Client-team role education | `teaching/` | E.g., `emg-learning-ae.md` |
| Superseded prior version | `Archive/<original-subpath>` | Never delete; archive |

One copy per artifact. If a Word export and PDF export of the same source exist, they share the base name with different extensions, they're the same artifact in different formats, not two separate artifacts.

## The fields

### `<CLIENT>` (required)

| Client | Code |
|---|---|
| Example Media | `EMG` |
| Example Nonprofit | `CC` |
| Example Agency | `EA` |
| Example Health | `EH` |
| Terra FS | `TerraFS` |

For a new client, define a code in PascalCase or uppercase and add it to the client's `README.md`.

### `<Type>` (required)

| Type | Use it for |
|---|---|
| `Transcript` | Raw transcript of a call or meeting |
| `Debrief` | XRAY Debrief export (from the Debrief Airtable) |
| `CallNotes` | Notes during a call (not a transcript) |
| `MeetingPrep` | Pre-meeting prep doc |
| `Summary` | Post-meeting or post-session summary |
| `Handoff` | Session handoff to pick up where you left off |
| `POST_RUN` | Post-run analysis from an `--apply` script |
| `Plan` | Project plan or roadmap |
| `Brief` | One-page brief for a stakeholder |
| `Audit` | Audit findings (schema, data, automations) |
| `Agreement` | Signed client/legal documents (enrollment agreements, contracts), date = date received |
| `Sample` | Example artifacts kept for reference (rendered output samples, design comps) |

PascalCase. Add new types here with one-line definition when needed.

### `YYYY-MM-DD` (required)

ISO date. The date the artifact was created, or the date it pertains to (transcript date for a transcript, meeting date for prep), whichever helps a future reader find it.

### `-topic` (optional)

Use when:
- Multiple artifacts of the same Type land on the same date
- The Type alone doesn't tell you what's inside
- A future Finder-scan needs disambiguation

Style: PascalCase, kebab-case, or mixed. Be specific over generic. Use `+` to separate themes when no single theme dominates.

For Debriefs pulled from the XRAY Debrief Airtable, append `-<rec8>` (last 8 chars of the record ID) instead of a topic, uniqueness comes from the record ID:
```
EMG-Debrief-2026-05-20-example-media-&-xray-weekly-check-in-pV8Lz0h6.md
```

### `-v<n>` (optional)

Omit by default. Add the moment a `v2` lands, then rename the original to `-v1` for clarity. Continue: `-v3`, `-v4`.

For in-progress drafts (multiple iterations before publishing), use `-draft<n>` to signal pre-publish state:
```
EMG-Plan-2026-06-09-EmailAutomationFinalShip-draft1.md
EMG-Plan-2026-06-09-EmailAutomationFinalShip-draft2.md
EMG-Plan-2026-06-09-EmailAutomationFinalShip-v1.md   ← published
```

### `.ext` (required)

Match the actual format. Most common: `.md`. Also `.docx`, `.pdf`, `.html`, `.json`, `.csv`.

## Examples

### Good

```
EMG-Handoff-2026-06-09-EmailAutomationShip+SchemaDocPass-v1.md
EMG-Debrief-2026-06-05-example-media-weekly-ssbxCSaE.md
CC-MeetingPrep-2026-05-22-EnrollmentBlockerWalkthrough.md
EA-Audit-2026-06-04-TrainingWorkflowSchemaDrift.md
EH-Transcript-2026-05-09.md
TerraFS-POST_RUN-2026-06-02-ClaimResponseApply.md
```

### Bad: and the fix

| Bad | Why it fails | Fix |
|---|---|---|
| `session_handoff.md` | No client, generic type, no date, no topic, no version, useless in Finder | `EMG-Handoff-2026-06-09-<topic>-v1.md` |
| `notes.md` | Tells nothing about who, what, or when | `EMG-CallNotes-2026-06-09-<topic>.md` |
| `transcript-call-notes-2026-04-02.md` | Wrong field order, conflated types, lowercase | `EMG-Transcript-2026-04-02-<topic>.md` |
| `emg-handoff-2026-06-09.md` | Lowercase client code breaks alphabetical sort grouping | `EMG-Handoff-2026-06-09-<topic>.md` |
| `2026-06-09-handoff.md` | Date-first prevents grouping by client | `EMG-Handoff-2026-06-09-<topic>.md` |

## Renaming an existing badly-named file

When you find a file that doesn't follow the convention:

1. Read the file's title or first paragraph to derive its actual content
2. Build the new name per the pattern
3. Rename via `mv` (preserves Finder metadata)
4. If there's a dated archive alongside (`session_handoff-2026-04-15.md`), rename it to convention too while you're there

Don't bulk-rename an entire folder unless asked. Rename files you're actively working with.

## See also

- `feedback_client_folder_nomenclature` - the original memory establishing this pattern
- `feedback_client_folder_source_of_truth` - one copy per artifact, in the client's folder
- `feedback_save_transcripts_to_client_folder` - save raw transcripts to `Transcripts/` before summarizing
- `feedback_keep_draft_versions` - preserve in-progress drafts; archive older once a successor lands
