---
name: airtable-skill
version: 1.0.1
description: "garyj/airtable-skill — Python (pyairtable) CLI scripts for Airtable connection testing, record CRUD, batch operations, schema management, and webhooks. Use ONLY when the user explicitly asks for the pyairtable Python CLI path or webhook management; otherwise prefer airtable-cli or the native mcp__airtable__* tools."
---

# Airtable Skill (garyj/airtable-skill)

## Purpose in plain English

This skill helps you work with Airtable through the Python tools when you specifically need that approach.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


You are an Airtable integration assistant that helps users access and manage their Airtable bases, tables, and records using Python CLI scripts.

**Rachael note:** this skill overlaps with `airtable-cli` and the native `mcp__airtable__*` tools. Its unique surface is **webhooks**. Do not select this skill for record/schema work unless the user names it.

## Prerequisites

Before any Airtable operation, ensure:

1. **Python 3.10+** is installed
2. **uv** package manager is available
3. **AIRTABLE_API_TOKEN** environment variable is set

If the token is not configured, guide the user:

> **Set up Airtable API access:**
> 1. Go to https://airtable.com/create/tokens
> 2. Create a new token with scopes:
>    - `data.records:read` (read records)
>    - `data.records:write` (create/update/delete records)
>    - `schema.bases:read` (view base structure)
>    - `schema.bases:write` (create tables/fields)
>    - `webhook:manage` (for webhook operations)
> 3. Add access to the required bases
> 4. Set the environment variable:
>    ```bash
>    export AIRTABLE_API_TOKEN="patXXXXXXXX.XXXXXXX"
>    ```

## Privacy Guidelines

**Always follow [privacy.md](privacy.md) for data handling.** Key rules:

- **Never expose API tokens** in output or error messages
- **Confirm before write operations** (create, update, delete)
- **Fetch minimal data** using `--fields` and `--max-records`
- **Handle PII carefully** - mask sensitive data, summarize rather than dump
- **Format output cleanly** as tables, not raw JSON

## Scripts Reference

All scripts use `uv run ~/.claude/skills/airtable-skill/scripts/<script>.py` pattern.

### connection.py - Connection & Discovery

Test connectivity and discover accessible bases.

```bash
# Test API connection
uv run ~/.claude/skills/airtable-skill/scripts/connection.py test

# List all accessible bases
uv run ~/.claude/skills/airtable-skill/scripts/connection.py bases

# List bases with JSON output
uv run ~/.claude/skills/airtable-skill/scripts/connection.py bases --json
```

### schema.py - Schema Management

Inspect and modify table structures.

```bash
# List all tables in a base
uv run ~/.claude/skills/airtable-skill/scripts/schema.py tables list --base-id appXXX

# Describe table fields
uv run ~/.claude/skills/airtable-skill/scripts/schema.py tables describe --base-id appXXX --table "Contacts"

# Create a new table
uv run ~/.claude/skills/airtable-skill/scripts/schema.py tables create --base-id appXXX --name "Tasks" \
    --fields '[{"name": "Task Name", "type": "singleLineText"}, {"name": "Due Date", "type": "date"}]'

# Delete a table
uv run ~/.claude/skills/airtable-skill/scripts/schema.py tables delete --base-id appXXX --table "Old Table"

# Add a field to existing table
uv run ~/.claude/skills/airtable-skill/scripts/schema.py fields create --base-id appXXX --table "Contacts" \
    --field '{"name": "Notes", "type": "multilineText"}'

# Update field name or description
uv run ~/.claude/skills/airtable-skill/scripts/schema.py fields update --base-id appXXX --table "Contacts" \
    --field-id fldXXX --name "Contact Notes"

# List all views on a table
uv run ~/.claude/skills/airtable-skill/scripts/schema.py views list --base-id appXXX --table "Contacts"
```

**Supported field types (create_field):** singleLineText, multilineText, number, email, url, phoneNumber, singleSelect, multipleSelects, checkbox, date, dateTime, currency, percent, duration, rating, richText, multipleRecordLinks, multipleAttachments, multipleLookupValues, rollup.
**Not creatable by this script:** formula, count, button, auto fields. (Rachael note: the raw Airtable REST API DOES accept `formula` via create_field as of mid-2026 per `feedback_airtable_formula_workaround`; this script's validator doesn't allow it, so use `mcp__airtable__create_field` or raw REST for formula fields.)

### records.py - Record CRUD & Comments

Create, read, update, delete, and query records.

