---
name: client-doc-interface-prompts
version: 1.4.8
description: >-
  Draft or append to the canonical `interface-prompts.md` file for a client build, capturing the Airtable Labs Canvas prompts used to build custom Airtable apps for the client. Canvas builds FULL APPS from natural-language prompts: multi-tab, multi-table, can provision a new base or work against an existing one, with per-component feature specs, aesthetic direction, and data-behavior rules. Not for Omni interface pages. Use when Rachael says "capture the canvas prompt", "add canvas prompt to interface-prompts.md", "document the [X] canvas app", "canvas prompt for [app]", "canvas app for [client]", "log the canvas build", or when a build ships a Canvas app worth documenting. Produces one dated section per Canvas app with the exact prompt, intent, aesthetic direction, iteration notes, and any errors that got fed back in.
---

# client-doc-interface-prompts: canonical `interface-prompts.md` for Canvas prompts

## Purpose in plain English

This skill helps you save the exact requests used to build a client's Airtable app, together with their purpose and revisions.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Produces the `interface-prompts.md` file for the client's repo `XRAY-INC/<CLIENT>` at `projects/<build>/`. Captures **Airtable Labs Canvas** prompts. Writes local Markdown only; push is a separate step.

The interview is about five questions per app, covering the five prompt sections (frame, features, data model, aesthetic, behavior). Canvas is distinct from Omni, which builds standard interface pages of grid, filter, group, and form. This skill is not for those Omni pages.

## What Canvas is

Canvas is Airtable Labs' AI-generated app builder. A single Canvas prompt produces a full custom Airtable app: multi-tab, multi-table, with a data model, UI, interactions, aesthetic direction, and behavior rules. It's not just visualizations; it builds kanbans, dashboards, forms with modals, autosave, drag-and-drop, filters, dark/light mode, and more. It can either provision a NEW base with the schema it needs, or build against an EXISTING base you point it at.

**What Canvas can produce (from real prompts):**
- Multi-tab apps (kanban tab + feedback tab + dashboard tab)
- Full data models (tables + linked records + statuses + priorities + attachments)
- Custom visualizations (3D viewers, heatmaps, network diagrams, maps, infinite canvases)
- App-level features: create/edit modals, autosave, drag-and-drop, filters, delete confirmations, markdown rendering, loading/error states, refresh behavior
- Aesthetic direction: fonts, borders, buttons, icons, color schemes, dark/light mode with OS auto-detect, animation

**Canvas vs Omni:**

| | Omni | Canvas |
|---|---|---|
| What it builds | Standard interface pages (grid, filter, group, form) on an existing base | Full bespoke apps, or bespoke elements, with a full data model + UI + behavior |
| Base | Existing only | New OR existing |
| Multi-tab | Yes (each page is a tab) | Yes (real tabs in a bespoke app UI) |
| Aesthetic control | Airtable's default styling | Full control: fonts, borders, buttons, colors, dark/light mode |
| Multi-table per prompt | Yes | Yes, including linked records + rollups in one prompt |
| Generation time | Seconds | ~5 minutes; can error |
| Iteration | Rewrite the prompt | Adjust one section, copy errors back |

Canvas is the default interface builder, but not every client uses it (Example Client staff screens are built in Zite, for example). Check which tool the client uses before drafting. For a Zite build, record the Zite prompts in the same file format, with the tool named in the entry header, and use the `zite-prompt` skill to write them. The Canvas-vs-Omni comparison above is orientation only, it explains what Canvas is by contrast to Airtable's other interface builder.

Note: Canvas is a live Airtable Labs product; its conventions are still evolving. If a prompt structure below stops matching what Canvas expects, check current Airtable Labs Canvas docs and update this skill.

## The five sections of a good Canvas prompt

Every Canvas prompt worth capturing follows this order. Reference from a real prompt Rachael wrote ("Pencil"):

