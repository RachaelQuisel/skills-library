---
name: review
version: 1.0.1
description: Run a structured, opinionated code review against a quality bar covering logging, error handling, TypeScript safety, production-readiness, React/hooks correctness, performance, security, and architectural fit. Use when the user says "review this", "review the code", "do a code review", "look this over", or wants a project-quality audit. This skill is a holistic project-quality check; for a focused diff-only bug-and-cleanup pass, use the built-in `code-review` skill instead.
tags:
  - skill
---
# Code Review Task

## Purpose in plain English

This skill helps you review code for reliability, clarity, maintainability, and problems that could affect users.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Perform a comprehensive code review. Be thorough but concise.

## How to run

1. Scope the review. Ask the user: just the current diff, a specific path, or the whole project? If unclear, default to the current diff.
2. Walk the checklist below in order. Skip categories that don't apply (e.g., React rules in a non-React file) instead of forcing them.
3. For each issue found, name the file and line, classify severity, and write a one-line fix. Don't paste large code blocks — point at the location.
4. End with the summary block. If zero issues, say so plainly.

## Check For

**Logging** - No console.log statements, uses proper logger with context
**Error Handling** - Try-catch for async, centralized handlers, helpful messages
**TypeScript** - No `any` types, proper interfaces, no @ts-ignore
**Production Readiness** - No debug statements, no TODOs, no hardcoded secrets
**React/Hooks** - Effects have cleanup, dependencies complete, no infinite loops
**Performance** - No unnecessary re-renders, expensive calcs memoized
**Security** - Auth checked, inputs validated, RLS policies in place
**Architecture** - Follows existing patterns, code in correct directory

## Output Format

### ✅ Looks Good
- [Item 1]
- [Item 2]

### ⚠️ Issues Found
- **[Severity]** [File:line] - [Issue description]
  - Fix: [Suggested fix]

### 📊 Summary
- Files reviewed: X
- Critical issues: X
- Warnings: X

## Severity Levels
- **CRITICAL** - Security, data loss, crashes
- **HIGH** - Bugs, performance issues, bad UX
- **MEDIUM** - Code quality, maintainability
- **LOW** - Style, minor improvements
