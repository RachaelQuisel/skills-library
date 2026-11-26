# Skills

A library of **AI agent skills** for Claude Code — modular, self-contained instruction bundles that extend agent capabilities across planning, development, client work, and operations.

Each skill lives in its own folder and contains a `SKILL.md` plus optional `references/`, `scripts/`, and `assets/`.

## Where things live

- This repo is the one public home for every skill. Each skill has one folder at the top level.
- Each plugin has its own repo. `.claude-plugin/marketplace.json` installs each of those plugins from its repo.
- A skill that ships inside a plugin is edited here. The same change is then copied to the plugin's repo. No script makes that copy yet.
- Ten plugins still have a folder in `plugins/`. Eight of them have no repo of their own yet: `automation-briefing`, `automation-catalog`, `automation-catalog-failure-check`, `client-docs`, `find-fix-mistakes`, `independent-check`, `skillkeeper` and `zite-prompt`. The other two, `github-portfolio-builder` and `github-portfolio-review`, have repos with a different layout.
- Client names, people's names, email addresses, phone numbers and workspace IDs in this repo are dummy data.
- A skill that needs real private details has a private version in a private repo.

## Skillkeeper plugin

[Skillkeeper](plugins/skillkeeper/README.md) packages the maintained-skills routine as a private Claude Code plugin. It inventories skill ownership and versions, preserves sanitized regression cases, separates offline checks from live compatibility evidence, prepares controlled updates and rollbacks, and explains failures without guessing their cause.

```text
claude plugin marketplace add RachaelQuisel/Skills
claude plugin install skillkeeper@rachael-quisel-skills
```

The plugin is instruction-only. The repository workflow and ChatGPT alert task remain separate services and must be verified independently.

## Zite Prompt plugin

[Zite Prompt](plugins/zite-prompt/README.md) creates lean, paste-ready prompts using verified facts and known IDs. It includes examples for interface builds, prompt shortening, and missing decisions.

```text
claude plugin install zite-prompt@rachael-quisel-skills
```

## Skills in this repo

### Planning & Design

| Skill | Purpose |
|-------|---------|
| **write-a-prd** | Create a PRD through user interview + codebase exploration, filed as a GitHub issue |
| **prd-to-plan** | Turn a PRD into a phased implementation plan using tracer-bullet vertical slices |
| **prd-to-issues** | Break a PRD into independently-grabbable GitHub issues |
| **grill-me** | Stress-test a plan or design by interviewing relentlessly |
| **request-refactor-plan** | Plan a refactor with tiny commits, filed as a GitHub issue |
| **ubiquitous-language** | Extract a DDD-style glossary from conversation, saved to UBIQUITOUS_LANGUAGE.md |
| **business-case** | Discovery call transcript to XRAY-branded business case (.docx) |
| **business-requirements** | Elicit and capture business requirements (Vision & Scope) |

### Development

