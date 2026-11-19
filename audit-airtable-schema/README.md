# audit-airtable-schema

Audit the complete schema of an Airtable base — every table, every field — and map the dependencies and logic spread across the system. Use this skill whenever the user asks to document, audit, review, map, or understand the data structure of an Airtable base, including questions like "what tables exist in this base?", "what fields are in X?", "how do these tables connect?", "what formulas reference Field Y?", "draw me an ERD", "what does this base look like?", or "where is the logic hidden?". The skill produces a single markdown audit document with: a Mermaid ERD showing every linked-record relationship, per-table sections covering every field (type, description, formula text, cross-table references), a cross-table dependency map (rollups, lookups, formula references), and AI-drafted descriptions for fields that don't have one in Airtable. Requires the Airtable MCP.

The working instructions are in `SKILL.md`.
