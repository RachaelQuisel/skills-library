---
name: humanizing
version: 1.0.2
description: Draft or rewrite human-facing messages in Rachael Quisel's personal voice. Use for emails, Slack messages, texts, client communications, and public posts when the user says "humanize this," "make it sound like me," "in my voice," or otherwise asks for Rachael's tone. Do not use for process or automation explanations whose main need is plain-English clarity; use voice-align for those. When the user explicitly invokes both skills, keep every voice-align constraint.
---

# Humanizing

## Purpose in plain English

This skill helps you draft or revise messages in Rachael Quisel's personal voice.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Make the writing sound like Rachael. Keep it direct, warm, specific, and natural.

## Follow this order

1. Follow the user's current instructions.
2. Preserve every material fact from the source.
3. Apply the rules in this file.
4. Use recurring patterns from the reference samples.
5. Treat an individual sample as supporting evidence only.

Do not claim that authorship proves a current preference. A sent message proves a writing choice. It does not prove that Rachael still likes that choice.

## Draft the message

- Identify the reader and the relationship.
- Identify what Rachael needs the reader to know or do.
- Start with the first useful point.
- Write in first person when Rachael will send the message.
- Use contractions.
- Use concrete details.
- Keep warmth brief and specific.
- Ask direct questions.
- Keep uncertainty when it changes the meaning.
- Use technical terms the reader already knows.
- Explain unfamiliar terms in plain English.
- End after the request or final useful fact.

Do not add humor, enthusiasm, or casual language without support from the source or relationship.

## Keep the writing natural

- Prefer short paragraphs.
- Use a fragment only when it sounds intentional and remains clear.
- Use parenthetical comments sparingly.
- Use semicolons only when they improve the sentence.
- Do not use em dashes.
- Do not use quotation marks, bold, or italics for emphasis.
- Do not add emojis unless the user asks for them.
- Do not repeat a point for emphasis unless the user asks to preserve expressive repetition.

Remove a trailing clause when it only explains what the reader can already infer.

## Avoid generic language

Remove openings such as:

- "I wanted to reach out..."
- "I just wanted to provide an update..."
- "I hope this message finds you well."

Avoid corporate filler such as "utilize," "leverage," "facilitate," and "streamline."

Remove empty confidence claims. State the evidence or the uncertainty instead.

Do not use absolute terms such as "always" or "never" unless they are factually required.

## Match the channel

### Email

- Use names or no greeting. Do not open with "Hi team."
- Lead with what was delivered, decided, or learned.
- State what Rachael needs from the reader.
- Ask the next question.
- Put billing or administrative details at the end.
- Do not use headers unless the message is too long to scan without them.
- Use "All best,\nRachael" only when an email needs a sign-off.

### Chat or text

- Skip the email sign-off.
- Keep the message short enough for the channel.
- Use casual language only when it fits the relationship.

### Public post

- Lead with a concrete point.
- Use examples or numbers when they add evidence.
- End with the requested action.

## Use writing evidence carefully

Load references only when the task needs more tone calibration:

- Read [references/voice-samples.md](references/voice-samples.md) for a long or difficult message.
- Read [references/voice-example-internal-team-ask.md](references/voice-example-internal-team-ask.md) for an internal request for feedback.
- Read [references/voice-example-consultant-role-limit.md](references/voice-example-consultant-role-limit.md) for a client email that names a consultant-role limit directly in first person while keeping the door open to pushback.

Keep quoted samples verbatim. Do not copy private names, facts, figures, or client details into new writing.

Use a pattern only when it appears more than once or Rachael has confirmed it directly.

## Route related requests

- Use `voice-align` for plain English, concision, reviews, and automation or process explanations.
- Use `rachael-work-voice` for a difficult boundary, redirect, or work preference.
- Use `xray-team-voice-shifter-local` for the shared XRAY team voice.
- Use `humanizing` for Rachael's general personal voice.

Do not combine voice skills automatically. Use both only when the user explicitly invokes both.

When `voice-align` and `humanizing` are both active:

1. Apply `voice-align` first.
2. Add only first person, contractions, brief warmth, and direct questions.
3. Do not override a `voice-align` rule.

## Final check

- Confirm that the meaning is unchanged.
- Confirm that the message fits the reader and channel.
- Confirm that each point appears once.
- Confirm that no sample fact leaked into the draft.
- Return only the requested writing.
