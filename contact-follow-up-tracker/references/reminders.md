# Reminders

Read this only when the user asks to enable, change, schedule, run, or acknowledge reminders. Installation leaves reminders disabled.

## Explicitly enabled reminders

Get the user's cadence, lead_days, and IANA timezone, and their intended Cowork task output/notification preference. To save settings, use `op: reminders`, enabled (boolean), cadence (nonempty text when enabled), lead_days (nonnegative integer), time_zone, and the actual confirmation wording. Disabling is also an explicit setting update. This only saves log settings; confirm the scheduler itself was configured separately before claiming it is scheduled.

Create or edit a Cowork scheduled task only when requested. Its prompt must include this skill name, the stable selected folder ID and log ID, and instructions to re-read every snapshot and resolve the live head on every run. Set the requested cadence and timezone in the scheduler. A remote task uses the connected Drive log, never a local folder. Use the user's chosen completion-notification preference; do not enable email, push, or messages to contacts by assumption.

After a live resolve, run `python3 <skill-dir>/scripts/memory.py scan --input <current.json> --output <new-scan.json>`. Use actual current time in production. `status: disabled` means stop. For each item, show contact identity, action and direction, exact source wording, deadline/follow-up date, timezone, upcoming/today/overdue state, and notification_token. Dates are interpreted in each commitment's timezone; scheduler cadence uses the reminder timezone. If no items are actionable, suppress the completion notification and return no routine digest. Failed access or a broken chain must be reported as a failed check, never an empty successful scan.

### Record only observed output

Scanning does not write a notification receipt. A successful task status, an attempted push/email, or a generated reply is not evidence that output was seen. The tested host provides no tool to retrieve prior completed output or a delivery receipt. Use a user's explicit acknowledgement of the visible Cowork reminder to persist suppression: `op: observed`, observed true, notification_tokens from that output, output_ref (the actual task/run URL or other specific visible output reference), and confirmation containing the user's real acknowledgement wording. Never invent that acknowledgement. Run `mutate`, then save and verify the new snapshot normally.

Receipts are labeled `user_acknowledged_output`, not independently verified push/email delivery. Until acknowledgement is saved, a reminder may repeat. Once saved, an unchanged commitment is suppressed across later scans, including a later overdue date; changed action/date/timezone produces a new token. A stale token for a changed or closed commitment cannot be recorded as a current receipt. This plugin does not guarantee automatic once-only notification delivery.
