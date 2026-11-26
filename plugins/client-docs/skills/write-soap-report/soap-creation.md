---
name: write-soap-report
description: Turn a session transcript (or session notes) into an XRAY-branded SOAP report .docx in Rachael's consulting voice. SOAP = Subjective / Objective / Assessment / Plan. Use when the user provides a client-session transcript or notes and asks for a SOAP report, session report, session recap, or "write up this session." Triggers on "SOAP report", "SOAP", "session report", "write up the session", "recap this call as a SOAP".
tags:
  - skill
---

# Write a SOAP Report

Convert a consulting-session transcript or notes into a polished, XRAY-branded **SOAP report** `.docx`. SOAP is the chart-note format adapted for client work: **S**ubjective, **O**bjective, **A**ssessment, **P**lan.

These are internal/client session recaps written by Rachael (XRAY) after a working session with a client. The gold-standard examples are the four THFH (Chris Nolan Example) reports; match their structure, specificity, and voice.

## Inputs you need

Each client folder under `~/Claude-Work/CLIENTS/<Client_Folder>/` holds a `Transcripts/` folder (raw session transcripts) and a `SOAP-Reports/` folder (the deliverables). **Always check `Transcripts/` first**, the source may already be filed there. If either folder is missing, create it.

Before writing, make sure you have:
- **The transcript or session notes** (required).
- **Client name** (e.g., "The HOPE for Health (Chris Nolan Example)").
- **Session date** and **duration** (e.g., "March 16, 2026" / "3 hours (async)"). Check the transcript **filename** first, it usually carries the date (`GMT20260527…`, `…5_9_2026`). For duration, read the first and last timestamps; note when the consultant actually joined vs. when the recording started. Ask only if you can't derive it.
- **Session type**: live meeting vs. async work, affects framing (a meeting captures discussion + decisions; async captures work performed).

If date/duration/client aren't in the transcript, ask once, then proceed.

## Workflow

1. **Read the transcript fully.** Identify: what the client needed (the presenting problem), what was actually done or discussed, what it means, and what happens next.
2. **Draft the four sections** following `references/soap-format-and-voice.md` exactly, that file defines what each section contains and Rachael's voice rules. Do not skip it.
3. **Run the draft through the `humanizing` skill** before building. This is a required step, not optional, invoke the `humanizing` skill on the drafted prose so it lands in Rachael's voice (kill em dashes, drop `-ly` adverbs and banned words, first person where she's the actor, warm and direct). Per Rachael's standing note, also apply the other feedback memories alongside it (inclusive terminology: "needs to be fixed" not "needs fixing," "complete" not "clean"; "normalize" not "clean" for data; no throat-clearing). **Keep the SOAP scaffolding intact**: the S/O/A/P headers, the bold list lead-ins, and the ✅/⚠/✋ status markers are document structure, not email-style emphasis, so the humanizing skill's "no headers/no bold" email rules do NOT apply to them.
4. **Write the humanized content as a Python dict** and feed it to the build script (`references/build_soap.py`), which renders the XRAY-branded `.docx`. See "Generating the .docx" below.
5. **Save the deliverable** to the client's SOAP folder, not Downloads: `~/Claude-Work/CLIENTS/<Client_Folder>/SOAP-Reports/`. Also keep a markdown copy alongside it (the examples were drafted in markdown first). And **file the source transcript** in the client's `Transcripts/` folder (clean name, e.g. `<CLIENT>-Transcript-YYYY-MM-DD.ext`) if it isn't already there, don't leave transcripts loose in Downloads.
6. **Sanity-check the output**: confirm 0 em dashes and no banned words in the rendered prose, then tell Rachael the exact output path and offer to open or refine it.

## Subject line + description (required on every SOAP)

Every SOAP report carries two extra fields. They render in a small block under the title meta AND in the .docx's native Word Subject/Description properties.

- **Subject line**: a single pipe-delimited line in this exact order: `Client's name | Rachael Quisel | Client's company | Date | Project`. The last field is the **project** the meeting was about, in one or two words (not the meeting topic). Every client has at least one project; reference it. Example: `Chris Nolan Example | Rachael Quisel | The HOPE for Health | May 9, 2026 | Partner Portal`. (THFH's project is the **Partner Portal**: the Airtable/Fillout/Teachery partner-cohort enrollment system.)
- **Description**: one or two plain sentences on what the session covered. Keep it under 255 characters (Word's Description field caps there; the builder truncates as a safety net).

In the content dict, pass `subject` and `description` keys alongside `client`/`date`/`duration`/`consultant`. Mirror both at the top of the markdown draft.

## The four sections (summary: full rules in the reference)

- **Subjective**: the client's situation/need in their framing. The "presenting problem." Plain, specific, names the real issue.
- **Objective**: what was actually done or covered this session. Factual, structured (numbered work items, bullets, tables). This is the longest section.
- **Assessment**: Rachael's analysis: what it *means*, why it matters, the value-add, the risks/gaps. This is where opinion lives.
- **Plan**: next steps, split into: immediate next steps, upcoming/prioritized build items, and maintenance/client to-dos.

## Generating the .docx

The build script `references/build_soap.py` is the single source of truth for the XRAY brand helpers (Urbanist headings, Figtree body, blue accent rules, branded tables, logo header, footer). It exposes `build(content, out_path)` - you supply a content dict, it renders the `.docx`.

**Don't copy the builder into the client folder.** Instead, write a thin per-session driver in the client's `Code/` folder that imports the shared builder and passes it the content dict. That way a brand or layout fix lives in one place and every client picks it up. The driver pattern:

```python
import os, sys
sys.dont_write_bytecode = True  # keep the shared skill folder free of __pycache__
sys.path.insert(0, os.path.expanduser("~/.claude/skills/write-soap-report/references"))
import build_soap

CONTENT = { "client": ..., "date": ..., "subject": ..., "description": ..., "sections": [...] }
OUT = os.path.join(os.path.dirname(__file__), "..", "SOAP-Reports", "THFH-SOAP-Meeting-YYYY-MM-DD.docx")

if __name__ == "__main__":
    build_soap.build(CONTENT, os.path.abspath(OUT))
```

Name the driver after the session (e.g. `build_soap_meeting_2026_05_27.py`) and run it with `python3` from the `Code/` folder. The dict schema and a worked example live at the top of `build_soap.py` and in `references/soap-format-and-voice.md`.

Requirements: `pip install python-docx` if not present. The XRAY wordmark PNG is auto-located (THFH Code folder / Downloads); the doc still builds without it.

## Voice rules (do not violate)

Pulled from the SOAP example memory and Rachael's standing feedback, full list in the reference:
- Direct, specific, no filler. "Got Teachery talking to Airtable," not "Successfully integrated the Teachery platform."
- Name problems plainly; be honest about client gaps.
- Use arrows for flows: "Wix → Teachery → Airtable → Coach Portal."
- Assessment is where your opinion lives, not just what happened, but what it means.
- Inclusive terminology: "main" not "master," "complete" not "clean," always "needs to be fixed" never "needs fixing."
- XRAY footer tagline is "Workflow Automation That Works", never add "actually." (Older THFH scripts used "That Actually Works", do NOT copy that; use the correct tagline.)

## Related
- `references/soap-format-and-voice.md` - full section definitions, voice rules, content-dict schema.
- `references/build_soap.py` - parameterized XRAY-branded generator.
- `xray-brand` skill, source of truth for brand tokens/logo if anything needs updating.
- The four THFH SOAP examples in `~/Claude-Work/CLIENTS/The_HOPE_for_Health_Teri_Hall/` (`Archive/` markdown, `Code/` generators).
