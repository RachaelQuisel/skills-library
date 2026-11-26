---
name: build-page-publisher-local
version: 1.4.7
description: Publish a shareable Artifact web page documenting what was built in this session, how it functions, what triggers it, what breaks it, what the gates are, what a client needs to know. PM-quality client education, rendered as a clean shareable link the client can open in a browser. Use when Rachael types "/artifact," when she says "make me an artifact of what we built," "publish an education page," "shareable version of the HOW-IT-WORKS doc," "give the client a link they can read," or right after a substantial build ships and she wants a visual, forwardable web-page version instead of a markdown file.
---

# artifact

## Purpose in plain English

This skill helps you turn an explanation of completed work into a web page that a client can read and share.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Build and publish an Artifact (via the Artifact tool) that documents what was built in this session. The Artifact is a shareable web page the client can open in a browser without opening any files, code, or Airtable.

## Rules

- Load the `artifact-design` skill BEFORE writing the page. Do not skip this, that skill sets how much design investment this particular request warrants.
- Plain English throughout. No jargon that is not defined inline. No metaphors. No "clean," "heal," "drift," "sync" (as a verb standing in for the real action), "smoke," "master," or any word standing in for the literal action.
- PM-quality: tight headings, scannable tables, every claim has a concrete example, plain English first then technical detail.
- Never "needs fixing." Use "needs to be fixed."
- Refer to fields, tables, and records by their human-readable name in the page body. If a field ID matters for a developer viewing later, put it in parens.
- Artifact starts private. Rachael decides when and where the link goes. Do not auto-share.
- Do not fabricate content. If a section has no real answer for what was built, write "Not applicable for this build, [one plain-English sentence naming why]." Do not fill it with plausible-sounding text.

## Sections the page must cover

Same 11-section structure as `/education`, rendered as a clean HTML page instead of a markdown file:

1. **Quick Read (for [Operator Name])**: the daily operator's one page. What to check, what to look at, what success and failure look like. Auto-detect the operator name from the client folder (Example Nonprofit → Janine, Example Agency → Jessica, The HOPE for Health → Teri, AY Media → Casandra). Only ask if the client has more than one plausible operator.
2. **What this does**: one paragraph for the owner.
3. **How it functions**: the end-to-end flow in 3 to 6 numbered steps.
4. **What triggers things**: every condition that starts the automation.
5. **What breaks things**: every hard error and every misconfiguration that stops the automation dead.
6. **The conditions**: every "if this then that" in the automation, in plain English.
7. **The gates**: every safety check the automation runs before it does the thing. Split into bypassable gates and hard guards.
8. **The pipeline**: a diagram (ASCII fenced in `<pre>`, or an inline SVG) showing the actual named systems in the flow. For example, "Airtable → Zapier → QuickBooks Online → writeback to Airtable" or "Fillout → Airtable → Gmail." Never write a generic title like "Source → Middleware → Destination." Always name the real systems.
9. **Common errors and what they mean**: the translation guide, as a table. Columns: `Message the user sees`, `What's wrong`, `How to fix`.
10. **For a senior product manager at Google to read**: design decisions and the rationale, how the system fails safely, audit trail (every place a run leaves a trace), versioning and rollback, release notes drafted verbatim so Rachael can forward without editing.
11. **What a client would need to know**: the 5 to 8 bullets a non-technical client absolutely has to walk away with.

If any of the 11 sections genuinely does not apply, keep the header and write "Not applicable for this build, [why in one plain-English sentence]." Do not omit the header.

## Design notes for the Artifact itself

- Responsive layout. Wide tables scroll inside their own container so the page body never scrolls horizontally.
- Theme-aware, style for both light and dark unless the design deliberately commits to one.
- Favicon: an emoji that names the automation's purpose (a checkbox for a push automation, a paper airplane for an email automation, a clipboard for an intake form, and so on). Keep it stable across redeploys of the same automation. Only pick a new emoji on a hard pivot in what the automation is about.
- Title: `How [Automation Name] Works - [Client Name]`.
- Description (gallery subtitle): one sentence naming what the automation does for the client.

## Before publishing

- Ask Rachael what to name the automation on the page if it is not obvious from the session.
- Ask which client the page is for if there is any ambiguity.
- If the session touched more than one automation, ask which one this Artifact is for. One Artifact per automation.

## After publishing

- Print the Artifact URL.
- One-line summary: which client, which automation, and the URL.
- Offer to draft a Slack or email message to the daily operator that includes the link. Something like: "Want me to draft a message to [Operator Name] that includes this link? I'll show it here first, you decide whether to send."
- If Rachael says yes, draft the message in her voice (per [[rachael-work-voice]] and the humanizing skill) and print it in chat. Do NOT send it automatically. She copies and sends when she is ready.
- If Rachael says no, stop. Do NOT auto-send the link anywhere.
