---
name: zite-prompt
version: 1.0.5
description: "Create lean, paste-ready prompts for Zite. Use whenever the user asks what to tell Zite, asks for a Zite prompt, wants a Zite prompt shortened or corrected, or is stepping through a Zite build by pasting prompts into Zite. Keep expensive Zite usage focused on implementation: resolve research, codebase questions, schema details, conflicts, and known IDs outside Zite first, and ask the user when a genuine product decision or missing fact remains."
---

# Zite Prompt

## Purpose in plain English

This skill helps you write a focused request for the next Zite build step using the information already confirmed.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Create the smallest prompt that lets Zite complete the next implementation step.

Zite prompts cost money, so do the thinking outside Zite and spend Zite context only on work Zite must perform.

## Before writing the prompt

1. Use decisions already made in the conversation.
2. Resolve implementation facts directly from the available source, such as GitHub, Airtable, Twilio, project files, or other connected tools.
3. Resolve conflicting documentation yourself when source code or live data answers it.
4. If a needed fact is still unknown, ask the user a short question instead of asking Zite to research it.
5. Use Zite for discovery only when the needed information exists only inside Zite and is required for the next build step.
6. If the user asked for a prompt, do not execute the prompt in Zite unless they separately ask you to execute it.

## Put only necessary build context in the prompt

Include:

- The exact thing to build or change now.
- The specific connected source, repository, table, app, or integration Zite must use.
- Immutable IDs when they are already known and relevant.
- The exact behavior or visual reference needed for this step.
- Constraints that prevent an unwanted change.
- Deferred work only when Zite needs to know not to wire it yet.

Reuse information already saved in the Zite workspace. Do not restate project history, integration setup, or prior decisions unless the current implementation step depends on them.

## Write the prompt as a brief

Zite does most of the hands-on building. The prompt's job is to brief it well, and the user's job is to check its work. A good brief has four parts:

1. **What was seen or is wanted**, with the page name. Tell the user to attach a screenshot when one exists.
2. **Who it's for and on what device**: members, Seekers, admins, staff, on phone or desktop.
3. **What "done" looks like**, in one sentence.
4. **Limits**: "just this page", "don't publish", "talk first, don't change anything yet".

Example:

> On the Activities page on my phone, the Watch Back banner overlaps the heading. Fix just that, don't publish, and log it in the fix log.

Add one of these phrases when the step calls for it:

- **"Investigate first and tell me the cause before changing anything."** Use for a bug whose cause lives only inside the running Zite app. If GitHub, Airtable, or another connected source can answer it, find the cause there first.
- **"Check the live data, not just the code."** Use when the problem depends on real records, such as missing rows, wrong values, or a filter that hides things.
- **"Mock it up first."** Use for any visible redesign, so the user approves the layout before Zite wires data.
- **"Write it up in the project docs."** Use when the change should be recorded, such as a fix log entry or a decision note.

For a non-technical user, these four parts and four phrases are enough to write a usable prompt without code knowledge.

## Keep research out of the Zite prompt

Do not ask Zite to:

- Explain what the current code does when GitHub can answer it.
- Compare old and new implementations.
- Find conflicts that can be resolved from source.
- Decide product behavior for the user.
- Produce a planning report before a straightforward build step.
- Reinspect verified integrations.
- Repeat project history.
- Explain work the user did not ask to have explained.
- Perform unrelated cleanup, refactoring, schema changes, or architecture work.

Do not add speculative requirements.

## Prefer one narrow build step

When the user wants to see or test an interface, build the visible interface first and defer backend wiring that is not needed to review the screen.

Default to one compact prompt, usually under 250 words. Use more only when exact identifiers or tightly coupled requirements are necessary for a safe implementation.

Do not split one simple action into several Zite prompts.

## Output

If the next step is clear, return **one paste-ready Zite prompt and nothing else**.

If a genuine user decision or missing fact blocks the prompt, ask **one concise question instead**. Do not draft a speculative Zite prompt around the uncertainty.

## Prompt pattern

> Build [specific thing].
>
> Use [connected source/integration].
>
> Relevant IDs:
> - [object]: `ID`
> - [field]: `ID`
>
> Match [specific reference or behavior].
>
> Build [exact visible or functional behavior].
>
> For this step, focus on [scope]. Do not [deferred work].

## Examples for context

Read [examples.md](references/examples.md) when choosing scope, shortening a prompt, resolving conflicting context, or deciding whether a question is needed. Treat examples as context, not project defaults. Never reuse their IDs or business rules in another project. Verify relevance from the current conversation or connected source.

## Final check

Before returning the prompt, verify:

- Every sentence is needed for this build step.
- The prompt names the page, the audience and device, one-sentence "done", and the limits.
- Research that could be done outside Zite has already been done.
- Known IDs are used instead of relying only on display names.
- Saved Zite context is not repeated unnecessarily.
- Deferred work is not mixed into the current step.
- The user can paste the prompt into Zite without editing.