| Skill | Purpose |
|-------|---------|
| **explore-first** | Understand codebase and requirements before implementing |
| **create-plan** | Produce a markdown execution plan with status tracking |
| **zite-prompt** | Create compact, implementation-focused prompts for Zite while keeping research and decision-making outside Zite |
| **execute** | Implement the plan step by step |
| **workflow-orchestration** | Plan-first, verification, lessons, subagents for non-trivial tasks |
| **review** | Code review checklist and output format |
| **create-issue** | Fast capture of bugs/features mid-development |
| **triage-issue** | Investigate a bug, find root cause, file a GitHub issue with TDD fix plan |
| **qa** | Interactive QA session — report bugs conversationally, agent files GitHub issues |
| **explain-code** | Explain code with visual diagrams and analogies |
| **peer-review** | Cross-model review (Codex/Gemini reviews Claude's work) |
| **research** | Research using subagents (APIs, data, debugging, comparisons) |
| **tech-docs-bootstrap** | Bootstrap technical documentation for a project |

### Security

| Skill | Purpose |
|-------|---------|
| **vibe-safe** | Secure API development (RAILGUARD, validation, auth, errors) |
| **vibe-safe-auth** | Secure authentication patterns (login, sessions, CSRF) |
| **vibe-safe-errors** | Secure error handling (no info leaks) |
| **vibe-safe-upload** | Secure file upload handling (MIME validation, size limits) |
| **git-guardrails-claude-code** | Block dangerous git commands via Claude Code hooks |

### Client & Operations (XRAY)

| Skill | Purpose |
|-------|---------|
| **micro-case-study** | Mine transcripts for atomic client wins, produce structured MCS records |
| **kpi-report** | Generate KPI reference doc from discovery transcript |
| **post-to-huddle** | Post updates to client Slack huddle channels |
| **humanizing** | Rewrite text in Rachael's voice |
| **insidery** | Rewrite text in XRAY engineering team voice |
| **internal-comms** | Internal comms (status reports, newsletters, FAQs) |
| **xray-brand** | Apply XRAY 2026 brand identity to any output |
| **xray-tasks** | Interact with the XRAY Task Inbox |
| **task-check** | List active tasks from tasks.xray.tech |
| **new-account** | Log signups/subscriptions to Airtable |
| **omni-prompt** | Generate Airtable Omni AI prompts for interfaces |

### Documents & Output

| Skill | Purpose |
|-------|---------|
| **docx** | Create, read, edit Word documents |
| **pdf-builder** | Build production PDF documents with ReportLab |
| **markdown-to-xr-gdoc** | Convert Markdown to branded XRAY Google Docs |
| **frontend-design** | Production-grade frontend interfaces |
| **slack-gif-creator** | Animated GIFs optimized for Slack |
| **puzzle-prompt-builder** | Convert SOPs/workflows into Puzzle.io Nova prompts |

### Travel

| Skill | Purpose |
|-------|---------|
| **travel-brief** | Comprehensive travel briefing with logistics |
| **travel-packing-list** | Personalized packing lists |

### Meta

| Skill | Purpose |
|-------|---------|
| **skill-creator** | Create and package new skills |
| **token-check** | Estimate token usage of a skill |
| **context-awareness** | Monitor context window, create session handoff documents |
| **gem-miner** | Mine conversations for gems (daily) |
| **mcp-troubleshooting** | Diagnose MCP server auth failures |

## Audit log pilot

The audit log keeps a diary of everything the Execute skill does when it carries out a written plan. There is no schedule. It runs whenever someone asks Execute to work.

As Execute goes, it writes a short dated note at each key moment: when it starts, when it begins a step, which files it changed, what test it ran and whether it passed, when it finishes a step, and when it stops to flag a problem. If a step has no named test, it writes "review" plus the step's name. That counts as weaker proof, because Execute is vouching for itself.

The input is the plan file (a to-do list whose steps are marked red, yellow, or green) plus those notes. The output is the diary, one line per event, and the report from the automation run verifier. The automation run verifier reads the diary and gives one of three answers:

- **Verified.** Every main step is green, each one had a passing test after its last file change and before it was marked done, the percentage matches the share of finished steps, and the only files touched were ones the plan named, ones explicitly approved when Execute flagged a problem, or the plan file itself.
- **Not achieved.** Something clearly went wrong: a step is still open, a test failed in that window, the percentage does not add up, or a file changed that was not in the plan and was not approved.
- **Unknown.** Some proof is missing, or a test result sits outside that window, so the automation run verifier will not call the job finished.

The diary is a plain text file, `execute/.audit/events.jsonl`, in a hidden folder inside the Execute skill on the computer that ran it. That folder stays out of the GitHub repo, so the diary is not online yet. A database version is planned later.

If a step was marked done without proof, the separate correction tool (`audit-log-plugin/scripts/reopen_task.py`), not the automation run verifier, reopens it. That tool flips the step back from green, updates the percentage, and writes a note. It never touches the actual work or the code.

## Structure of a skill

```text
skill-name/
├── SKILL.md          # Required: YAML frontmatter (name, description) + body
├── references/       # Optional: loaded when the skill says to read them
├── scripts/          # Optional: runnable helpers
└── assets/           # Optional: templates, images
```

## Installation

This repo is cloned to `~/.claude/skills/`. Claude Code discovers skills automatically from that location and exposes them as slash commands (e.g. `/review`, `/qa`).

## Creating new skills

```bash
python3 skill-creator/scripts/init_skill.py <name> --path ~/.claude/skills/
```

## Maintained collection

Each of the 161 registered skill paths has a maintenance README. This inventory includes standalone skills and nested plugin copies in this repository. The combined Skill checks workflow checks release versions, inventory, and registered tests on changes and every Monday at 15:30 UTC. The existing hourly task reports each unresolved problem once and sends one verified recovery notice. Its saved alert record prevents repeated messages for the same problem. These routines run without a personal computer.

Read [how the maintenance routine works](maintenance/Skills-HowItWorks-2026-10-11-maintenance.md) for the trigger, inputs, steps, and outputs. The [maintenance guide](maintenance/README.md) explains tests, support, update approval, and returning to an earlier version. Live integration and agent compatibility remain unverified until separately tested. Installed skills are not updated automatically.



## Automation catalog plugins

| Plugin | Purpose |
| --- | --- |
| [Automation Metadata Maker](plugins/automation-catalog/README.md) | Find accessible automations and update their guides, categories, tags and approved Slack messages. |
| [Automation Catalog Failure Check](plugins/automation-catalog-failure-check/README.md) | Check for missing catalog reports and send known failures or blockers to an approved channel. |

Both have matching Soft Index icons and plain-English instructions. The repository marketplace lists both packages. They are private review versions, not approved Anthropic directory listings. See the [marketplace review](deployments/automation-catalog/marketplace-review.md) for validation results and remaining Claude checks.

The [configured cloud routines](deployments/automation-catalog/README.md) run on Mondays at 5 AM and 6 AM Pacific. Generic plugin installation does not create these schedules. Package tests run separately from the top-level maintained-skills collection.

