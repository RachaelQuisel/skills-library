---
name: automation-explainer-local
version: 1.4.6
description: Write and save a short, bullet-format education document that explains one automation in plain English through its trigger, inputs, complete steps, and outputs. Use when Rachael invokes "/automation-explainer-local" or asks for a "short little education document," "auto doc," or "quick automation explanation." Also update the existing project documentation and running updates and questions that directly cover the automation. Use `how-it-works-doc-writer-local` for the fixed 11-section handoff document and `explain-code` for a code-level walkthrough.
---

# Auto

## Purpose in plain English

This skill helps you write a short explanation of what starts an automation, what it uses, what happens, and what it produces.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Write a short document that explains one automation without requiring the reader to open its code or configuration.

## Find the facts

1. Identify the automation and project from the request, current work, or working directory.
2. Read the code, configuration, or live definition that controls the automation.
3. Read existing project documents that directly describe the automation.
4. Confirm the trigger, inputs, complete steps, conditions, stopping points, failure paths, and outputs.
5. Label a required fact as unknown when the source does not provide it. Do not guess. Ask one direct question only when the missing fact prevents an accurate document.

## Write the document

Use these sections and no others:

- **Trigger:** State every event and condition that must be true before the automation starts.
- **Inputs:** List every piece of information the automation reads or receives. State what each input is used for when it is not clear.
- **What happens:** Use numbered bullets to list every action in order. State each condition before its result. Include alternate routes, stopping points, and failure actions.
- **Outputs:** List everything the automation creates, changes, sends, or records. Name the destination for each output.

Follow these writing rules:

- Use common words and complete sentences. Keep one idea in each sentence.
- Do not use jargon, unexplained shortened terms, metaphors, em dashes, throat-clearing, or sentence fragments.
- Preserve exact product, table, field, automation, and status names. Explain an unavoidable technical term at first use.
- Write "needs to be fixed," not "needs fixing."
- Keep each fact in one place. Do not repeat the trigger or outputs in the steps unless the sequence would be unclear without them.
- Do not add an overview, a boundaries section, or a closing summary.
- Keep the document to about one page when the automation is simple. Use more space only when every step needs it.

## Save and update

- Return a draft without changing files when the user asks for a draft only.
- Find the project folder from the current work. Do not assume one fixed home-directory path.
- Follow the project's existing naming convention. If none exists, use `<CLIENT>-HowItWorks-YYYY-MM-DD-<automation-name>.md`.
- Save the document beside the automation's code when that folder exists. Otherwise, save it in the existing `Project Documentation` folder.
- Update the existing `running-updates-and-questions.md` with today's date, what changed, the current status, and any question the client still needs to answer. State that the automation went live only when the source proves it. Do not invent a question.
- Update another project document only when it directly describes this automation and is now inaccurate or incomplete.
- Preserve unrelated content and the existing structure of every file. Report a missing file instead of guessing where to create it.
- Apply the same writing rules to every project update.
- Report the full path to each file created or updated. Reveal a file in Finder only when the user asks.
