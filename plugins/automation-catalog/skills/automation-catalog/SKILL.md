---
name: automation-catalog
version: 1.0.5
description: Create each automation’s name, plain-English guide, run location, and tags. Find and document automations across accessible businesses, client projects, personal projects, repositories and connected services. Use to find all automations, refresh an automation catalog, apply /auto to each workflow, add categories and tags, or update existing guides and appropriate Slack channels. This does not authorize running or changing the discovered automations.
---

# Automation Metadata Maker

## Purpose in plain English

This skill helps you give each automation a clear name, explanation, run location, and useful labels.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


## Scope and permissions

1. Read the request and prior authorization. Default “all automations” to all accessible accounts and projects, including personal workflows when in scope. Do not limit discovery to a previously discussed business.
2. Separate permission to search, save documents, and post messages. Creating this plugin does not authorize a new business-wide publication. A request to document and post does authorize that work without another routine confirmation.
3. Inventory connected accounts and business identities. Prefer service connectors. Check the plugin directory before declaring a needed integration unavailable. Follow the host's approved fallback rules. Never bypass denied access through private endpoints or alternate credentials.
4. Find existing project instructions, inventories, running updates and document homes. Reuse the right repository. Read [discovery.md](references/discovery.md) and [publication.md](references/publication.md).

## Discover and reconcile

1. Search native schedules and workflow definitions, then repositories, project documents and approved messages. Use business names and workflow terms. Paginate relevant lists. Follow references to scripts, accounts and deployments.
2. Keep a coverage ledger for each source: account, business, resource, timestamp, pages checked, limits and outcome. Distinguish checked, empty, denied, unavailable, truncated and not checked. A denied or truncated result is not an empty inventory.
3. Identify workflows by business ID, provider and stable workflow ID. If no provider ID exists, use repository plus entry-point path. Preserve identity across title changes. Record aliases and related helpers. Do not count every helper script as a separate automation.
4. Match candidates against existing inventory entries, guide paths and Slack message references. Resolve duplicates using source identities. Keep uncertain matches flagged. Do not merge workflows across businesses because names match.
5. Read controlling code, configuration or live definitions and directly related documents. Preserve source links and immutable revisions when available. Plans, open pull requests, copied code and old messages are not proof of the current running version.
6. Record implementation evidence, observed run evidence and cloud evidence separately. Use clear status labels: code reviewed, enabled schedule verified, past output observed, manual, planned, older description, disabled, or unknown. Past success is not current health. An enabled task is not proof of future delivery.
7. Identify every trigger, input, action, condition, stopping point, retry rule and output. Mark missing facts unknown. Do not invent steps to fill gaps.

## Write and classify

1. Apply the current installed `/auto` skill to each distinct workflow. Load its instructions once. Apply `/voice-align` or `/plain-english-editor`. If unavailable, use the writing contract below and disclose the missing dependency. Never claim a skill ran when it did not.
2. Use only four body sections: Trigger, Inputs, What happens, Outputs. Number the steps. State each condition before its result. Use short sentences and everyday words. Explain unavoidable technical terms. No em dashes, filler or unexplained shortened terms.
3. Preserve exact names, field labels, commands, dates and necessary contact details. Do not simplify away failure paths or approval steps. Exclude tokens, passwords and guest access codes.
4. Above the body, add category, workflow type, source tools, status, run location and search tags. Use the project's existing vocabulary. Read [classification.md](references/classification.md). A tool label is not proof of a live connection.
5. Update the existing guide rather than adding a duplicate. Follow the project's naming convention. Save beside the code when appropriate, otherwise in the existing documentation folder. If the expected folder is missing, report the gap rather than guessing.
6. Check older guides, indexes and directly related README sections for contradictions. Correct inaccurate current instructions while preserving dated history. Append today's entry to the existing running-updates-and-questions.md. Preserve unrelated content and operating code.
7. Group the catalog by business and category. Count evidence levels separately so plans do not inflate the live automation count. Report “all found in checked sources,” not unsupported exhaustive coverage.

## Save and share

1. Read current file revisions or Git head before writes. Follow project branch rules. Prepare a documentation branch and draft pull request where required. Reconcile concurrent changes without overwriting them. Do not merge or deploy merely to document.
2. Save a private publication ledger per business: workflow identity, document path, content hash, repository revision, destination IDs, message ID, verified result and errors. Store no credentials. A combined private register needs explicit approval.
3. Before Slack writes, verify authorization, business ownership, audience, workspace and exact channel ID. Identical channel names are not interchangeable. Searching all projects never means posting all clients' information in La Maison Slack.
4. Use an existing approved automation channel. A central private channel needs explicit permission for the included businesses. Hold only ambiguous publications and continue other work. Ask one focused question when a missing destination prevents sending.
5. Edit an existing owned message when content changes. Skip identical content. Reuse the index thread. If editing is impossible, use an authorized linked replacement. Do not duplicate all guides on every run.
6. Respect connector message limits. Prefer a concise guide and durable link. Split only at clear section boundaries if needed. Keep Slack and saved documents consistent.
7. Require successful receipts before recording completion. If a request times out, read the destination before retrying. Read back the index and guides. Save partial progress so retries handle only unfinished work.
8. Report found, documented, saved and posted counts separately. Link results and list held items or access gaps. Report failures in the current run and an approved failure destination when available. Do not fail silently.

## Local helper

Use `python scripts/catalog.py INPUT.json --output OUTPUT_DIRECTORY` to check a prepared inventory, render guides and build a publication plan. Read [data-contract.md](references/data-contract.md) first. The helper makes no network calls and sends no messages. It refuses an existing output directory. Source truth, authority and destination identity still require independent checks through connectors.

## Scheduled use

When recurring work is requested, follow [scheduled-runs.md](references/scheduled-runs.md). Keep personal account settings outside this package.

## Finish

Check factual accuracy, plain English, stable identities, business boundaries, links and receipts. Do not enable, run, repair, purchase through or reschedule discovered automations. The plugin is on demand. If recurring work is separately requested, use a supported cloud scheduler and verify the saved scope and routes before claiming computer-independent operation.
