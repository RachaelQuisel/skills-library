# Automation catalog routines

| Routine | Time | Icon | Purpose |
| --- | --- | --- | --- |
| Automation Metadata Maker | Monday, 5 AM Pacific | [Sage catalog](../../plugins/automation-catalog/icon.png) | Find accessible automations and update their guides, tags and approved Slack messages. |
| Check Catalog Reports | Monday, 6 AM Pacific | [Mauve alert](../../plugins/automation-catalog-failure-check/icon.png) | Check for a final catalog report and report missing results or blockers. |

## Trigger

Both tasks use the ChatGPT cloud scheduler. They start on October 12, 2026. They do not depend on Rachael's computer being awake. The saved time zone is America/Los_Angeles.

## Inputs

The updater reads accessible workflow definitions, schedules, code, project documents and approved messages. Its fallback skill is pinned to commit 780d1e3a21bcc3bf2e930f31417824ebf23c5fa6 in this repository. The task prompt contains the five-attempt and reporting rules.

The report checker reads the updater's task status and the matching La Maison #automations thread. Exact task prompts, identifiers and schedules are in [settings.json](settings.json). This private deployment file is outside both plugin packages.

## What happens

1. The updater checks for an existing run before starting. It records each attempt. It stops after at most five total attempts for that weekly occurrence. It can stop sooner for missing access or an unclear destination.
2. It searches all accessible businesses and projects. It keeps each business's guides in its approved project and channel. It skips unchanged copies and resumes unfinished writes.
3. It reports COMPLETE, PARTIAL or FAILED in La Maison #automations. The overall report contains safe counts and blockers. It does not contain other clients' private workflow details.
4. At 6 AM, the checker looks for that report. It avoids duplicate alerts. It reports missing results, disabled tasks or an exceeded attempt limit. It never retries the catalog itself.
5. If Slack delivery fails, the task returns the report in ChatGPT. An outage affecting the shared scheduler or host can delay both tasks and their alerts.

## Outputs

The updater produces revised guides, categories, tags, delivery records and a final status report. The checker produces an alert only when action is needed.

Both task updates were confirmed by the scheduler on October 11, 2026. Their first scheduled deliveries have not yet been tested. The five-attempt limit is enforced through agent instructions and saved counts, not a hard scheduler setting.

The icons are declared in the Claude plugin manifests. The ChatGPT scheduler does not expose a custom-icon field. They are not attached to the scheduled-task cards.

## October 12, 2026 documentation review

- Added separate plain-English guides for [Automation Metadata Maker](UpdateCatalog-HowItWorks-2026-10-12.md) and [Check Catalog Reports](CheckReports-HowItWorks-2026-10-12.md). Each guide has category, workflow type, tool and run tags.
- Both task definitions were read and their enabled status was verified. This does not establish successful catalog completion or alert delivery.
- Today's catalog status and attempt history are recorded in the [approved status thread](https://example.slack.com/archives/C0EXAMPLE01/p1791806593148719).
- Search coverage remains incomplete after Airtable request timeouts and an unexpected tool-session closure. The cause of the closure is unknown. No discovered workflow was run or changed.
- No existing running-updates-and-questions.md was found in this deployment folder. This dated note preserves the documentation update here.
