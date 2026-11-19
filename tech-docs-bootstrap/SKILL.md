---
name: tech-docs-bootstrap
version: 1.0.1
description: >
  Create organized technical documentation for a project so LLMs have accurate,
  up-to-date reference material during development. Scans the codebase to detect
  the tech stack, fetches current documentation via Context7 and web search, and
  documents data table schemas. Outputs a structured docs/ folder wired into
  CLAUDE.md. Use when the user says things like "set up docs for this project",
  "bootstrap technical docs", "create reference docs", "document the tech stack",
  "add project documentation", or "set up docs so you have context". Works for
  both new project bootstrapping and enriching existing projects mid-development.
tags:
  - skill
---

# Tech Docs Bootstrap

## Purpose in plain English

This skill helps you create organized technical reference documents from an existing project.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Bootstrap a project's `docs/` folder with organized, LLM-optimized technical
reference material so Claude has accurate context when developing.

## Workflow

1. **Detect** the tech stack from project files
2. **Confirm** findings with the user and gather additions
3. **Classify** each technology as core or supporting
4. **Fetch** documentation using Context7 and web search
5. **Document data tables** if a data layer exists
6. **Write** organized files into `docs/`
7. **Wire** docs into CLAUDE.md

## Step 1: Detect Tech Stack

Run the included stack detection script from the project root:

```bash
python scripts/detect_stack.py .
```

This script will quickly scan `package.json`, `Cargo.toml`, `pyproject.toml`, and other configuration files to output a structured JSON list of the frameworks, languages, data layer, testing tools, and infrastructure used in the repository. This saves you from having to manually traverse deep directories or burn tokens reading giant manifest files.

## Step 2: Confirm with User

Present the detected stack as a categorized list and ask:
- Is this complete? Any technologies to add or remove?
- Are there external services or APIs the project integrates with?
- Any data stores not captured (Airtable bases, external DBs, etc.)?

## Step 3: Classify Technologies

Categorize each technology to determine documentation depth:

**Core** (thorough docs) — frameworks and libraries central to the project's
architecture. These get comprehensive docs with API patterns, configuration,
and common pitfalls. Examples: Next.js for a Next app, Prisma for the data layer.

**Supporting** (concise docs) — utilities, dev tools, and secondary libraries.
These get a focused cheat sheet. Examples: lodash, prettier, eslint.

**Infrastructure** (operational docs) — deployment, CI/CD, containerization.
Document configuration and common operations.

Use judgment: if a library appears in many files or is architecturally significant,
treat it as core even if it might seem minor.

## Step 4: Fetch Documentation

For each technology, gather current documentation:

1. **Context7 first** — use `resolve-library-id` then `get-library-docs` with a
   relevant topic. Set tokens based on classification:
   - Core: 8000-10000 tokens
   - Supporting: 3000-5000 tokens
   - Infrastructure: 3000-5000 tokens

2. **Web search for gaps** — if Context7 lacks coverage or the user needs specific
   topics (migration guides, version-specific changes), use web search.

3. **Code analysis** — scan how the project actually uses each technology. Note
   specific patterns, configurations, and conventions already in place.

Synthesize these sources into documentation. See `references/doc-templates.md`
for the file format templates.

### What makes good LLM reference docs

- **Version-specific**: pin the version, note breaking changes from prior versions
- **Pattern-focused**: show the patterns this project uses, not every possible API
- **Gotcha-heavy**: common mistakes and their fixes save the most time
- **Example-rich**: short, real code examples > lengthy explanations
- **Project-aware**: reference this project's actual file structure and conventions

### What to skip

- Generic "what is X" introductions (Claude already knows)
- Exhaustive API listings (link to official docs instead)
- Tutorial-style walkthroughs
- Historical context or philosophy

## Step 5: Document Data Tables

If a data layer is detected, document the schema. Adapt approach based on source:

**ORM/Migration and SQL files**:
Use the included schema parser script to automatically extract the schemas into LLM-friendly markdown:

```bash
python scripts/parse_schema_to_markdown.py .
```

This will automatically output the schema definitions in markdown so you don't have to manually read and parse massive SQL or Prisma files block-by-block.

**Airtable** (if MCP available):
- Use `list_bases` to find the relevant base
- Use `list_tables` then `describe_table` with `detailLevel: "full"`
- Document fields, types, and views

**Supabase/External DBs**:
- Check for type definitions, API clients, or schema dumps in the codebase
- Ask the user for connection details if needed

Create `docs/data/schema-overview.md` plus individual table docs for tables with
5+ fields. See `references/doc-templates.md` for the table documentation format.

## Step 6: Write Documentation Files

Create this structure:

```
docs/
  README.md                  # Stack overview and docs index
  {technology-name}.md       # One file per core/supporting technology
  data/
    schema-overview.md       # Data model overview with relationships
    {table-name}.md          # Per-table docs (for tables with 5+ fields)
```

Naming conventions:
- Use kebab-case for all filenames: `next-js.md`, `react-query.md`
- Group data docs under `data/` subdirectory
- Keep `README.md` as the index/overview

The `README.md` should contain:
- Project tech stack at a glance (table format)
- Links to each doc file with one-line descriptions
- Date generated and instructions for updating

## Step 7: Wire into CLAUDE.md

Append or update the project's `CLAUDE.md` to reference the docs:

```markdown
## Technical Documentation

Reference docs are in `docs/`. Consult them when working with unfamiliar
parts of the stack.

- Stack overview: docs/README.md
- Data schema: docs/data/schema-overview.md
```

If `CLAUDE.md` doesn't exist, create it with this section plus a brief project
description inferred from the codebase.

If `CLAUDE.md` already exists, append the documentation section — do not
overwrite existing content.

## Updating Existing Docs

When run on a project that already has `docs/`, ask the user:
- Refresh all docs, or only specific ones?
- Any new technologies to add?

Overwrite only the files that need updating. Preserve any manually-added docs.
