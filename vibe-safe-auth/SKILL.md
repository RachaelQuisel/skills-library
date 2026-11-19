---
name: vibe-safe-auth
version: 1.0.1
description: Implements secure authentication patterns including login, signup, sessions, password hashing, CSRF protection, and rate limiting. Use when building auth flows, password reset, session management, or OAuth integration.
tags:
  - skill
---

# Vibe-Safe: Secure Authentication

## Purpose in plain English

This skill helps you build account sign-in and session handling with appropriate security controls.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Apply these principles when implementing authentication.

## Risk-First Thinking

Before writing auth code:
1. **Think:** "How could an attacker bypass this?"
2. **Plan:** "What tests catch auth failures?"
3. **Code:** Generate with security built in
4. **Verify:** Test both happy path and attack scenarios

## Non-Negotiable Constraints

- NEVER store passwords in plaintext or with reversible encryption
- NEVER send passwords in URL query parameters
- NEVER log passwords, tokens, or session IDs
- NEVER return different errors for "user not found" vs "wrong password"
- ALWAYS use bcrypt (cost >= 12) or Argon2id for password hashing
- ALWAYS use generic error: "Invalid credentials"

## Secure Auth Defaults

When building login/signup:
- Session-based auth with CSRF protection
- Rate limiting: 5 attempts per 15 min per IP+username
- Account lockout after failed attempts
- Secure cookies: `httpOnly`, `secure`, `sameSite: 'lax'`

## When to Read Reference

For detailed auth implementation patterns, read `references/auth.md`.
