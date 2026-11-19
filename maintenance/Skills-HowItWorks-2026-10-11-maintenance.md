The Skill checks workflow checks release versions, generated copies, skill inventory, and all registered offline tests in one run. It runs when main changes, when a pull request changes, on demand, and each Monday at 15:30 UTC. That is 8:30 a.m. Pacific during daylight time and 7:30 a.m. during standard time.

The workflow reads the canonical release registry, maintenance inventory, and required regression list. Both release and maintenance checks run even if one fails. The result includes a readable summary, structured report, and logs. Missing or skipped required tests remain failures. The workflow does not certify live integrations or public directory publication.

The existing hourly Skill Maintenance Alerts task reads the current instructions in [ALERT-TASK.md](ALERT-TASK.md) and the [notification policy](notification-policy.json). It watches the combined workflow. A newer successful check supersedes earlier completed failures, so old failures do not create new alerts. Runs that remain active for over an hour, missing recent successes, and unavailable verification are checked separately.

The task saves each unresolved problem and its delivery receipts in the private repository's skill-alert-state branch. It announces each problem once and sends one recovery notice after the checks confirm recovery. Another run with the same problem does not create another alert. There are no daily reminders or separate repair-progress alerts. If a problem returns after recovery, it starts a new episode.

Before sending, the task conditionally claims the saved event and checks the existing Slack message marker. It reads the message back before recording delivery. A timeout requires checking whether the message arrived; it is not permission to send another copy. If saved state cannot be read or updated, delivery stops rather than discarding history.

Alerts use the existing La Maison Slack #automations destination, with the existing task chat as fallback after a confirmed delivery failure. GitHub's own account email settings remain unchanged. An unchanged healthy check produces no task notification.

Confirmed code problems may be investigated on an existing repair branch or a new draft pull request. The task keeps a persistent limit of three attempts per unresolved problem. It records repair progress in GitHub. It cannot merge, change main directly, upgrade installed copies, or change business systems. A proposed repair is not a verified recovery.

The combined replacement passed in GitHub before the old Maintained skills workflow was disabled and removed from the active configuration on November 2. The old run history remains available. The existing alert task was saved and resumed; its hourly schedule and active state were read back. See [the consolidation record](consolidation-record.json) for the evidence. Future scheduled message delivery is verified only when an actual message is sent and read back.
