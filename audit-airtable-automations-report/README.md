# audit-airtable-automations-report

Audit all automations in an Airtable base. Use this skill whenever the user asks to document, audit, review, or understand Airtable automations — including questions like "what automations send emails to partners?", "map the automation cascade", "document all automations before we do cleanup", or "what triggers partner emails?". The skill produces a full audit document covering trigger conditions (watched fields and filter formulas, not vague "any update" labels), field writes, email recipients (decoded from Airtable's expression-tree AST into readable strings), cascade chains between automations, and per-automation hyperlinks back to Airtable. Requires the Airtable MCP and Chrome DevTools MCP (with Airtable open and authenticated in the browser).

The working instructions are in `SKILL.md`.
