---
name: make-it-sound-human
version: 1.0.1
description: Turn a technical report, data check, audit, comparison, or assistant-generated summary into a friendly, client-facing XRAY-branded PDF that reads like Rachael wrote it. The reader dislikes technology and reads at about an 8th-grade level. Use this whenever Rachael pastes a report and wants it "for the client," "in plain English," "for someone non-technical," "client-facing," "in my voice," or "to sound human." Examples include an Instinct check, an Airtable or Acuity comparison, a reconciliation, or a status report. Use it even if she does not say PDF or name this skill.
---

# Make it sound human

## Who reads the result

- The reader is a client who dislikes technology.
- The reader reads at about an 8th-grade level.
- The reader cannot fill in missing steps or make inferences.
- The reader still needs every real detail.

## What the result does

- It reads like a warm note from Rachael.
- It shares information.
- It gives the client no tasks.
- It says nothing about how the work was done.
- It claims no more certainty than the facts support.

## Steps

1. **Pull out the facts.** List only what the reader needs:
    - Every item compared, with names, full dates, times, and the group or class.
    - The count for each group, from both sources.
    - Every difference, with the exact value from each source.
    - Possible duplicates.
    - Look-alikes that are probably two different people, such as two people with the same name and different phone numbers.
    - Anything left off on purpose, with the reason.
    - What the report does not cover, such as attendance or which value is correct.
2. **Drop the process.** Remove tools, assistants, agents, "Instinct," booking IDs, reading order, time spent, and confidence math. The client does not know that this work happened.
3. **Ask Rachael short questions.** Ask about test entries, staff entries, or placeholders when it is unclear whether to leave them off. Ask no more than two questions. If she says to go ahead, use the most sensible reading. Mention that reading in your reply to her, not in the document.
4. **List what was left off.**
    - Use a table with these columns: Name, Where it was, How many, Why I left it off.
    - Write each reason as a short, plain sentence.
    - Example: "These are the Zoom seed sign-ups that set up each class. They aren't people taking the class."
    - Write about known entries with confidence. Known entries include test sign-ups, Zoom seeds, and staff such as Casey. Rachael and the client both know what they are.
    - State the new total.
    - State that nothing was changed or deleted in the original systems.
    - Recount every total after the removals.
5. **Write the text.** Apply the `voice-align` skill first. Then apply the `humanizing` skill. If either skill is unavailable, follow these rules directly:
    - Write in first person: "I compared," "I left these off."
    - Lead with the good news when there is some.
    - Put one idea in each sentence.
    - Use common words.
    - Spell out dates and times, such as "Tuesday, October 13" and "5:30 in the evening."
    - Use no shortened terms except product names, such as Acuity, Zoom, and Airtable.
    - Use no jargon, metaphors, em dashes, all caps, or emojis.
    - Avoid "always," "never," "ensure," "utilize," "resume," "clean," "master," and "needs fixing."
    - Avoid adverbs that end in "ly," such as "ideally" and "differently."
    - Name each system the way the reader knows it. For example, write "the sign-in sheet," not "Airtable," when the reader looks at the sign-in sheet.
    - Explain each system in one plain sentence the first time it appears.
6. **Share information only.**
    - Leave out "please," "call," "check," "fix," "ask," "make sure," and "before you delete."
    - Turn each instruction into a fact.
    - Example: Write "6 people have a different phone number on the two lists," not "Call these 6 people."
    - Example: Write "Some of these might be on purpose, so I left them as they are," not "Check with each person before deleting."
7. **Leave room for being wrong.**
    - Soften only open questions, such as which phone number is right or whether two sign-ups are the same person.
    - Use phrases such as "As far as I can tell," "It looks like," "I believe," "might be," and "I could be wrong."
    - Offer kind reasons for a difference, such as a new phone number or a family member's phone.
    - Add one line that welcomes corrections, such as "I may have missed something, and I'm happy to take another look."
    - Do not soften raw values. A phone number stays exact.
    - Do not soften what Rachael and the client already know. Hedging there makes Rachael sound unsure about her own client.
8. **Lay out the page in this order.** Copy the styles and structure in `assets/example-class-signups.html`.
    1. Header: the XRAY logo (`assets/logo-xray.svg`) on the left. "For [client]" and "From Rachael Quisel, XRAY" on the right.
    2. A friendly title.
    3. An as-of line, such as "I compared the lists on..."
    4. A shaded box with the main finding and the line that welcomes corrections.
    5. One sentence that explains each source.
    6. A key: ✓ means the lists match. ✗ means the lists do not match.
    7. "At a glance": who has which kind of difference, in short two-column lists.
    8. The "Sign-ups I left off, and why" table.
    9. The count for each group, with both sources, a ✓ or ✗ column, and a total row.
    10. One small card for each person with a difference. Each card has rows for Phone and Email and columns for each source and "Same?" Shade the rows that do not match. Write "Same on both lists" when the values match. Write "No phone" or "No email" when a source is blank.
    11. Possible duplicates and look-alikes.
    12. "What this page doesn't show," as short list items.
    13. A friendly closing line and the sign-off "All best," then "Rachael" on the next line. Leave out her email address because the client already has it.
9. **Apply the brand.**
    - Use navy `#0E1C2D` for text, headings, and the header line.
    - Use green for ✓ and red for ✗.
    - Pair every color with its symbol so the page reads in black and white.
    - Use only the XRAY logo. Leave out partner logos.
10. **Build the PDF.**
    1. Write the page as one HTML file in a working folder.
    2. Run `python scripts/render.py <page.html> <name>.pdf`. The script copies the logo, builds the PDF, and saves page previews.
11. **Look at the previews.**
    - Confirm that the logo shows.
    - Confirm that nothing is cut off.
    - Confirm that no card splits across two pages.
    - Confirm that the totals match.
    - Search the text for "please," "we," "always," "never," em dashes, and any mention of tools or assistants.
12. **Send the PDF.**
    - In the reply to Rachael, state what changed and what you assumed in one or two sentences.
    - Keep notes for Rachael out of the document.
    - When Rachael asks for edits, change only what she asked. Then build the PDF again.
