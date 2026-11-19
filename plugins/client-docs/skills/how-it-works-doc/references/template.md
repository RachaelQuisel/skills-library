# HOW-IT-WORKS Template

Copy this into a new file named `HOW-IT-WORKS-<automation-slug>.md`. Fill in every section that applies; delete the ones that do not. Replace the placeholder text in angle brackets.

---

# How the <Automation Name> Works

A plain-English guide to <one-line description of what this is>.

**Audience:** <who this is written for, daily operator, client owner, engineer, all three>
**Status:** <built and live | built but not yet deployed | design only, blocked on X>
**Where the code lives:** <path on disk, or the Airtable / Make / Zapier location>

## What it does, in one sentence

<One sentence. Active voice. Plain English. Describe the actual effect, not the abstract purpose.>

## What sets it off (the trigger)

<What event, schedule, or human action makes the automation run. If there is more than one trigger, list them.>

## What it needs to do its job (the inputs)

- <Field or record the automation reads> (<source table or system>)
- <Field or record the automation reads> (<source table or system>)
- <Credentials, if relevant, name them, do not paste them>

## What it produces (the outputs)

On the <target table or system>:

- <Field that gets populated or changed>
- <Field that gets populated or changed>
- <Record that gets created or updated>

## Step by step, when the trigger fires

1. **<Actor>** does <action>.
2. **<Actor>** does <action>.
3. **<Actor>** does <action>.
4. **<Actor>** does <action>.

(One sentence per step. Bold the actor when more than one system is involved.)

## What this automation does not do

- It does not <thing a reader might reasonably assume it does>, that is handled by <where>.
- It does not <thing a reader might reasonably assume it does>, that is handled by <where>.
- It does not retry on its own. If it fails, <what happens next>.

## When to expect it to fire

<Once per X. Daily at 8 AM Pacific. Every time someone signs a contract. State the cadence in plain English.>

---

## Optional sections: keep when the automation is complex enough

## Quick read (for the daily operator)

### The one thing you do

<One sentence. What the operator's job actually is during the normal path.>

### What you see

1. <What appears in the system at step one, from the operator's point of view>
2. <What appears at step two>
3. <What appears at step three>

### What success looks like

| Indicator | Value |
|---|---|
| <Field name> | <Value that means it worked> |
| <Field name> | <Value that means it worked> |

### What review-needed looks like

| Indicator | What it means |
|---|---|
| <Field name = some value> | <What the operator should do about it> |
| <Field name = some value> | <What the operator should do about it> |

## Gates and guards

The automation stops without running when:

- <Condition that halts it, and what shows up so someone notices>
- <Condition that halts it, and what shows up so someone notices>

The automation refuses to overwrite:

- <Field or row state it will never touch, and why>

## Failure modes

| What breaks | What it looks like | Who notices first |
|---|---|---|
| <Failure> | <Symptom, what field, record, or message the operator sees> | <Person or system> |
| <Failure> | <Symptom> | <Person or system> |

## Files and locations

- **Code:** <path>
- **README:** <path>
- **Post-run analysis (most recent):** <path>
- **Design doc:** <path>
- **Schema dependencies:** <path>

## Why it was built this way

<One short paragraph. The trade-off the architect made and why. What was rejected and why. This section is for the engineer, not the operator, keep it short.>

## Open items

- <Decision pending, with who is blocking and what the decision is>
- <Decision pending>
- <Future build that depends on this one>
