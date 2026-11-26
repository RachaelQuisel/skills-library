# AYMG: Parse the 513 Multi-Item Contracts into Contract Line Items

## Scope (confirmed)
- **Only the 513 Contracts** whose `Line Items` field contains multiple items (string contains `), `).
- **Do not touch existing Contract Line Item records.** Leave them as-is.
- For each of these 513 Contracts, add *additional* Contract Line Item records — one per *extra* parsed piece (pieces 2..N).
- Leave the other ~14,834 single-item Contracts alone.
- Leave the broken `Line Item 1` formula on Contracts alone (out of scope).

## Problem Recap
`Line Items` (`fldExample0000218` on Contracts `tblExample0000219`) holds strings like:
```
Quarter Page Power Package (Print) ($335.00), Standard Square Ad - AY 300x250 ($0.00)
```
For these 513 Contracts, only one Contract Line Item record currently exists, but there are 2+ items in the string. Fix: create the missing ones.

## Fix Approach
One-time backfill script via the Airtable API. For each of the 513 Contracts:
1. Parse `Line Items` on `"), "` and re-append `)` to all pieces except the last. Call the result `pieces`.
2. If `len(pieces) <= 1`, skip (shouldn't happen given the filter, but defensive).
3. For pieces **index 1 through N-1** (i.e. skip piece 0 — the existing Contract Line Item is considered to "cover" the first piece, even though its text is a record ID):
   - Create a new Contract Line Item record with:
     - `Line Item 1` (`fldExample0000220`) = parsed text
     - `Contracts` (`fldExample0000221`) = [Contract record ID]
4. Do NOT delete or modify any existing Contract Line Item record.

Batched per Airtable limits (10 records/request, 5 req/sec).

## Assumptions (flag if wrong)
- "Leave existing Contract Line Items alone" means: skip piece 0 and only create records for pieces 1..N-1. The existing record stays untouched even though its `Line Item 1` text holds a record ID rather than the first parsed piece.
- Target field for new records: `Line Item 1` (`fldExample0000220`).
- No other `Line Items` formats beyond `... ($price), ...`.

## Steps
- [ ] Write Python script `backfill_multi_item_contracts.py` using PAT from memory
- [ ] Dry-run mode first: print what would be created for 5 sample Contracts, no writes
- [ ] Run dry-run, review output, spot-check `recExample0000222` shows 1 new record for the 2nd piece
- [ ] Run for real against all 513 (with progress log + error log)
- [ ] Verification:
  - [ ] `recExample0000222` now has 2 linked Contract Line Item records total (1 original + 1 new)
  - [ ] New record's `Line Item 1` text = `"Standard Square Ad - AY 300x250 ($0.00)"`
  - [ ] Random 3 other multi-item Contracts show expected total count + text
  - [ ] Original Contract Line Item records for these 513 are unchanged

## Review
(To be completed after execution)
