# Update Automation Catalog

Status checked October 12, 2026: Enabled schedule verified. A complete catalog refresh has not been verified.

Category: Reporting
Workflow type: Documentation updates
Tools: ChatGPT, GitHub, Airtable, Google Drive, Slack.
Runs: Cloud schedule verified.
Tags: #reporting #documentation-updates #chatgpt #github #airtable #google-drive #slack #cloud-verified
Identity: ChatGPT task 6acb928d16bc8191ae1716cfe40da199.
Source: The current task definition, read October 12, 2026. The saved definition is in [settings.json](settings.json). The fallback [Automation Catalog skill](https://github.com/RachaelQuisel/Skills/blob/780d1e3a21bcc3bf2e930f31417824ebf23c5fa6/plugins/automation-catalog/skills/automation-catalog/SKILL.md) is pinned to a specific revision.

## Trigger

- The cloud task starts each Monday at 5 AM America/Los_Angeles, beginning October 12, 2026.
- It does not depend on Rachael's computer being awake.

## Inputs

- Read accessible workflow definitions, scheduled tasks, GitHub code, Airtable automations, Google Drive project documents and Slack references.
- Read the installed Automation Catalog, /auto and /voice-align instructions. Use the pinned fallback when the catalog skill is unavailable.
- Read the occurrence's messages and all replies in La Maison #automations, channel C0EXAMPLE01 in workspace T0AT819U2UQ.
- Read existing guides, document homes, source identifiers, publication receipts and each business's approved Slack destination.

## What happens

1. Use the scheduled Monday's date in ACATALOG:YYYY-MM-DD. If a verified COMPLETE, PARTIAL or FAILED report exists, return its link without running again. If another worker may be active, report the blocker.
2. Read the largest recorded attempt count. Before starting an attempt, save ATTEMPT n/5 in the status thread and read it back. Stop if the count cannot be read or recorded. Never exceed five total attempts for the occurrence.
3. Search all accessible businesses, client projects and personal projects. Read every relevant result page. Record denied, unavailable, unread and cut-short sources.
4. Match workflows by business, provider and stable identifier. For code, use the repository and entry point. Keep plans, reviewed code, enabled schedules and observed runs separate.
5. Apply /auto to each distinct workflow. Write Trigger, Inputs, What happens and Outputs in plain English. Add category, workflow type, tool and run tags.
6. Update existing current guides and related documents. Append to existing running updates. Skip unchanged content. Keep each business's private details in its own project.
7. Reuse La Maison's index thread 1791723995.673909 and its guide messages. For other businesses, verify the document home, workspace, channel and audience. Hold unclear Slack writes and continue other work.
8. Keep write receipts. If a write times out, check its destination before retrying. Resume only unfinished work. Retry only problems that may clear. Stop early for denied access, missing authorization or unclear destinations.
9. Post a final COMPLETE, PARTIAL or FAILED report in the occurrence's thread. Include attempts used, counts found, documented, saved, posted and unchanged, search gaps, evidence-based failure reasons, blockers, one next step and safe verified links. Use PARTIAL only when useful work was saved but gaps remain.
10. Read back the final report. If Slack delivery fails, return the full report in ChatGPT and state that it was not delivered. Keep the weekly task active after a failed occurrence.
11. Change documentation only. Do not run, repair, enable, pay through or reschedule discovered workflows. Do not merge pull requests.

## Outputs

- Updated guides, categories, tags and related project documentation are saved in verified project homes.
- Approved Slack guides and their index are updated only where needed.
- The occurrence's status thread receives a final report, including when nothing changed.
- The overall La Maison report contains safe counts and blockers. It contains no other client's private workflow content.
- The October 11 manual test used ACATALOG-MANUAL:2026-10-11 and a separate attempt budget. It does not consume a Monday occurrence's budget.
