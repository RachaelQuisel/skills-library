---
name: mcp-troubleshooting
version: 1.0.1
description: Diagnose and fix MCP server authentication failures. Use when mcp__airtable__, mcp__github__, or other MCP tools return "Invalid authentication token", "UNAUTHORIZED", or "AUTHENTICATION_REQUIRED" errors. Helps determine if the token is actually invalid or if the MCP server is using a stale cached token.
tags:
  - skill
---

# MCP Authentication Troubleshooting

## Purpose in plain English

This skill helps you find and resolve sign-in or access problems affecting an assistant's connected tools.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


## The Core Issue

MCP servers cache tokens at startup. When a user regenerates a token, the MCP server continues using the old cached token until restarted.

## Diagnosis: Test Token Directly

Before assuming the token is invalid, bypass MCP and test with curl:

```bash
# Airtable
curl -s "https://api.airtable.com/v0/meta/bases" -H "Authorization: Bearer <TOKEN>"

# GitHub
curl -s "https://api.github.com/user" -H "Authorization: Bearer <TOKEN>"
```

## Interpreting Results

| MCP Result | Direct API Result | Diagnosis | Action |
|------------|-------------------|-----------|--------|
| Auth error | Auth error | Token invalid | User must fix token |
| Auth error | **Success** | **Stale MCP cache** | Use direct API calls |
| Success | Success | No problem | - |

## Solution: Bypass MCP with Direct API

When MCP has a stale token but the user's token works, use curl directly:

```bash
# Instead of mcp__airtable__create_table:
API_KEY='pat...' curl -s -X POST "https://api.airtable.com/v0/meta/bases/BASE_ID/tables" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "TableName", "fields": [...]}'
```

## Alternative: Restart MCP

Tell the user to restart Claude Code to reinitialize MCP servers with the new token.
