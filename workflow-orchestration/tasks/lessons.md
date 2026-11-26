# Lessons Learned

## 2026-04-22: Never Abbreviate "Contract Line Item" as CLI

**Problem:** I wrote the EMG parsing plan using "CLI" as shorthand for Contract Line Item. Rachael reads CLI as "command line interface" and had to stop me mid-plan.

**This is already in auto-memory** (`feedback_emg_no_cli_abbreviation.md`) — I failed to apply it.

**Prevention:**
1. At the start of any EMG work, scan the planned artifact for "CLI" before showing it to the user.
2. Applies to prose, tables, diagrams, file names, and code comments — not just chat messages.
3. Write "Contract Line Item" (or "Line Item" if context is obvious) in full. Never acronymize.

**Pair rule:** When working on EMG, re-read feedback memories before writing any plan or doc.

---

## 2024-02-16: Airtable CSV Import Pollutes SingleSelect Fields

**Problem:** When importing CSV data into Airtable, if a CSV column contains values that don't match existing singleSelect options, Airtable automatically ADDS those values as new options instead of rejecting them.

**Result:** Dollar amounts, random text, and garbage data became dropdown options in Ad Type, Production Status, Ad Size, and Guaranteed Position fields.

**Prevention:**
1. Clean CSV data BEFORE import - ensure values match exact dropdown options
2. Or: Import into text fields first, then convert to singleSelect after cleaning
3. Or: Create singleSelect fields AFTER import, mapping from text field

**Fix when it happens:**
1. Cannot modify singleSelect options via MCP API (only name/description)
2. Must delete polluted field entirely
3. Create new field with correct options
4. User deletes old field in Airtable UI
5. Rename new field to original name

**Time cost:** ~15 minutes to fix 4 fields
