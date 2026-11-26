<!-- preflight-allow: documents-scanner-patterns -->

# Alerting

A failure trips the gate, and a named human needs to hear about it within a set time. The default is a local Markdown file. Everything beyond that lives in this reference and only runs with the user's explicit say-so.

## Default: local blocker file (always on)

When `scripts/check.py` exits non-zero and `--no-alert` is not set, it writes a timestamped Markdown file under `./alerts/`. The file names:

- The job and the time the check ran.
- The acceptance sentence and the never sentence (quoted).
- Every failing assertion, marked `(GATE)` if it was a gate.
- The configured check file's path.

A gate trip does not fire an external send on its own. The user reads the file. For an unattended run, this file is still the source of truth; any external route sends a link to it, not a replacement for it.

## Slack incoming webhook (opt-in)

Ask the user for the webhook URL. Credentials live in the host's environment or a secret store. The webhook URL is sensitive; never paste it into `check.json`, SKILL.md, chat, or a commit.

1. Ask: "Which named human owns this alert? What Slack channel? Within how many minutes should they see it?"
2. Ask: "Where is the Slack incoming webhook URL stored?" (Expect an environment variable name; do not accept the URL itself in chat.)
3. Draft the send wrapper locally. Example shape (the user writes the real file in their own folder):

   ```bash
   #!/usr/bin/env bash
   # scripts/alert-slack.sh - called after a non-zero check.py exit
   set -euo pipefail
   ALERT_FILE="${1:?need alert file path}"
   [[ -n "${SLACK_WEBHOOK_URL:-}" ]] || { echo "SLACK_WEBHOOK_URL not set"; exit 3; }
   JOB=$(grep -m1 '^# Independent check tripped:' "$ALERT_FILE" | sed 's/^# //')
   HUMAN="@name-here"
   BODY=$(printf "%s (cc %s)\\nBlocker report: %s" "$JOB" "$HUMAN" "$ALERT_FILE")
   curl -sS -X POST -H 'Content-type: application/json' \
     --data "$(jq -n --arg t "$BODY" '{text: $t}')" \
     "$SLACK_WEBHOOK_URL"
   ```

4. Dry-run the wrapper first. Point it at a fake webhook URL (e.g. `https://httpbin.org/post`) and confirm the formatted body. Only then swap in the real URL.
5. Fire a live alert only after the user says to fire it, and only against a test channel the first time.

## Email via SMTP (opt-in)

Same discipline. Credentials in the host's secret store. Draft the send wrapper locally. Dry-run against a disposable address the first time. Fire the live send only after the user says to.

## GitHub issue (opt-in)

For engineering-owned automations the right alert is often a GitHub issue:

```bash
gh issue create \
  --repo "$OWNER/$REPO" \
  --title "Independent check tripped: $JOB_NAME" \
  --body-file "$ALERT_FILE" \
  --label blocker
```

Same opt-in rule: ask first, dry-run against a sandbox repo, only create against the real repo after the user confirms.

## Stop-after-three retries

If the same check trips three consecutive times with no human acknowledgement:

- Stop re-sending the external alert.
- Keep writing the local blocker file.
- Emit a stale-run notice naming the number of unacknowledged trips.

The point is not to silence a real problem; it is to stop pager-storms when the problem is the checker itself or the alert route.

## What "verified" means for an alert route

"Verified" here is a two-step thing:

1. A live send against a test destination produced the expected message, with the expected formatting, inside the time budget.
2. The named human confirmed by hand that they saw it.

Neither on its own is sufficient. A `200 OK` from a webhook is not proof that a person read the message. Say so in the report to the user.
