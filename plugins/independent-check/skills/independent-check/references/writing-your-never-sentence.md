# Writing your never sentence

The never sentence is one sentence. It is the one unacceptable outcome that fails the check at any average score. It is not a list. If you have three nevers, the job needs three independent gates.

## Shape

> This job must never **<verb>** **<specific unacceptable outcome>**.

Not:

> This job must never make mistakes.
> This job must never break things.
> This job must never do anything wrong.

Those are moods, not gates. A machine cannot tell whether an outcome is "wrong" without a concrete rule.

## Good examples

- "This job must never send pricing or dates that are not in the customer's own record."
- "This job must never book a customer onto a class that has already started."
- "This job must never archive a case before the 90-day retention window closes."
- "This job must never send a message that contains the word `CONFIDENTIAL:` to anyone outside the project's shared Slack."

Each one names a verb, a specific condition, and a source of truth that lives outside the maker.

## Three questions the sentence has to answer

1. What is the verb? (`send`, `archive`, `publish`, `post`, `charge`, `book`, `delete`.)
2. What is the specific unacceptable thing? (A dollar amount, a date, a status transition, a phrase, a name.)
3. Against what standard? (The customer record, the price list, the calendar, the retention table.) If the sentence does not name a standard outside the maker, go back and find one.

## How to turn a never sentence into an assertion

| Verb in the sentence | Assertion kind to reach for |
| --- | --- |
| "send pricing that is not in the record" | `all-currency-in-standard` with `gate: true` |
| "send dates that are not in the record" | `all-dates-in-standard` with `gate: true` |
| "mention another customer's job" | `mentions-only-named-job` with `gate: true` |
| "contain `CONFIDENTIAL:` in an outside message" | `forbidden-phrases` with `gate: true` |
| "omit the agreed scope" | `required-phrases` (not usually a gate; it is a quality miss) |

If none of the shipped assertion kinds fits, say so to the user. Add a new assertion kind in a fork rather than mapping a loose kind onto a specific gate.

## The share-out line (from the workshop)

Write it in one line so the user can read it out loud:

> "My job is ___. It must never ___. When it tries, ___ gets it within ___."

If the sentence cannot be read in one breath, it is probably two nevers. Split them.
