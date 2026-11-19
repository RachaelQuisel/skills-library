---
name: app-content
description: Automate the weekly video content review workflow in Notion. Connects to a Notion video database, identifies unprocessed videos (missing category and date stamp), categorizes them, applies tags, and date-stamps them. Use this skill any time the user wants to review, categorize, or tag videos in their Notion database. Trigger on "app content", "review videos", "categorize videos", "video review", "content review", "tag videos", "weekly video review", or any mention of processing new video entries, even if they don't say "video review" explicitly. If the user mentions Amy's video database or weekly content tasks, this is likely the right skill.
---

# App Content -- Weekly Video Review

This skill automates Rachael's weekly video content review workflow. It connects to a Notion video database, finds new/unprocessed videos, categorizes them, tags them, date-stamps them, and writes everything back to Notion without a confirmation step.

---

## Configurable Category List

Update this list when new categories are needed. This is the single source of truth for valid categories. Each video gets exactly one.

```
CATEGORIES:
- Digital Health
- Safety
- Privacy
- Security
- News
- Updates
```

If a video does not clearly fit one of these categories, assign it **"Needs Review"** so Rachael can decide manually.

---

## Workflow

Follow these steps in order every time this skill triggers.

### Step 1: Connect to the Notion video database

Use the Notion MCP tools to find the database.

1. Call `notion-search` with the query **"Amy's Notion database"** to locate the database.
2. Once found, store the database ID for all subsequent calls.
3. Call `notion-fetch` on the database URL to confirm access and inspect the schema (list of properties and their types).

**If the database cannot be found:** Stop and tell the user. Do not guess or use a different database. Report the exact search query used so the user can troubleshoot.

### Step 2: Verify and create required fields

The database needs these properties. Check the schema from Step 1.

| Field Name  | Property Type | Notes |
|-------------|--------------|-------|
| Title       | Title        | Should already exist. This is the video name. |
| Description | Rich text    | Should already exist. Used for categorization context. |
| Category    | Select       | Create if missing. Populate select options with the categories listed above plus "Needs Review". |
| Tags        | Multi-select | Create if missing. Populate multi-select options with the categories listed above. |
| Date Stamp  | Date         | Create if missing. |

**To create a missing field:** Use `notion-update-page` or the appropriate Notion MCP tool to add the property to the database. If the Notion MCP tools do not support creating database properties directly, tell the user which fields need to be created manually and pause until they confirm the fields exist.

**If any expected existing field (Title, Description) is missing or named differently:** Stop and report which fields were found and which were expected. Do not write data to the wrong field. Ask the user to confirm the correct field names.

### Step 3: Pull all records and identify new videos

1. Call `notion-fetch` or the appropriate query tool to retrieve all records from the database.
2. Filter for the **working set**: records where Category is empty/null AND Date Stamp is empty/null.
   - A record with an existing Category value is considered already processed -- skip it entirely.
   - A record with an existing Date Stamp but no Category is ambiguous -- include it in the working set but flag it in the summary as "previously date-stamped but uncategorized."
3. If the working set is empty, report "No new videos to process" and stop.

### Step 4: Categorize each video

For each video in the working set:

1. Read the **Title** and **Description** (if available).
2. Match against the category list using these guidelines:

   - **Digital Health** -- Topics about health technology, telemedicine, health apps, wearable health devices, electronic health records, digital therapeutics, health data.
   - **Safety** -- Topics about physical safety, child safety, product safety, workplace safety, safety regulations, accident prevention.
   - **Privacy** -- Topics about data privacy, personal information protection, privacy laws/regulations (GDPR, CCPA), surveillance, tracking, consent.
   - **Security** -- Topics about cybersecurity, network security, encryption, hacking, breaches, authentication, threat detection, security tools.
   - **News** -- General news coverage, current events, industry news roundups, breaking developments.
   - **Updates** -- Product updates, software releases, company announcements, changelog-style content, feature launches.

3. Assign exactly one category. Pick the **strongest match** based on the title and description.
4. If two categories are a close call (the second-best category is nearly as strong a fit), note both in the summary output so Rachael can override.
5. If the title is vague and the description is missing or unhelpful, assign **"Needs Review"** and note that the title was too vague to categorize confidently.

**Important:** Never overwrite an existing Category value. Only fill in blanks.

### Step 5: Apply tags

For each video in the working set:

1. Set the **Tags** multi-select field to the assigned category value (e.g., if Category is "Privacy", Tags gets ["Privacy"]).
2. If the video was assigned "Needs Review", leave Tags empty -- do not tag it until Rachael decides.

### Step 6: Date stamp each video

For each video in the working set:

1. Set the **Date Stamp** field to today's date in YYYY-MM-DD format.
2. This marks the video as processed. The date should reflect the review date, not the video's upload or creation date.

### Step 7: Write updates to Notion

For each video in the working set, update the Notion record with the assigned Category, Tags, and Date Stamp in a single update call per record using the Notion MCP `notion-update-page` tool.

- Do NOT ask for confirmation before writing. Speed matters here.
- Do NOT batch records if the MCP tool requires individual updates -- update them one at a time.
- If an update fails for a specific record, log the failure (record title + error) and continue processing the remaining records. Report all failures in the summary.

### Step 8: Report results

After all updates are complete, present a summary to Rachael in this format:

```
VIDEO REVIEW SUMMARY -- [today's date]

Processed: [count] videos
Categorized: [count]
Flagged as Needs Review: [count]
Errors: [count] (if any)

CATEGORY BREAKDOWN:
- Digital Health: [count]
- Safety: [count]
- Privacy: [count]
- Security: [count]
- News: [count]
- Updates: [count]

NEEDS REVIEW ([count]):
- [Video Title 1] -- Reason: [why it couldn't be categorized]
- [Video Title 2] -- Reason: [why it couldn't be categorized]

CLOSE CALLS:
- [Video Title] -- Assigned: [Category], Runner-up: [Category]. Rationale: [brief explanation]

ERRORS (if any):
- [Video Title] -- [error description]
```

Omit any section that has zero items (e.g., skip CLOSE CALLS if there were none). No emojis in the output.

---

## Error Handling

- **Database not found:** Report the search query and stop. Do not guess.
- **Field not found:** Report which fields exist vs. which were expected. Do not write to wrong fields.
- **Field creation fails:** Tell the user which fields need to be created manually.
- **Individual record update fails:** Log it, continue with remaining records, report all failures in the summary.
- **Notion API rate limiting:** If updates start failing due to rate limits, add a brief pause between calls and retry. If retries also fail, report which records were not updated.

---

## Constraints

- Never delete any records or data without Rachael's explicit approval.
- Never overwrite an existing Category -- only fill in blanks.
- Write directly to Notion without a confirmation step.
- Use "complete" not "clean" for data status language.
- Use "needs to be fixed" not "needs fixing."
- No emojis in outputs.
- Categorization is based on title and description metadata only -- there is no way to read actual video content.

---

## Future-Proofing Notes

- There is no "Reviewed" or "Status" field today. The skill infers "new" from missing Category + missing Date Stamp. If a status field is added later, update Step 3 to filter by status instead.
- The category list at the top of this file is the single source of truth. To add a new category, add it to the list above and update the keyword guidelines in Step 4.
- If the number of "Needs Review" videos trends upward week over week, that is a signal the category list may need to be expanded.

---

## Quality Checks (post-run)

After each run, Rachael should:
1. Spot-check 3-5 categorizations against the actual video content to verify accuracy.
2. Track how many videos land in "Needs Review" each week -- if trending up, expand the category list.
3. Confirm the Date Stamp matches the actual review date, not the video upload date.
