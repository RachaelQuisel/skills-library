---
name: new-account
version: 1.0.2
description: Log new account signups, subscriptions, and recurring donations to Airtable. Scans bank statements (PDF/CSV) to discover, update, and reconcile subscriptions. Triggers on "signed up", "new account", "subscribed", "started using", "registered", "donation", "recurring", "bank statement", "credit card statement", "transactions".
tags:
  - skill
---

# New Account Logger

## Purpose in plain English

This skill helps you record account signups and recurring payments, and reconcile them against the information you provide.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Log new account signups and subscriptions to the Subscriptions table in Airtable.

## Airtable Details

- **Base ID**: `appExample0000107`
- **Table ID**: `tblExample0000108`
- **Table Name**: Subscriptions

### Field IDs

| Field | ID | Type |
|-------|-----|------|
| Name (service) | `fldExample0000109` | singleLineText |
| Email Used | `fldExample0000110` | singleLineText |
| Date Signed Up | `fldExample0000111` | date |
| Plan/Tier | `fldExample0000112` | singleLineText |
| Monthly Cost | `fldExample0000113` | currency |
| Renewal Date | `fldExample0000114` | date |
| Category | `fldExample0000115` | singleSelect |
| Notes | `fldExample0000116` | multilineText |
| Benefits | `fldExample0000117` | multilineText |
| Subscription Status | `fldExample0000118` | singleSelect |
| Payment Card | `fldExample0000119` | singleLineText |

### Category Choices

Valid category names: `Dev Tools`, `Media`, `Productivity`, `AI/ML`, `Finance`, `Communication`, `Design`, `Other`

### Subscription Status Choices

Valid status names: `Active`, `Cancelled`, `Free Trial`, `Unknown`

Default new signups to `Active`. Use `Free Trial` when the user mentions a trial. Only mark `Cancelled` when there is **evidence** the subscription has actually been cancelled (e.g., cancellation confirmation email, no charges for multiple billing cycles). If the user says they *want* to cancel, keep it Active and add a note — the status tracks reality, not intent.

## Workflow

1. **Extract what you can** from the user's message. If they said "I just signed up for Figma Pro for $15/mo", pull out: service name, plan, cost.

2. **Check for duplicates** before proceeding. Search the table for an existing record with the same service name. If found, ask the user if they want to update the existing record or create a new one.

3. **Ask only for missing details** using AskUserQuestion. Required: service name. Everything else is optional but try to collect at least plan/tier and category. **This table is for personal accounts only** — don't ask which email; leave Email Used blank unless the user volunteers a specific address. If the user mentions which card/account, populate Payment Card.

4. **Default Date Signed Up to today** (use ISO format YYYY-MM-DD).

5. **Infer the category** from the service name when obvious:
   - GitHub, VS Code, Vercel, Railway, Heroku, Netlify, Docker → Dev Tools
   - Spotify, Netflix, YouTube, Hulu, Apple Music → Media
   - Notion, Airtable, Slack, Asana, Monday, Trello, Todoist → Productivity
   - ChatGPT, Claude, Midjourney, Copilot, Perplexity, Cursor → AI/ML
   - QuickBooks, Stripe, Plaid, Brex, Mercury → Finance
   - Zoom, Discord, Teams, Webex, Loom → Communication
   - Figma, Canva, Adobe, Sketch, Framer → Design
   - If unsure, ask or use Other

6. **Create the record** using `mcp__airtable__create_record` with base ID `appExample0000107` and table ID `tblExample0000108`. Use field IDs (not names) in the fields object. For the Category field, pass the choice **name** as a string (e.g., `"Dev Tools"`), not an ID object.

7. **Set cancellation reminder for free trials / promos** — whenever the subscription status is `Free Trial` or the plan involves a free period that auto-renews to paid, create a Google Calendar event on `person4@example.com` using `mcp__claude_ai_Google_Calendar__gcal_create_event`:
   - **Calendar**: `person4@example.com`
   - **Date**: 1 week before the free period ends
   - **Title**: `Cancel or renew [Service Name] (free trial/promo expires)`
   - **Description**: Include what the trial is, when it was redeemed, any codes used, and where to manage/cancel
   - **Reminders**: popup + email, both 7 days before (10080 minutes)
   - **sendUpdates**: `none`

8. **Confirm** with a short summary like:
   > Logged: **Figma** — Pro plan, $15/mo, Design category.

## Bank Statement Scanning

When the user shares a bank or credit card statement (PDF or CSV):

1. **Read all pages/rows** of the statement.
2. **Identify recurring charges** — look for merchant names that match known subscription patterns (software, media, SaaS, memberships, donations, health/wellness). Filter out one-time purchases (Amazon marketplace, restaurants, gas, groceries, parking).
3. **Cross-reference against existing records** — list all current records from the Subscriptions table, then match by merchant name. Watch for merchant name variations (e.g., `NOTION LABS, INC.` = Notion, `X CORP. PAID FEATURES` = X Premium, `HUMANE WORLD FKA HSUS` = Free Animal Doctor).
4. **For existing records**: update Monthly Cost if it was missing, confirm Subscription Status as Active, and add billing details to Notes.
5. **For new subscriptions**: create records with all available data — infer category, set status to Active, note the billing merchant name.
6. **Flag ambiguous charges** for user confirmation — charges that might be subscriptions but aren't clearly recurring (e.g., Thrive Causemetics, Konmari).
7. **Detect cancellations** — if a subscription that was previously recurring has no charge in the latest statement period, flag it as potentially cancelled.
8. **Clean up** — delete empty records, resolve Unknown statuses where the statement provides evidence.
9. **Set Payment Card** — identify which card/account each charge appeared on. Use format: `Visa ...0439 (Rachael)`, `Card ...6175 (Thomas)`, `Apple App Store`, `Apple (direct billing)`, or `N/A (Free)`. For CSV statements, check the memo field for cardholder name. For PDFs, use the card type and last 4 digits from the header.
10. **Summarize** — show the user what was updated, created, and flagged.

### Merchant Name Mappings

See [references/merchant-mappings.md](references/merchant-mappings.md) for the full table of known bank statement merchant names → subscription record names. Read this file when scanning statements.

## Date Format

All date fields use ISO 8601: `YYYY-MM-DD`

## Notes Field

Use the Notes field for any extra context the user mentions, like:
- "annual plan, paid via company card"
- "free trial ends May 1"

## Benefits Field

Use the Benefits field to capture what the user gets from the subscription — perks, bundled services, discounts on other platforms, access to communities, etc. Ask the user if they know of any specific benefits, or note obvious ones:
- "Includes free access to Recomendo and other Substack bundles"
- "Search & rescue helicopter evacuation coverage"