```bash
# List records
uv run ~/.claude/skills/airtable-skill/scripts/records.py list --base-id appXXX --table "Contacts" \
    --fields "Name,Email,Company" --max-records 10

# List from a view
uv run ~/.claude/skills/airtable-skill/scripts/records.py list --base-id appXXX --table "Contacts" --view "Active Contacts"

# Get a specific record
uv run ~/.claude/skills/airtable-skill/scripts/records.py get --base-id appXXX --table "Contacts" --record-id recXXX

# Query with Airtable formula
uv run ~/.claude/skills/airtable-skill/scripts/records.py query --base-id appXXX --table "Contacts" \
    --formula "{Status}='Active'"

# Query with match criteria (equality)
uv run ~/.claude/skills/airtable-skill/scripts/records.py query --base-id appXXX --table "Contacts" \
    --match '{"Status": "Active", "Company": "Acme Corp"}'

# Create / update / delete
uv run ~/.claude/skills/airtable-skill/scripts/records.py create --base-id appXXX --table "Contacts" \
    --fields '{"Name": "John Doe", "Email": "john@example.com"}'
uv run ~/.claude/skills/airtable-skill/scripts/records.py update --base-id appXXX --table "Contacts" \
    --record-id recXXX --fields '{"Status": "Inactive"}'
uv run ~/.claude/skills/airtable-skill/scripts/records.py delete --base-id appXXX --table "Contacts" \
    --record-id recXXX

# Comments
uv run ~/.claude/skills/airtable-skill/scripts/records.py comments --base-id appXXX --table "Contacts" --record-id recXXX
uv run ~/.claude/skills/airtable-skill/scripts/records.py add-comment --base-id appXXX --table "Contacts" \
    --record-id recXXX --text "Followed up via email"
uv run ~/.claude/skills/airtable-skill/scripts/records.py delete-comment --base-id appXXX --table "Contacts" \
    --record-id recXXX --comment-id comXXX
```

### batch.py - Bulk Operations

Efficient batch create, update, upsert, and delete. Handles Airtable's 10-record-per-request limit automatically.

```bash
uv run ~/.claude/skills/airtable-skill/scripts/batch.py create --base-id appXXX --table "Contacts" \
    --records '[{"Name": "Alice"}, {"Name": "Bob"}]'

uv run ~/.claude/skills/airtable-skill/scripts/batch.py update --base-id appXXX --table "Contacts" \
    --records '[{"id": "recXXX", "fields": {"Status": "Active"}}]'

uv run ~/.claude/skills/airtable-skill/scripts/batch.py upsert --base-id appXXX --table "Contacts" \
    --records '[{"Email": "alice@example.com", "Name": "Alice Updated"}]' \
    --key-fields "Email"

uv run ~/.claude/skills/airtable-skill/scripts/batch.py delete --base-id appXXX --table "Contacts" \
    --record-ids "recXXX,recYYY,recZZZ"
```

### webhooks.py - Webhook Management

Unique to this skill — no equivalent in `airtable-cli` or `mcp__airtable__*`.

```bash
# List all webhooks
uv run ~/.claude/skills/airtable-skill/scripts/webhooks.py list --base-id appXXX

# Get webhook details
uv run ~/.claude/skills/airtable-skill/scripts/webhooks.py get --base-id appXXX --webhook-id whXXX

# Create a webhook (watch all table data)
uv run ~/.claude/skills/airtable-skill/scripts/webhooks.py create --base-id appXXX \
    --url "https://example.com/webhook" \
    --spec '{"options": {"filters": {"dataTypes": ["tableData"]}}}'

# Scoped to one table
uv run ~/.claude/skills/airtable-skill/scripts/webhooks.py create --base-id appXXX \
    --url "https://example.com/webhook" \
    --spec '{"options": {"filters": {"dataTypes": ["tableData"], "recordChangeScope": "tblXXX"}}}'

# Get webhook payloads (paginated by cursor)
uv run ~/.claude/skills/airtable-skill/scripts/webhooks.py payloads --base-id appXXX --webhook-id whXXX
uv run ~/.claude/skills/airtable-skill/scripts/webhooks.py payloads --base-id appXXX --webhook-id whXXX --cursor 123

# Delete
uv run ~/.claude/skills/airtable-skill/scripts/webhooks.py delete --base-id appXXX --webhook-id whXXX
```

## JSON Output Flag

All scripts support `--json` for machine-readable output. Always pass `--json` when parsing output programmatically.

## Error Handling

Scripts provide clear error messages without exposing sensitive data:

| Error | Message |
|-------|---------|
| Missing token | `AIRTABLE_API_TOKEN environment variable is not set` |
| Invalid token | `Authentication failed. Verify your AIRTABLE_API_TOKEN is valid.` |
| Base not found | `Base not found. Check the base ID and your token's permissions.` |
| Table not found | `Table 'X' not found in base.` |
| Permission denied | `Permission denied. Your token may not have access to this base.` |
