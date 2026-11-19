# Setup

Capture these values from the user's authorized setup and verify them through the relevant connector. Do not copy the maintainer's destinations or infer a recipient from a name alone.

```yaml
report_timezone: "USER_SELECTED_TIMEZONE"
slack_workspace_id: "VERIFIED_WORKSPACE_ID"
slack_connection_id: "HOST_CONNECTION_IF_REQUIRED"
slack_recipient_user_id: "VERIFIED_USER_ID"
slack_recipient_email: "VERIFIED_EMAIL"
github_repository: "OWNER/REPOSITORY"
github_branch: "VERIFIED_BRANCH"
github_archive_path: "docs/business-automation-briefs"
delivery_authorized: false
archive_authorized: false
```

Store configuration separately from the distributable plugin, in the host's approved persistent settings or scheduler prompt. Never store credentials here. Set authorization values only from an explicit instruction covering those actions.

For an interactive run, resolve missing values before delivery. For an unattended run, produce the useful brief and report missing destinations or permissions; do not guess, send elsewhere, or create a second scheduler. Honor a draft-only request without writing externally.

Use a dated archive file such as `2026-10-05.md`. Structure it as:

```markdown
# Business Automation Brief | YYYY-MM-DD

Reporting window: START through END, TIMEZONE.

## Brief

The exact Slack brief, under 400 words.

## Delivery

- Status: confirmed, pending, failed, or uncertain
- Slack permalink: confirmed link only
- Verified workspace and recipient ID: configured values
- Delivered at: timestamp if confirmed

## Research notes

Checked sources, failed or inaccessible pages, date evidence, and prior items excluded.
```

Keep research notes out of the concise Slack message. Do not include private client data. Preserve an existing report on retries, updating only verified delivery metadata as needed.
