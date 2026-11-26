# SOAP Format & Voice

Full definitions of each section, Rachael's voice rules, and the content-dict schema the build script expects.

## What a SOAP report is

A post-session recap of XRAY consulting work for a client. Borrowed from the clinical SOAP note (Subjective / Objective / Assessment / Plan) and adapted to workflow-automation consulting. One report per working session (live meeting or async work block). Written by Rachael; audience is the client + XRAY's own record.

## The four sections

### Subjective: the client's situation in their framing
The presenting problem. What the client needed, why, and the state of things going in. Written from the client's perspective but in Rachael's plain voice. One to two tight paragraphs.
- Example: "Teri's Complete Program Flow document, the comprehensive reference for how the THFH Portal Airtable base works, was out of date. Several fields documented didn't actually exist in the live base... Teri needed the document corrected to reflect reality and professionally branded."
- Name the real problem. Don't soften it into vague consultant-speak.

### Objective: what was actually done / covered
The factual record of the session. This is the **longest** section. Structure it:
- Numbered work items (`## 1. Full Airtable Base Schema Audit`, `## 2. ...`), each a discrete thing done or discussed.
- Under each, a short framing sentence, then bullets / bold-lead bullets / tables for specifics.
- Use **bold lead-ins** on bullets to call out the subject ("**Contact Status** on Students table, doesn't exist").
- Use **tables** for deliverables produced (File | Location), schemas, before/after.
- Be technically specific: real field names, real base IDs, real counts. Specificity is the whole point.
- For a **live meeting**, Objective captures topics discussed + decisions reached. For **async work**, it captures work performed + artifacts produced.
- End Objective with a **Deliverables Produced** table when artifacts were created.

### Assessment: Rachael's analysis (where opinion lives)
Not a recap, the *meaning*. What the work/discussion implies, why it matters, what the value-adds are beyond the obvious, and what risks or gaps remain. Usually a framing sentence + a numbered list of insights, each with a bold lead-in.
- Example insights: "Honesty about build status, By clearly marking what's built vs. planned... prevents confusion where someone expects an automation to fire and nothing happens."
- Be honest about client gaps and strategic ambiguity ("Her unclear product definition creates strategic ambiguity").

### Plan: what happens next
Split into labeled subsections (use `## H2` for each):
- **Immediate Next Steps**: numbered, near-term, often client validation + fixes.
- **Upcoming Build Items (prioritized)**: numbered, the build backlog with brief rationale per item.
- **Document/System Maintenance** or **Client To-Dos**: bullets. Separate what XRAY does next from what the client must do.

## Voice rules

From the SOAP example memory + Rachael's standing feedback memories. Apply all of them:
- **Direct, specific, no filler.** "Got Teachery talking to Airtable," not "Successfully integrated the Teachery platform."
- **Name the problem plainly.** "She'd owned ActiveCampaign for four years but had zero automations."
- **Honest about client gaps.** Assessment can say the hard thing.
- **Arrows for flows.** "Wix → Teachery → Airtable → Coach Portal."
- **Assessment = opinion.** Every other section is fact; Assessment is judgment.
- **Inclusive terminology:** "main" not "master"; "complete" not "clean"; always "needs to be fixed," never "needs fixing."
- **Client-facing data language:** prefer "normalize/normalization" over "clean/cleaning."
- **No throat-clearing**, no neutral hedging commentary.
- **Footer tagline is "Workflow Automation That Works"**: never "actually." (Old THFH scripts wrote "That Actually Works"; that's wrong, do not reproduce it.)
- If the humanizing skill is run over the draft, apply all feedback memories (terminology, grammar) too.

## Content-dict schema (for build_soap.py)

The build script renders this dict. Blocks are rendered in order. Block types:

```python
CONTENT = {
    "client": "The HOPE for Health (Chris Nolan Example)",   # subtitle on title page
    "date": "March 16, 2026",
    "duration": "3 hours (async)",
    "consultant": "Rachael Quisel, XRAY",
    # Required on every SOAP. Subject order: Client | Rachael Quisel | Company | Date | Project (1-2 words).
    # description <=255 chars (Word Description field cap; builder truncates as a safety net).
    "subject": "Chris Nolan Example | Rachael Quisel | The HOPE for Health | March 16, 2026 | Partner Portal",
    "description": "Async session: schema audit, program-flow doc correction, and XRAY branding.",
    "sections": [
        {"heading": "Subjective", "blocks": [
            {"body": "Teri's Complete Program Flow document ..."},
        ]},
        {"heading": "Objective", "blocks": [
            {"h2": "1. Full Airtable Base Schema Audit"},
            {"body": "Conducted a complete API-level audit ..."},
            {"bold_body": "Fields that don't exist (removed from document):"},
            {"bullet": "on Students table - doesn't exist", "bold": "Contact Status "},
            {"bullet": "checkbox on Volunteers table - doesn't exist", "bold": "Welcome Email Sent? "},
            {"h2": "Deliverables Produced"},
            {"table": {"headers": ["File", "Location"],
                       "rows": [["THFH-Program-Flow.docx", "~/Claude-Work/CLIENTS/.../soap-reports/"]]}},
        ]},
        {"heading": "Assessment", "blocks": [
            {"body": "The document is now a single-source-of-truth reference. The key value adds:"},
            {"numbered": "- By clearly marking built vs. planned, gaps are immediately visible.", "bold": "Honesty about build status "},
        ]},
        {"heading": "Plan", "blocks": [
            {"h2": "Immediate Next Steps"},
            {"numbered": "for review - validate the status indicators.", "bold": "Share updated document with Teri "},
            {"h2": "Upcoming Build Items (prioritized)"},
            {"numbered": "- Make.com scenario triggered by the checkbox.", "bold": "Zoom meeting scheduling automation "},
            {"h2": "Document Maintenance"},
            {"bullet": "Update the .docx whenever a new automation is built."},
        ]},
    ],
}
```

Block keys:
- `{"body": "..."}` - body paragraph.
- `{"bold_body": "..."}` - bold lead-in paragraph (no trailing normal text), used as a mini sub-label.
- `{"bullet": "...", "bold": "optional prefix "}` - bullet; `bold` prefix is rendered Gray-900 bold, the rest Gray-600.
- `{"numbered": "...", "bold": "optional prefix "}` - numbered list item, same bold-prefix behavior.
- `{"h2": "..."}` / `{"h3": "..."}` - subheadings inside a section.
- `{"table": {"headers": [...], "rows": [[...], ...]}}` - branded table.

Top-level `sections` each render an H1 (with the blue accent rule). Keep the four canonical headings: Subjective, Objective, Assessment, Plan.