1. **Frame:** app name + tabs at a glance. Example: "Build a project management app called 'Pencil' with two tabs: Tasks and Feedback."
2. **Per-tab feature spec:** dense comma-separated features per tab. Example: "Tasks is a kanban board for Open, Planning, In Progress, and Done, with drag-and-drop status changes, category/assignee/milestone filters, task cards, create/edit modals, autosave, attachments, milestone creation, and delete confirmation."
3. **Data model:** new base or existing? Which tables? Linked records? Field types? Example: "For the sample data: create a new Airtable base with tasks, team members, milestones, and user feedback. Include linked records, statuses, priorities, GitHub issue URLs, tags, AI summaries, and structured suggestions."
4. **Aesthetic direction:** typography, borders, buttons, icons, color scheme, dark/light mode, animation. Example: "Use a terminal/monospace brutalist aesthetic: IBM Plex Mono only, dashed borders, square corners, bracketed ghost buttons like [close], ASCII status icons, and no radius. Support light/dark mode with OS auto-detect, manual toggle, and localStorage persistence."
5. **UI behavior rules:** what's editable vs read-only, loading/error states, refresh, transitions. Example: "Keep the UI Airtable-driven: editable kanban tasks, read-only AI feedback fields, markdown summaries, loading/error states, shared modal transitions, and automatic feedback refresh."

Interview questions match these five sections exactly.

## Where the output lands

`~/Claude-Work/CLIENTS/<CLIENT_FOLDER>/Documents/interface-prompts/<build>/interface-prompts.md`

Find the client repo name using the rule in the `client-docs` skill.

## Reference

Read `references/example-interface-prompts.md` before drafting. It shows a finished `interface-prompts.md` for a made-up client. Match its format and level of detail.

## Drafting from sources (no interview)

When Rachael asks to draft from transcripts or discovery material, or isn't available to answer questions, skip the interview questions: read the sources, answer each question from them, and write `> TODO: <specific question>` inline wherever the sources don't answer it. Never invent facts to fill a gap. Debrief summaries written by AI can be wrong (a decision reversed the next day, for example): check every claim against the transcript itself before using it.

## Workflow: interview-driven, ~5 questions per Canvas app

### Step 1: Detect client and build

Mine the current context for client + build. If either is unclear, ask ONE question that pins both.

### Step 2: Ask the 5 questions

Ask in one message, numbered. Match the five sections. If Rachael already ran the Canvas prompt and just wants to log it, skip to Step 4 and paste her prompt into the template directly.

1. **Frame:** what's the app, and what tabs does it have? One line for the app (name + one-line intent), then a bullet per tab. Even a single-element Canvas prompt has a frame: name it and describe the one thing.
2. **Per-tab features:** for each tab, what does it DO? Dense feature list per tab, verbs first. "drag-and-drop status changes", "create/edit modals", "autosave", "markdown previews", "detail modals", "add-to-tasks action". Include interactions, states, and any conditional UI.
3. **Data model:** new base or existing? If new: which tables, which fields, which linked records, what statuses/priorities/tags/attachments? If existing: name the base + tables + relevant fields by name AND ID.
4. **Aesthetic direction:** what does it look and feel like? Font family, border style (dashed/solid/none), corner radius, button style (solid/ghost/bracketed), icon style, color scheme (specific colors for light + dark), dark/light mode handling (auto-detect? manual toggle? persistence?), animation details (offset shadow press, transitions).
5. **Behavior rules:** what's editable, what's read-only, what refreshes? Which fields are user-editable vs read-only (AI-generated ones usually read-only). Loading/error states. Auto-refresh behavior. Modal transitions. Anything the UI does automatically without the user asking.

Also capture: **any errors from prior Canvas attempts?** Paste them verbatim. Canvas's iteration pattern is "copy the error into the next prompt so the model can fix it." Skip if first attempt.

### Step 3: Compose the Canvas prompt

Assemble the answers in section order: frame, per-tab features, data model, aesthetic, behavior. Rules:

