# Check Catalog Reports

![Catalog report check icon](icon.png)

Check whether a scheduled automation catalog update produced its final report. Send known failures and blockers to an approved channel.

## Use it

In Claude Code, run `/automation-catalog-failure-check:check-catalog-reports`. Supply the catalog task, expected run date, time zone, report deadline and approved report channel. Existing saved settings can supply these details.

The plugin reads the task status and matching report thread. It stays quiet after a verified successful report. It avoids repeating failures that were already explained. If the report is missing after the deadline, it states what was observed and gives one next step. It does not invent a cause.

## Connections and limits

The host needs access to the scheduler and report destination. If scheduler data is unavailable, the check says so. If report access fails, it cannot declare the run healthy.

The plugin can post an authorized alert and keep delivery evidence. It never reruns the catalog, repairs workflows or changes schedules. It allows at most five alert-delivery attempts. A saved count prevents a resumed run from starting over. These are agent instructions, not a hard limit in scheduler code.

The package contains instructions and references. It has no server, hooks, scripts or credentials. It uses existing host connections. The icon is a plugin asset. It is not a custom icon on a ChatGPT scheduled task.

## Scheduling

Installing this plugin does not create a schedule. A separately configured cloud scheduler is required for background checks. Keep task identifiers, account routes and private evidence outside this package.

A scheduled check uses its saved settings. It reports missing settings rather than waiting for a live conversation. If Slack delivery fails, it returns the alert in the host. If the shared scheduler or host is also down, notification may be delayed.

## Installation and review

Version: 0.2.0, a private review version. The package is in a draft pull request. It has not been submitted to Anthropic or tested through a Claude installation. See the repository's [marketplace review notes](../../deployments/automation-catalog/marketplace-review.md).

The repository-level marketplace lists this plugin and Update Automation Catalog. The checker can inspect an existing compatible catalog report without installing the updater.

## Maintenance

Owner: Rachael Quisel. Report problems at https://github.com/RachaelQuisel/Skills/issues. Include the version, expected result, actual result and sanitized evidence. Keep private client details and credentials out of public issues.

Review changes before adopting an update. Keep the previous commit for rollback. Reverting the plugin does not remove alerts already sent.
