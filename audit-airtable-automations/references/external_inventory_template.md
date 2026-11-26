---
# External Automations Inventory
#
# Lists automations that touch an Airtable base but live outside Airtable:
# Zapier zaps, Apps Script projects, Make scenarios, n8n flows, webhooks,
# custom scripts.
#
# The audit-airtable-automations skill reads this file and adds one record per
# entry to the base's `Automation Inventory` table. Field names match the
# canonical schema (EA / AYMG / CC pattern).

base_id: appXXXXXXXXX  # the Airtable base these external automations touch

external_automations:
  - automation_name: "Stripe customer.created → Customers"
    trigger_type: Webhook                            # one of the Trigger Type single-select choices
    what_it_does: Mirrors new Stripe customers into the Customers table
    source_table: Customers                          # the table this automation writes to
    group: External                                  # A - Has script action | B - No script action | Sweep | External | Webhook
    fields_written: Stripe ID, Email, Signup Date on Customers
    status: Live                                      # Live | Built not deployed | Disabled | Off
    source_file: https://zapier.com/app/.../zaps/12345
    deployed: true
    logger_added: false
    trigger_condition: Fires on Stripe customer.created event
    owner: Rachael
    last_updated: 2026-04-15
    dependencies: None upstream; Customers welcome email downstream
    pain_points_addressed: Manual customer entry from billing system
    deliverable: Customers table auto-population
    notes:

  - automation_name: "Daily inventory rollup"
    trigger_type: Scheduled
    what_it_does: Aggregates shipped orders into a Daily Rollup summary and emails ops
    source_table: Orders
    group: A - Has script action
    fields_written: Creates row in Daily Rollup table; no field writes on Orders
    status: Live
    source_file: https://script.google.com/d/.../edit
    deployed: true
    logger_added: false
    trigger_condition: Runs daily at 02:00 UTC
    owner: Mark
    last_updated: 2026-03-22
    dependencies: Orders table Status field staying stable
    pain_points_addressed: Manual end-of-day reporting
    deliverable: Daily ops digest email
    notes:
---
