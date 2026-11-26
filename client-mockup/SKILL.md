---
name: client-mockup
version: 1.2.0
description: Build a client-facing mock-up of a planned system as one scrolling web page, published as an Artifact. The page has a workflow diagram first (redrawn exactly from the client's Lucid chart export if there is one), then every planned screen stacked in process order as a non-clickable picture, with "new on [date]" tags that show which client feedback landed when, "proposed" tags for open questions, hover definitions for key terms, and the client's own brand colors on white. Also builds a short client-facing Next Steps page. Use whenever Rachael asks for a mock-up, mockup, wireframe, screen preview, "show the client what it will look like", "add this to the mock-up", "update the mock-up with...", "add the workflow to the mock-up", or shares a Lucid/Lucidchart export or a list of screens for a client build, even if she does not say "skill" or "artifact".
---

# Client mock-up

Build a mock-up a client can react to before anything is built: one page, the workflow first, then each planned screen in the order the process moves. It is a picture of a plan. Everything about it says "draft, for your feedback".

The reader is the client, usually not technical. Rachael is a consultant. If a page implies something is done, finished or complete when it is not, the client takes it as a promise. Every rule below follows from that.

## How to work with Rachael while doing this

These apply to every step, not just at the end.

- **Say what you are doing, without being asked.** At the start of each step, post one or two lines: the step you are on, what you just finished, and what you will build next. Rachael should never have to ask "what is taking so long" or "where is it".
- **Never fail silently.** If a file will not open, a source is missing, a check fails, a tool errors, or you had to skip something, say so right away in plain words, with what you will do about it. Do not quietly work around it and do not leave it out of the report.
- **Ask questions to get clarity.** Before building, ask about anything that would change what you build (see Step 1). Ask one or two focused questions at a time. Do not ask about things you can look up yourself (brand colors, field names, dates in transcripts).
- **Agree on the definition of done before you build.** Propose it in Step 0 and wait for Rachael to agree or change it. At the end, check each item and report which are met.

## Step 0: Agree on the definition of done

Propose a short checklist tailored to this request and ask Rachael to confirm. A typical one:

- The mock-up page is published at a link (the same link if it already exists), and Rachael has been told who can open it.
- It shows the workflow and the screens she asked for, with this round's changes tagged "new on [date]".
- It uses the client's brand colors on a white page.
- Wording says work in progress throughout, with no "done", "shipped", "every", or "all" claims.
- It has been checked in light mode, dark mode and at phone width, with screenshots.
- The Next Steps page is updated if it exists or was asked for.
- Anything from the sources that looks wrong (a chart error, a conflict between documents) has been reported to Rachael, not silently fixed.

Note: for a client build, "done" for the real system means the client has tested it (alpha and beta). The mock-up is only a draft for review. Never describe the mock-up as the build being done.

## Step 1: Gather the inputs

Find these yourself first. Ask Rachael only for what you cannot find.

| Input | Where to look | If missing |
|---|---|---|
| Client and build name | The request, the client folder `~/Claude-Work/CLIENTS/<CLIENT>/` | Ask |
| Workflow source | A Lucid JSON export, a screenshot, written steps, or nothing | See Step 2 |
| What each screen holds | Design doc, vision-and-scope, transcripts, meeting notes, the client's own notes (e.g. rubric notes) | Ask what the screen is for |
| Field names and choices | The live Airtable base schema (re-pull it; do not trust old docs) | Use plain labels and say so |
| Dated change requests | Meeting notes and transcripts in the client folder, with their dates. Also the Debrief Recordings table (base `appExample0000004`, table `tblExample0000011`; filter on the client's name in `XRay's Client`). It often has the full call transcript when the client folder does not. Read only; never write to that base. Note the time in the call for each change you use, so Rachael can check it. | Ask which meeting each change came from |
| Open questions | Meeting notes, "still deciding" lists | Ask |
| Key terms that need a definition | The request; words a student, counselor or staff member may not know | Propose a list |
| Client brand colors | A brand file in the client folder, else the client's own website (see Step 5) | Say you could not find them and ask |
| Existing page links | The request, earlier Artifact publishes, `Artifact` list | It is a new page |
| Next review meeting date | The request, calendar, notes | Leave the date out |

Two lookups are required, and each gets its own line in the report even when it finds nothing:
- **Meeting transcripts.** Check the client folder, Granola or Wispr Flow, and the Debrief Recordings table. Report "Transcript for [date]: found in [place]" or "not found in [places checked]". The tag key may say "from our [date] meeting" only when you read that meeting's transcript or notes. Otherwise say where the change came from ("from our November 19 notes"). The client will take "from our meeting" to mean we listened to them.
- **Real names.** See Step 3.

Gather from documents, the schema and saved screenshots. Do not open the client's live web apps (sign-in sheets, booking pages, Zite or Softr apps, Airtable interfaces) to copy their content. One stray click there changes real records.

Questions that usually need asking (one or two at a time):
- Which screens should this round include? (Never assume the mock-up shows every screen.)
- Is this page for the client, or internal? Default: client-facing.
- Should anything stay out of the client's view?
- Is there a Next Steps page to update, or should one be made?

## Step 2: The workflow diagram

The diagram comes first on the page. How you draw it depends on the source.

**A Lucid JSON export.** Run:

```
python3 -I ~/.claude/skills/client-mockup/scripts/lucid_outline.py /path/to/Chart.json
```

It prints every shape in process order with its exact text, every arrow with its label, the sticky notes, and a "Report to Rachael" list (missing arrows, unlabeled or oddly labeled decision lines, loops, typos). Redraw the diagram exactly: the same boxes, the same words, the same arrows and directions, the same sticky notes. Rachael has rejected a paraphrased version before ("I need to see the actual step by step diagram from Lucid chart please, not your interpretation of it"). The export has no positions, so lay it out from the arrows, left to right and top to bottom.

Fix only plain typos (and tell Rachael which ones, so she can fix them in Lucid too). Do not fix missing arrows, backward arrows or logic problems in the diagram. Draw them as exported, and report every item in the script's list to Rachael before publishing, because changing the logic changes her workflow.

**Another source** (screenshot, photo, written list, pasted text). Redraw it as faithfully as the source allows. Say in the report what you could not read.

**No source.** Draft the workflow from the transcripts and documents. Label it on the page as "Our draft of the workflow, for you to confirm", and show it to Rachael before publishing, because it is your interpretation. "No chart yet" means draft one, not leave the diagram out. The drawing must show every outcome the screens show: if a screen offers Attended, No show and Removed, the decision in the diagram has those three branches.

**When a client decision changes a step the chart still shows,** keep the chart's words in the box, give the box the highlight outline, and put a small "Changed [Mon D]" label on it, with one line under the diagram saying what changed. A note somewhere else on the page is not enough, because the client reads the old box first. Tell Rachael so she can update the chart.

Draw the diagram as inline SVG on the page: rectangles for steps, a diamond for a decision, arrow lines with labels, and text inside `foreignObject` so it wraps. Give it a minimum width and let it scroll sideways inside its own box on a phone. Never publish Mermaid or other diagram code to a client page. See `references/page-template.html` for the pattern.

## Step 3: The screens

Stack the screens in the order the process moves. Number them ("Screen 1 of 6"), where the count is the screens on this page, not a claim about the whole system.

For each screen:
- A fake browser bar on top with a web address and who sees it ("Example Client staff only", "signed in as..."). This tells the client at a glance whose screen it is.
- A one- or two-sentence note under the heading saying what happens on this screen.
- Realistic example content grounded in the client's world (their towns, schools, programs, real dollar ranges). Use made-up people, and say in the footer that names and figures are examples.
- Check every example name before you use it. Search for the first name and the last name separately in: the people records in the client's Airtable base (staff, applicants, contacts), the transcripts, and every file in the client folder (exports, notes, handoffs). Schema alone is not enough. Change any name that matches a real person, including a last name shared with a staff member or applicant. In the report, list each example name and where you searched. On an update, check the names already on the page too, not just new ones. For a staff screen, write "signed in as a Example Client reviewer" rather than a real staff member's name. A client who sees a real person's name on an example will think it is real data.
- Show only what is decided as the plan. If something is undecided, or a weak practice (a shared login, a manual workaround), it stays out of the screens or appears as conditional wording ("Asked only if...") with a "still deciding" tag and a Still open entry. This holds even when an internal document says it was agreed, because internal agreement is not the client's decision, and a weak practice shown as the plan makes XRAY look bad.
- Every factual claim on a screen ("Only Lesli can change attendance", "No link goes to the student") needs a source you read. If your sources disagree, show it as "still deciding" and report the conflict.
- Nothing clickable. Disable pointer events on the screens, and say in the banner that nothing is clickable. A page that clicks looks built.
- Fields carried over from an earlier step are shown dashed, with a label like "pre-filled by your counselor", so the client sees what flows where.
- A phone-shaped single column for any screen the public fills in on a phone.
- Status labels are neutral: words like "On hold" or "Waiting on student", in the template's one status style (square corners, grey outline). Never use the highlight color or the main color for a status, because those mean "new" and "still deciding", and a student's status must never read as an open question. Never color a person red or label them as failing.

## Step 4: Tags, definitions and open items

- **Dated tags.** Tag each new screen, field or change with "new on [Mon D]". Put a key near the top naming each date's source, e.g. "new on Nov 17: from your November 17 rubric notes". Give the newest date the highlight color and older dates a quieter style. Rachael likes this because the client can see their feedback being used. On a first draft everything is new, so put the date once (in the key and page heading) and tag only the items the client specifically asked for. Too many chips crowd a page meant to have few words.
- **Proposed tags.** Tag every undecided item "proposed", "still deciding" or "wording to confirm". Keep dates and proposed tags visually different, so a date never reads as a decision.
- **Decided lists.** A "Decided on [date]" list holds only what the client decided, in their words. Details you worked out from it (how students find the link, who gets the form first) stay tagged "still deciding". Email or message text keeps "wording to confirm" until the client approves the exact words, even when the words come from our own prep.
- **Still open list.** End with a short list of open questions in plain words.
- **Hover definitions.** Give key terms a dotted underline and a short definition that shows on hover or tap. Terms must opt back into pointer events, since the screens do not take clicks.

## Step 5: Colors: the client's brand, on white

Use the brand colors of the client the mock-up is for. Never use a default palette, and never tan-on-tan (beige or off-white page with tan panels). Rachael: "i hate the color scheme, no tan on tan. that is awful."

1. Look for a brand file in the client folder. If there is none, download the client's homepage and pull the hex colors it uses most (buttons, headers, highlights):
   ```
   curl -sL -A "Mozilla/5.0" -o /tmp/<scratch>/home.html https://<client-site>/
   grep -oiE '#[0-9a-f]{6}\b' /tmp/<scratch>/home.html | sort | uniq -c | sort -rn | head -25
   ```
   Check where the top colors are used before choosing. Say which colors you found and where.
2. Page and cards are white. Use the brand's main color for structure (banner, buttons, selected states, diagram boxes) and its accent color only for highlights (newest tag, items needing a decision, the next step).
3. Check text contrast. Brand colors are often too light for text on white. Darken the main color until white text on it, and it on white, reach at least 4.5 to 1. Keep the original shade for borders and large fills.
4. Define every color as a token on `:root`, with a dark-mode set, so the page works in both themes.

Known clients:
- Example Client (ccres.org): blue #40a1d0 (text and buttons #1e6f98), orange #e88a3d (orange text #9a4a12), navy text #1b2b3a.

## Step 6: Wording review

Run every sentence through these before publishing, including on an update: the whole mock-up and the whole Next Steps page, not just the sentences you added. Carried-over text reaches the client too. Details are in `references/review-checklist.md`.

- **Plain English (voice-align).** Short sentences, one idea each, common words, no jargon, no metaphors, no em dashes. Few words, diagrams first. Friendly and welcoming.
- **Work in progress, never done.** A banner at the top: "Work in progress. Nothing on this mock-up is final or clickable." The intro says these are some of the screens and they will change. No "done", "shipped", "complete", "ready", "every screen" or "all". Dates are goals.
- **No XRAY internals.** No table or field IDs, internal decisions, process notes, tool names or "the chart says". Internal material (design docs, plans, rubrics, meeting prep) stays in internal files.
- **No bias.** Neutral status words. No unsourced disability, ability or other personal labels on anything that feeds a score. Example people vary without stereotyping.
- **Nothing that makes XRAY look bad.** No typos. No weak practices shown as the plan (for example a shared admin login). No guessed causes.
- **Every statement has a source** (a transcript, a document, the schema). Anything unsourced becomes an open question.

## Step 7: Check it in a browser

Open the local file with Chrome DevTools and take screenshots before publishing:
- Light mode and dark mode.
- Desktop width and phone width. For phone width, use DevTools emulation with the viewport set to 420 by 900 pixels and mobile turned off. Resizing the window does not work, because Chrome will not shrink a window below 500 pixels. Mobile emulation does not work either, because the local file has no viewport tag, so the page renders 980 pixels wide.
- Run `document.documentElement.scrollWidth === clientWidth` at phone width. If the page scrolls sideways, fix it (usually `grid-template-columns: minmax(0,1fr)` on the wrapper and `min-width: 0` on grid children).
- Hover a definition and confirm it shows.

If a check fails or a tool will not run, say so and say what you did instead.

## Step 8: Publish

- Save the source to `~/Claude-Work/CLIENTS/<CLIENT>/Documents/mockup/<build>/<CLIENT>-Mockup-YYYY-MM-DD-<build>.html`.
- Publish with the Artifact tool. For an existing page, republish the same file path (or pass its URL) so the client keeps one link. Do not create a second page.
- Report who can open each page, as the publish result states it. You cannot change sharing. If a page the client needs is private, tell Rachael to use the page's Share menu.
- Do not post links to Slack, email or anywhere else unless Rachael asks. If she asks, word the post as a work in progress (see the checklist).

## Step 9: The Next Steps page

A short client-facing page in the same brand colors: a five-step timeline and tiles that link to screens in the mock-up (`<mock-up URL>#<screen-id>`). Start from `references/next-steps-template.html`. Head the tiles "Screens on this mock-up", not "What we plan to build", because the mock-up shows some of the screens and two tiles would read as the whole build. Every detail on the timeline (a date, "in person") needs a source.

- Mark the mock-up step "First draft, [date]" with a dashed outline, never as done.
- Highlight the next step (usually the review meeting) in the accent color.
- Label the launch date "Goal: [date]".
- The intro says the work is just starting and the plan may change.
- Save it to `~/Claude-Work/CLIENTS/<CLIENT>/Documents/build-plan/<build>/<CLIENT>-BuildPlan-YYYY-MM-DD-<build>-next-steps.html`.
- Leave out any section Rachael removes. Do not add a choices or decisions section unless asked.

## Step 10: Update the client documents

- Changelog (`Documents/changelog/<build>/changelog.md`): one line per change, marked **Drafted**, with "Not built." Never mark mock-up work **Shipped**.
- Vision-and-scope: if the mock-up conflicts with what the client already agreed, add a clearly marked "for <client> to confirm" section. Do not rewrite agreed text.
- Do not change the client's database for a mock-up. Building comes after the client reviews it, using the `create-plan` skill and the Seven Deliverables.

## Step 11: Report to Rachael

Keep it short. Include:
- The links, and who can open each one.
- What changed this round, as bullets.
- Each definition-of-done item and whether it is met.
- "Transcript for [date]: found in [place]" or "not found in [places checked]".
- Each example name and where you searched for it.
- Everything from the sources you drew as-is but think is wrong (chart errors, typos you fixed, conflicts between documents), so she can fix them at the source.
- Anything you skipped or could not check, and why.

## Decisions behind this design

| Decision | Why |
|---|---|
| One scrolling page, workflow first, screens in process order | The client reviews the whole flow top to bottom. |
| Exact redraw of the client's chart | A paraphrase is our interpretation and was rejected. |
| Inline SVG, not diagram code | Diagram code once showed up raw on a client page. SVG follows light and dark mode. |
| Non-clickable, with a banner | Clickable pages look built. |
| Dated tags plus a key | Shows the client their feedback landed, and when. |
| Separate proposed tags | Open questions stay visible and never read as decided. |
| Brand colors on white, darkened for text | Rachael's rule, and readable for everyone. |
| Neutral statuses, no personal labels in scoring | Avoids bias and stigma. |
| Same link on every update | The client keeps one bookmark. |
| Internal docs kept separate | The mock-up is external. |

## Files in this skill

- `scripts/lucid_outline.py`: turns a Lucid JSON export into an ordered outline and a list of problems to report.
- `references/page-template.html`: starting page with the color tokens, banner, tag key, diagram pattern, one screen, a phone screen, a definition, the open list and the footer. Copy it, then replace the brand tokens and content.
- `references/next-steps-template.html`: starting Next Steps page.
- `references/review-checklist.md`: the full pre-publish checklist, banned words, and a work-in-progress Slack post pattern.
