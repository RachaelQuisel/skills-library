# Client Docs

Twenty-six skills for documenting an XRAY client build. Each client has its own GitHub repo (`XRAY-INC/<CLIENT>`); docs go in `projects/<build>/`.

## What a full run outputs

A complete documentation pass for one build produces these 10 documents, drafted locally under `~/Claude-Work/CLIENTS/<CLIENT_FOLDER>/Documents/<doc-type>/<build>/` and pushed to the client repo through `client-doc-push`:

| # | Document | Written by |
|---|---|---|
| 1 | `prd.md` (the product requirements document, five-signals format) | `five-signals-prd`, with `prd-frame-estimate` for the opening block |
| 2 | `vision-and-scope.md` | `client-doc-vision-and-scope` |
| 3 | `build-plan.md` | `client-doc-build-plan` (the tasks.xray.tech API first; drafted from meeting transcripts, verified against the recordings, when the project has no outcomes or tasks yet) |
| 4 | `kpi-report.md` | `kpi-report` |
| 5 | `user-stories.md` | `client-doc-user-stories` |
| 6 | `interface-prompts.md` (only once a Canvas prompt has been run) | `client-doc-interface-prompts` |
| 7 | `decisions.md` | `client-doc-decisions` |
| 8 | `changelog.md` (only once something has shipped) | `client-doc-changelog` |
| 9 | `workflow-diagram.html`, published as a shareable web page | `client-doc-workflow-diagram` |
| 10 | `workflow-diagram.mmd`, the Mermaid source that imports into XR Workspace Blueprint | `client-doc-workflow-diagram` |

## The canonical docs

| Skill | What it does |
|---|---|
| `client-docs` | Keeps the 8 canonical docs for a build current and says which skill writes each one. |
| `client-doc-vision-and-scope` | Writes `vision-and-scope.md`: problem, vision, in scope, out of scope. |
| `client-doc-user-stories` | Writes `user-stories.md`, one section per persona. |
| `client-doc-interface-prompts` | Records the Airtable Canvas prompts used to build the client's apps. |
| `client-doc-decisions` | Adds a dated decision to `decisions.md`. |
| `client-doc-changelog` | Adds a dated entry to `changelog.md` for what shipped. |
| `client-doc-workflow-diagram` | Draws the client's products and deliverables as a styled Mermaid diagram from discovery and the canonical docs, and publishes it as a shareable web page. The same source imports into XR Workspace Blueprint. |
| `client-doc-push` | Pushes the drafted docs to the client's GitHub repo, one commit per file, after you say "push it". |
| `kpi-report` | Turns a discovery transcript into an internal list of KPIs to track for a client. Writes `kpi-report.md`. |
| `five-signals-prd` | Writes `prd.md` in the five-signals format (frame, estimate, design, defend, evolve). |
| `prd-frame-estimate` | Writes the six-row Frame + Estimate block that opens every PRD. |
| `client-doc-build-plan` | Writes `build-plan.md`: outcomes and tasks from the tasks system, or drafted from every meeting debrief and transcript (verified against the recordings) when the project has none yet. |

## Documentation around the build

| Skill | What it does |
|---|---|
| `auto` | Writes a short bullet doc explaining one automation's trigger, inputs, steps, and outputs. |
| `how-it-works-doc` | Writes a plain-English doc explaining what an automation does and what it does not do. |
| `education` | Writes a full 11-section how-it-works doc for a larger automation. |
| `artifact` | Publishes a shareable web page that explains to a client what was built in a session. |
| `ship` | Runs `education` and then `artifact` on a just-deployed automation and moves its shipping-queue item to Shipped. |
| `business-case` | Turns a discovery call transcript into an XRAY-branded business case Word doc. |
| `write-soap-report` | Turns a session transcript into an XRAY-branded SOAP report Word doc. |
| `markdown-to-xr-gdoc` | Converts a Markdown file into an XRAY-branded HTML doc and sends it to be converted into a Google Doc. |
| `file-naming-convention` | Names files in client folders as CLIENT-Type-YYYY-MM-DD-topic. |
| `spec-driven-dev` | Enforces the README-first, dry-run, review, apply, and post-run sequence for every change to a client base. |
| `workflow-eval` | Checks whether a multi-step automation chain produced the expected results and marks each case pass, fail, or unverified. |
| `audit-log-plugin` | Reads the `execute` skill's audit log and reports whether a run is Verified, Not achieved, or Unknown. |

## Tasks and meetings

| Skill | What it does |
| --- | --- |
| `fetch-tasks` | Fetches a client's open tasks from the XRAY task hub, sorts them by status, and reports duplicates and other hygiene problems without changing anything. |
| `transcript-review` | Turns a meeting transcript into a debrief file and, after approval, Airtable tasks for the action items. |

Every one of the 10 outputs is written by a skill in this plugin.

Each writing skill has a finished example for a made-up client in its `references/` folder.

## Install

- **Claude Code:** `/plugin install client-docs --marketplace RachaelQuisel/Skills`
- **claude.ai and Claude Desktop:** open Customize, then Plugins, then Add, then Add marketplace, and enter `RachaelQuisel/Skills`; then install Client Docs.

## Maintenance

Owner: Rachael Quisel. Each skill is listed in the [collection register](../../maintenance/collection.json). See the [maintenance guide](../../maintenance/README.md).
