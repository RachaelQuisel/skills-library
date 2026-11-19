---
name: explain-automation
description: Turn an Airtable automation into a plain-English explainer and share it with the client. Reads the automation's real configuration, writes a no-jargon education doc in bullet points (trigger, inputs, steps in order, outputs, what happens when it fires), and posts it to the client's Slack huddle channel with a threaded reply carrying the direct automation links and a step-by-step breakdown. Use this whenever the user asks to explain an automation, educate the client on an automation, document what an automation does, write an automation explainer, post an automation explainer to Slack, or announce that an automation went live — even if they only say "tell the team what this does" or "write this up for Janine."
---

# Explain Automation

Turn one or more Airtable automations into a plain-English explainer the client's team can actually understand, then deliver it: as a Slack post to the client huddle channel, as text to slot into an email, or as a standalone education doc. Default to the Slack post with a threaded technical reply, since that is the pattern Rachael uses; produce the other formats when she asks.

Why this exists: clients do not read automation configs, and jargon-heavy summaries scare them off. A good explainer means fewer "what does this do?" support messages, staff who trust the system instead of fighting it, and no panic when a batch of records changes on the first run.

## Step 1 — Identify the automation(s)

Figure out which automation(s) to explain, in this order:

1. Ones already discussed in the conversation (most common: an automation just built or turned on).
2. Ones the user names — look them up with `list_automations` on the relevant base and match by name.
3. If it is still ambiguous, ask which automation before writing anything.

Default base: Coding Clarified (`appo7ppmZsn2ejonS`). Other clients: find the base with `search_bases`.

Then pull the real configuration with `get_automation`. Read the actual trigger, actions, condition logic, and which fields get written. Never write the explainer from memory or from the automation's name alone — the explainer's whole value is that it matches what the automation truly does, and configs drift.

## Step 2 — Write the plain-English explainer

One section per automation. Give each a plain-English nickname that says what it does (for example "the stale task alarm"), with the technical name kept for the thread reply. Every section covers, in bullets:

- What triggers it: a person's action or a clock. Name the exact thing ("someone checks the Leave of Absence box", "it wakes up every morning at 6am Pacific"). One sentence.
- What it looks at (the inputs): the fields and records it reads, in human words ("each task's status and the last time anyone touched it").
- The steps, in order: numbered, arrow-style, or short sentences — trigger fires → what it checks → what it decides → what it does. Include the "does nothing" branches ("if a task already exists, it stops there, so nobody gets doubled up").
- What comes out the other end (the outputs): exactly what is created or changed, and just as important, what is NOT touched ("nothing is deleted and no emails go out; it only changes the label").
- What the team does with it: the human's part of the loop, so the automation reads as a helper, not a mystery.
- Good to know: surprises worth defusing ahead of time. The big one: if a scheduled automation will process a backlog on its first run, say so plainly ("expect a batch of older tasks to move after tomorrow's 6am run — that's the system working, not a glitch").

### Language rules

This goes to non-technical client staff, in Rachael's voice:

- No jargon. Banned words: trigger record, webhook, API, field ID, base, workflow, config, deploy, sync, integration. Say checkbox, task, label, record, list instead. "Automation" itself is fine.
- Plain names for people ("Brittany and Janine"), never Slack @-tags.
- No em dashes; use commas or semicolons. No all caps. No adverbs ending in -ly. Avoid: ensure, utilize, leverage, streamline, robust, "always"/"never" as absolutes.
- No emojis unless the user asks.
- Complete sentences, warm and direct. Assume the reader is smart but has never opened an automation editor.

## Step 3 — Confirm before posting

Show the user the full formatted message and name the target channel. Wait for explicit confirmation before sending anything. Even when the user said "post it" up front, show the draft first; a wrong detail in a client channel is expensive to walk back.

Channel reference (the hyphen in the Coding Clarified channel is intentional):

| Client           | Channel                  | Channel ID  |
|------------------|--------------------------|-------------|
| Coding Clarified | #huddle_coding-clarified | C0AGHQ4E7D5 |
| AY Media         | #huddle_aymedia          | C09S4B9ANR2 |

## Step 4 — Post the main message

Send the explainer to the client channel as one message. Shape:

```
**Two new automations are live in your Airtable** — a quick explainer for the team:

**1. [Plain-English nickname]** ([when it runs, in a few words])
• Trigger: ...
• What it looks at: ...
• Steps: [a] → [b] → [c].
• Result: ... Nothing is deleted and no emails go out.
• Your part: ...

**2. [Next automation, same shape]**

[First-run expectations if any.] Questions, ping me here.
```

Adjust the opening line to the count ("A new automation is live..." for one). Keep the whole message under 40 lines; if explaining more than three automations, post the most important ones and offer the rest in thread.

## Step 5 — Reply in the thread with links and the technical breakdown

Post a threaded reply on the message just sent (use its `thread_ts`), carrying the direct link and a plain-text step-by-step breakdown for each automation. The main post is for the whole team; the thread is for the people who want to verify or maintain it. Shape:

```
Links and configuration for reference (you'll need base access to open these):

**[Nickname]:** https://airtable.com/[baseId]/[automationId]
```
```
Name:    [exact automation name]
Trigger: [exact trigger, including schedule and timezone]
Step 1:  [exact condition or action, with real field names and values]
Step 2:  ...
Writes:  [exactly which fields/records it creates or changes; note what it never touches]
```

The automation link is `https://airtable.com/<baseId>/<automationId>` (the automation ID starts with `wfl`). Mention that the links need base access, so front-line staff aren't confused by a permission wall.

Return both message links to the user when done.

## Other delivery formats

- Email bullets: same content, but drop the Slack bold markers and keep it paste-ready plain text. No headers, no sign-off; the user slots it into a drafted email.
- Education doc: same content as a standalone one-pager (PDF or Word on request). Title it after the automation's nickname and date it.
- When the user asks for one format, offer the others in one short line, no more.

## Example (real, shipped)

For a daily 6am scan that flips idle tasks, the main-post section read:

```
**1. The stale task alarm** (runs daily at 6:00am Pacific)
• Trigger: a clock, not a person. It wakes up every morning at 6am.
• What it looks at: each task's status and the last time anyone touched it.
• Steps: scans every task → finds any marked In Progress with no activity for 7+ days → changes them to Follow Up.
• Result: forgotten tasks stand out at the top of the queue. Nothing is deleted and no emails go out; it only changes the label.
• Your part: work the Follow Up items, then set them back to In Progress once there's movement. If it goes quiet another 7 days, the alarm catches it again.
```

And its thread breakdown:

```
Name:    Task 7-day idle → Follow Up
Trigger: Every day at 6:00am Pacific
Step 1:  Find tasks where Task Status = "In Progress"
         AND Last Modified is before 7 days ago
Step 2:  For each task found, set Task Status = "Follow Up"
Writes:  Task Status field only. No deletes, no emails.
```
