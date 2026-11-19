---
name: post-to-huddle
version: 1.0.1
description: >
  Post a message to the correct XRAY client huddle channel in Slack. Use this skill any time a summary, report, or update needs to be shared in a client's Slack huddle channel. Trigger on: "post to Slack", "send to the huddle", "share this in Slack", "post the summary", "send to huddle channel", or any request to deliver content to a client's Slack channel. Always show the message and confirm before posting. No tags.
tags:
  - skill
---

# Post to Huddle

## Purpose in plain English

This skill helps you send an approved client update to the correct XRAY Slack channel.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Post a message to the correct client huddle channel in Slack. Always confirm before sending.

---

## Reference Data

| Client            | Channel                    | Channel ID   |
|-------------------|----------------------------|--------------|
| Coding Clarified  | #huddle_coding-clarified   | C0AGHQ4E7D5  |
| AY Media          | #huddle_aymedia            | C09S4B9ANR2  |
| Guardians of Love | #huddle_guardians_of_love  | C0B0BPCRVL0  |
| CCRES             | #huddle_ccres              | C09CZ718GFJ  |

⚠️ The hyphen in `huddle_coding-clarified` is intentional — do not change it to an underscore. Note also that GoL's channel uses underscores throughout (`huddle_guardians_of_love`) — not hyphens.

---

## Inputs Required

- Client name (determines which channel to post to)
- Message content (formatted text, from build-sprint-summary or equivalent)

---

## Step 1 — Format for Slack

Convert the summary to Slack mrkdwn format:

```
*Sprint Summary: [Start] – [End] | [Client]*

🔄 *In Progress ([N] — [N] at risk):*
⚠️ [Task] · [Project] — OVERDUE
• [Task] · [Project]

✅ *Completed ([N]):*
• [Task] · [Project]

📋 *Carried ([N]):*
• [Task]

📊 Velocity: *[N] tasks* | Completion rate: *[N]%*
```

**Rules:**
- No user tags
- Keep under 40 lines
- If any bucket exceeds 5 tasks, show top 5 and add "...and [N] more"
- Use `*bold*` not `**bold**`

---

## Step 2 — Confirm Before Posting

Show the user the formatted message and the target channel name. Ask: *"Ready to post this to [#channel-name]?"*

Only post after explicit confirmation.

---

## Step 3 — Post

Send to the correct channel ID using the Slack tool. Return the message link.