- **Be descriptive.** Spell out exactly what the app should do. Vague prompts produce vague apps.
- **Iterate in small steps.** Once a version is generated, adjust ONE section at a time on the next pass. Don't rewrite the whole prompt.
- **Copy errors back in.** If Canvas errors, paste the error text into the next iteration.
- **Name tables by name AND ID** when working against an existing base.
- **State the interaction model explicitly.** Read-only is a valid choice; say so.
- **Density is fine.** A single sentence can list 8 comma-separated features per tab.

Present the composed prompt to Rachael for review BEFORE she pastes it into Canvas. Ask if she wants to run it or edit first.

### Step 4: Read the existing file (if any), then append

- If `interface-prompts.md` exists, read it. Preserve everything above. Append the new app at the BOTTOM (append-mostly, dated).
- If it doesn't exist, create it with the header block first.

Never rewrite past entries. If a prior Canvas app got rebuilt, ADD a new dated entry and note "Supersedes: <earlier app title> (YYYY-MM-DD)" in the header.

### Step 5: Write the entry

File header (only on first creation):

```markdown
# Interface Prompts: <Build Name>

**Client:** <Client full name>
**Build:** <build name>

Canvas prompts used to build custom Airtable apps for this build. One section per app, newest at the bottom. See `client-doc-interface-prompts` skill for how these get drafted.

---
```

Each app uses this format:

````markdown
## <YYYY-MM-DD>: <App title>

**Base:** <New | Existing: base name (appXXXXXXX)>
**Tabs:** <comma-separated tab names, or "single element" if no tabs>
**Status:** <Draft | Generated | Iterating | Live | Superseded>

### Intent
<One paragraph. What this app does for the client and who uses it.>

### Data model
<For new base: tables + linked records + key fields. For existing: tables the app reads/writes, plus any field additions the prompt requires.>

### Aesthetic
<One paragraph. Font, borders, buttons, colors, dark/light mode. Match the language of the prompt.>

### Behavior rules
<Bullet or paragraph: what's editable, what's read-only, refresh/loading/error states.>

### Prompt (as pasted into Canvas)
```
<the exact prompt string, verbatim>
```

### Iteration notes
- <YYYY-MM-DD>: <what changed, why>
- <YYYY-MM-DD>: <error text pasted back in, what got fixed>

### Known limits and scope calls
<Anything Canvas couldn't do, or that required a scope call. e.g., "Needed to add a rollup on Tasks so the kanban card could show milestone name inline.">

---
````

Rules for the entry:
- Date is today, absolute.
- App title is one line and describes what the client SEES, not the tech.
- Prompt block is VERBATIM. Never paraphrase. Future-Rachael needs to regenerate this if the model updates.
- Iteration notes are dated; append, never rewrite.
- Plain English in Intent, Aesthetic, and Behavior rules: ordinary words a client can follow, with no jargon and no record IDs in those sections.
- Never use "clean", "heal", "drift", "master", or a metaphor. Name the literal thing (the field, the record, or the step).

### Step 6: Write the file and print the path

1. Create the directory if needed.
2. Write the file (create or append).
3. Print the path and a one-line summary. Example: "Appended: Pencil PM app, 2 tabs, new base with 4 tables. Status: Draft. Prompt ready to paste into Canvas."

### Step 7: Do NOT push

Push is a separate step. Stop after the local write.

## Voice

Rachael's voice per `~/Claude-Work/ABOUT-ME/my-voice.md`. Direct, plain English, no filler, no metaphors, no em-dashes in prose (use commas, semicolons, colons, parens, or two sentences). The Intent + Aesthetic paragraphs are client-readable; the Prompt block is technical (fine to include field names, color values, feature-verb density).

## When this skill is the wrong answer

- Building the vision or scope of the build → `client-doc-vision-and-scope`
- Logging a decision about which app to build → `client-doc-decisions`
- Recording that a Canvas app shipped → `client-doc-changelog`
