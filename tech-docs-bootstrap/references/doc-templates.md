# Documentation File Templates

Templates for each file type the skill produces. Adapt as needed — these are
defaults, not rigid formats.

## Table of Contents

- [Technology Doc (Core)](#technology-doc-core)
- [Technology Doc (Supporting)](#technology-doc-supporting)
- [Infrastructure Doc](#infrastructure-doc)
- [docs/README.md](#docsreadmemd)
- [Schema Overview](#schema-overview)
- [Individual Table Doc](#individual-table-doc)

---

## Technology Doc (Core)

For frameworks and libraries central to the project.

```markdown
# {Technology Name} v{version}

> {One-line role in this project}

## Key APIs and Patterns

### {Pattern 1 name}

{Brief explanation + code example showing how THIS PROJECT uses it}

### {Pattern 2 name}

{Brief explanation + code example}

## Configuration

{Document the project's actual config, not generic defaults}

**File**: `{path to config file}`

Key settings:
- `{setting}`: {what it does and why it's set this way}

## Common Pitfalls

- **{Pitfall 1}**: {What goes wrong and how to fix it}
- **{Pitfall 2}**: {What goes wrong and how to fix it}

## Project Conventions

- {Convention 1 observed in this codebase}
- {Convention 2 observed in this codebase}

## Links

- Official docs: {url}
- API reference: {url}
```

## Technology Doc (Supporting)

For utilities and secondary libraries. Keep it brief.

```markdown
# {Technology Name} v{version}

> {One-line role in this project}

## Quick Reference

{Most-used APIs in this project, as a compact list or table}

| Function | Purpose |
|----------|---------|
| `{fn1}` | {what it does} |
| `{fn2}` | {what it does} |

## Gotchas

- {Gotcha 1}
- {Gotcha 2}

## Links

- Docs: {url}
```

## Infrastructure Doc

For deployment, CI/CD, and operational tools.

```markdown
# {Tool Name}

> {One-line role in this project}

## Configuration

**File**: `{path}`

{Key configuration details}

## Common Operations

### {Operation 1, e.g. "Deploy"}

```bash
{command}
```

### {Operation 2, e.g. "View logs"}

```bash
{command}
```

## Environment Variables

| Variable | Purpose | Where Set |
|----------|---------|-----------|
| `{VAR}` | {purpose} | {.env / CI / etc.} |
```

## docs/README.md

The index file for the documentation folder.

```markdown
# Project Technical Documentation

Generated: {YYYY-MM-DD}

## Tech Stack

| Category | Technology | Version | Doc |
|----------|-----------|---------|-----|
| Framework | {e.g. Next.js} | {version} | [{name}.md]({name}.md) |
| Data | {e.g. Prisma} | {version} | [{name}.md]({name}.md) |
| ... | ... | ... | ... |

## Data Model

Overview: [data/schema-overview.md](data/schema-overview.md)

| Table | Description | Doc |
|-------|-------------|-----|
| {table} | {description} | [data/{table}.md](data/{table}.md) |

## Updating These Docs

To refresh: ask Claude to "update the project docs" or "refresh docs for {technology}".
These docs are reference material for LLM-assisted development — keep them
accurate when the stack changes.
```

## Schema Overview

High-level view of the data model.

```markdown
# Data Schema Overview

## Entity Relationship Summary

{Brief text description of how the main entities relate}

## Tables

| Table | Description | Key Fields |
|-------|-------------|------------|
| {table_name} | {purpose} | {important columns} |

## Key Relationships

- `{table_a}.{field}` -> `{table_b}.{field}` ({relationship type})
- ...

## Notes

- {Any important data conventions, naming patterns, or constraints}
```

## Individual Table Doc

For tables with 5+ fields that warrant their own file.

```markdown
# {Table Name}

> {What this table stores and its role in the system}

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `{field_name}` | {type} | {yes/no} | {purpose} |

## Relationships

- `{field}` references `{other_table}.{field}` — {explanation}

## Indexes

- `{index_name}` on `({fields})` — {why}

## Common Query Patterns

### {Pattern name, e.g. "Find active users"}

```sql
{example query or ORM call}
```

## Notes

- {Important constraints, default values, or business logic tied to this table}
```
