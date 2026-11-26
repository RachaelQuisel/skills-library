# Check Catalog Reports

Status checked October 12, 2026: Enabled schedule verified. Automatic alert delivery has not been verified.

Category: Reporting
Workflow type: Checks and alerts
Tools: ChatGPT, Slack.
Runs: Cloud schedule verified.
Tags: #reporting #checks-and-alerts #chatgpt #slack #cloud-verified
Identity: ChatGPT task 6acb92a719dc8191b372b3bd3368cb6f.
Source: The current task definition, read October 12, 2026. The saved definition is in [settings.json](settings.json).

## Trigger

- The cloud task starts each Monday at 6 AM America/Los_Angeles, beginning October 12, 2026.
- It checks that Monday's catalog report. It does not depend on Rachael's computer being awake.

## Inputs

- Read task 6acb928d16bc8191ae1716cfe40da199. Read whether it is enabled and when it last ran, when available.
- Read La Maison #automations, channel C0EXAMPLE01 in workspace T0AT819U2UQ.
- Read every relevant page and all replies for ACATALOG:YYYY-MM-DD. Read earlier alerts and delivery counts for ACATALOG-WATCH:YYYY-MM-DD.

## What happens

1. Look for a verified COMPLETE, PARTIAL or FAILED final report. A start or ATTEMPT note is not a final report.
2. If more than five catalog attempts are recorded, report that the limit was exceeded. Do not start another attempt.
3. If the catalog task is disabled, alert once for this occurrence. Do not enable it.
4. If COMPLETE is verified, stay quiet unless an independent disabled-task or attempt-limit condition needs an alert. If PARTIAL or FAILED already explains the blockers, do not repeat them.
5. If no final report exists at this check, prepare a short alert. State whether a start was seen, the known attempt count and available scheduler evidence. Say the cause is unknown unless logs prove it.
6. Explain the uncertainty. A missing start may mean the task did not run. A start without a final report may mean it is still running, stalled or unable to report. Time alone does not prove failure.
7. Before sending, check for the same ACATALOG-WATCH alert. Skip a duplicate.
8. Allow at most five total alert-delivery attempts. Save each count in the approved run thread and read it back when that thread is available. If the count cannot be read or recorded, stop Slack attempts and report in ChatGPT.
9. If a write times out, check whether it succeeded before retrying. Do not retry denied access or an unclear destination.
10. Read back the alert. If Slack is unavailable, return the full alert in ChatGPT and state that delivery failed. Never run or retry the catalog.

## Outputs

- Send an alert in #automations only when action is needed. Include the run label, observations, evidence, known attempt count, blockers, one next step and a verified message link after successful delivery.
- Keep other clients' private details out of the alert.
- The checker depends on the cloud scheduler and Slack. An outage affecting both can prevent notification.
- The October 11 manual test checked ACATALOG-MANUAL:2026-10-11. Its alert label was ACATALOG-WATCH-MANUAL:2026-10-11. A missing manual-test report meant pending rather than a missed scheduled deadline.
