# Disambiguation Rules — Auto-correct vs. Flag

The core decision in any normalization is: **does the script change this cell, or does it flag it for a human?**

Default to flagging. Auto-correct only patterns where the intended value is unambiguous from the malformed input.

## Auto-correct (log every change to `changes.csv`)

These are patterns where the typo could only have meant one thing.

| Pattern | Example input | Auto-corrected to | Why it's safe |
|---|---|---|---|
| Double slash in a date | `2//24/26` | `2/24/26` (then year-expanded to `2026-02-24`) | A double slash has no other meaning; collapse runs of slashes to one |
| 2-digit year in a date | `5/20/19` | `5/20/2019` | Python convention: 00-69 → 2000s, 70-99 → 1900s. Document the assumption |
| Whitespace stripped from date strings | `' 5/20/2019 '` | `5/20/2019` | Whitespace can't be meaningful in a date |

Note: this is intentionally a *short list*. Resist adding more.

## Flag for review (set `Status = 'needs client review'`, preserve raw value)

These are patterns where the script *cannot* infer the right answer.

| Pattern | Example | Flag message | Why not auto-correct |
|---|---|---|---|
| Out-of-range date | `4/30/2036` | `date out of expected range (2036-04-30)` | Could be 2026, 2036, or any other year — direction ambiguous |
| Unparseable date | `'i\nd\ne\nr\nr\n'`, `'florinda'`, `'inhome'`, `'44403'` | `date unparseable: ...` | Either gibberish or a non-date value typed in a date column |
| Lookup value not in expected set | Agency = `'PENNYLANE'` when expected set is `{GOL, DIUP}` | `lookup value not in expected set: 'PENNYLANE'` | Could be a real new value or a typo of an existing one — let the client decide |
| Lookup value is a delivery mode, not a person | Trainer = `'Outside'` or `'Online'` | `lookup is delivery mode, not a person` | Schema decision (add Delivery Mode field? leave blank?) belongs to the client |
| Calendar-invalid date | `5/59/2021` (day = 59) | `date invalid calendar value` | Could be `5/9` or `5/19` or `5/29` — no way to tell |
| Stray multi-line content | A cell containing a newline | `cell contains newline; needs cleanup` | Likely a paste error; preserve so a human can recover original intent |
| Apparent in-file duplicate | Same person twice in one source file | `apparent duplicate of row X` | Could be legitimate re-training or data entry duplicate |

## Preserve verbatim (do NOT touch)

These should never be modified by the script unless the user explicitly says otherwise.

| Field type | Why |
|---|---|
| Name fields (Last, First, Full Name) | Trimming, encoding-repair, or compound-surname splitting destroys information. `Maga�a` stays `Maga�a`; `Bryant ` keeps its trailing space; `(Co-App to Cynthia Romero)` stays in First Name. A human can decide later. |
| Free-text notes | Same logic |
| Raw lookup values | Always emit a `(raw)` column alongside the `(normalized)` one — never just replace the raw |

## Rationale (so future Claude knows when to deviate)

- **Auto-correcting saves the user time on rules they already agree with.** Double slashes are clearly typos. There's no judgment call.
- **Flagging defers judgment to the right person.** The user (or their client) knows the domain — Claude doesn't. If you auto-correct ambiguously, you introduce silent errors that compound and are hard to undo.
- **Preserve raw values alongside normalized ones**, because the raw is the only ground truth. Any normalization is a hypothesis; the raw is data.
- **The 3-output design (all_events.csv with Status + changes.csv)** means every row is in one place, every change is auditable, and nothing is hidden from the client.

## Anti-patterns spotted in the wild (do not repeat)

- Adding Excel serial date conversion (`44403` → `2021-08-24`) when only one row uses it. Cost > value.
- Adding `.title()` on names "to normalize them" when the user said preserve verbatim.
- Splitting outputs into normalized.csv + review.csv when one CSV + Status column is simpler for the client.
- Building fuzzy-matching to existing Airtable records inside Python when Airtable's UI does it natively.
- Adding `argparse`, type hints, or tests to a one-off migration script.
- Restructuring the script silently without first showing the template.
