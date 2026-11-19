# Alert policy

An alert should identify an actionable change. It should not create noise when the routine is healthy.

## Alert conditions

Alert when:

- a completed maintenance run concludes with failure, timeout, cancellation, action required, startup failure, or stale status;
- a run remains queued or in progress beyond the configured threshold;
- no successful completed run exists within the configured freshness window;
- the repository or workflow evidence cannot be read;
- the notification delivery step itself fails.

Do not treat a skipped run as a passing run. Do not report healthy when access fails.

## Message contents

Keep the message short. Include:

1. the recorded issue;
2. its impact;
3. the direct run or evidence link;
4. one next step.

Name a skill or regression case only when the evidence supports it. Distinguish failed assertions from dependency installation, permissions, missing evidence, and delivery failures.

## Repeats and recovery

Use the workflow run identifier and attempt as the alert key. Suppress repeat alerts for the same evidence when prior state is available. Remind about an unresolved condition no more than once per day. Send one recovery message after a verified rerun or documented fix resolves a previously reported problem.

State where alert state is stored. Conversation memory alone is not durable deduplication.

## Verification

Creating a schedule is not proof that delivery works. Verify the workflow produces completed runs and test the notification path. Until then, describe the channel as configured but unverified.
