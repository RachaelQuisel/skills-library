---
name: vibe-safe-errors
version: 1.0.1
description: Implements secure error handling patterns that log internally but never leak sensitive information to clients. Use when adding try/catch blocks, error boundaries, creating error responses, or building error handling middleware.
tags:
  - skill
---

# Vibe-Safe: Secure Error Handling

## Purpose in plain English

This skill helps you handle application errors without revealing sensitive internal details to users.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Apply these principles when handling errors.

## Risk-First Thinking

Before writing error handling:
1. **Think:** "What information could leak to attackers?"
2. **Plan:** "What gets logged vs returned?"
3. **Code:** Generate with security built in
4. **Verify:** Test that errors don't expose internals

## Non-Negotiable Constraints

- NEVER return stack traces to clients
- NEVER expose file paths, dependency versions, or database details
- NEVER silently swallow errors without logging
- NEVER use `catch (e: any)` — use `catch (error: unknown)`
- ALWAYS log full error internally with context
- ALWAYS return sanitized, generic errors to clients

## Secure Error Defaults

When handling errors:
- Wrap all async operations in try/catch
- Log internally: full error, path, method, user ID
- Return to client: generic message, error code, appropriate status
- Use structured responses: `{ error: string, code?: string }`

## When to Read Reference

For detailed error handling patterns, read `references/error-handling.md`.
