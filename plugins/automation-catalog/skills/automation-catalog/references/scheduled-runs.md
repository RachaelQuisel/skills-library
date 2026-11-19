# Scheduled catalog updates

Use this only when the user has requested recurring work. Installing the plugin does not schedule it.

1. Use a supported cloud scheduler when the task must run while the user's computer is asleep. Verify the saved task, scope, time zone and destination. Do not describe a local timer as cloud execution.
2. Keep task identifiers and account-specific routes outside the plugin. Use a private deployment record or saved task prompt. A scheduled run uses these settings. If a required setting is missing, report the blocker instead of waiting for live intake.
3. Give each scheduled occurrence a stable run key. Use the scheduled local date, even when execution starts late. Keep one status thread for that key. If a verified COMPLETE, PARTIAL or FAILED report already exists, return its link. If another run may be active, stop and report the uncertainty.
4. Allow no more than five total attempts for that occurrence, including the first. This is one shared budget for the whole routine. Before each attempt, save ATTEMPT n/5 in the approved status record and read it back. If the count cannot be verified, stop. Resume from the saved count. Never reset it or launch another worker to bypass the limit.
5. Retry only failures that may clear on retry. Stop early for denied access, missing authorization or unclear destinations. Before retrying a timed-out write, read the destination. Resume unfinished work and keep completed-write receipts. Never begin attempt six.
6. Post a final report even when nothing changed. Use COMPLETE for finished work, PARTIAL for saved work with remaining gaps, or FAILED for a blocked run or exhausted attempts. Include counts found, documented, saved, posted and unchanged. Include search gaps, attempts used, evidence for failures, blockers, one next step and safe result links.
7. Verify report delivery. If it fails, return the full report in the host and say the message was not delivered. Keep the weekly schedule active after a failed occurrence unless the user asked for a different stopping rule.

The five-attempt rule is an instruction to the host agent. This package does not provide a hard scheduler limit. A separate report checker can detect missing reports. If both rely on the same unavailable platform, neither can guarantee an alert during that outage.
