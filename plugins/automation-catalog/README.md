# Automation Metadata Maker

![Catalog update icon](icon.png)

Creates a name, guide, run location, and tags for each automation.

Find automations across accessible businesses and projects. Keep existing guides and approved Slack channels up to date.

Formerly Automation Catalog Refresh / Update Automation Catalog. The package identifier and invocation remain `automation-catalog` so existing installations and links keep working.

## Use it

In Claude Code, run `/automation-catalog:automation-catalog` and describe the projects to search and the approved places to save and share the results.

In Codex, use `$automation-catalog`. This is skill-invocation syntax. It is not a shell command or a request to read credentials.

The plugin checks connected workflow services, code, project documents and messages. It records unavailable sources. It does not claim to find every automation when access is incomplete.

Each guide has Trigger, Inputs, What happens and Outputs. Categories, workflow types, tool tags and run labels appear above those sections. Evidence labels distinguish enabled schedules, reviewed code, older descriptions and plans.

## What it changes

- Update existing guides and correct conflicting current instructions.
- Group the catalog by business and category.
- Edit existing approved Slack messages and skip unchanged copies.
- Record completed writes and unfinished work so retries do not repeat successful changes.
- Check the business, workspace, channel and audience before sharing.

## Connections and limits

The host needs access to the services being searched. Posting also needs an approved destination and write permission. This package uses the host's existing connectors. It supplies no credentials, server or Slack connection.

Use the installed /auto and /voice-align skills when available. The included writing rules provide a fallback. Report when either skill is unavailable.

The local Python helper checks a prepared inventory and creates draft guides and a publication plan. It does not search accounts or send messages. It requires Python 3.10 or later. It uses only the standard library.

The plugin changes documentation. It does not run or repair the automations it finds. Permission checks in its instructions are not a substitute for the host's access controls.

## Scheduling

Installing this plugin does not create a recurring task. A separately configured cloud scheduler is required to run while your computer is asleep. Keep personal routes and task settings outside this package.

For an approved recurring run, use one saved status record and at most five total attempts per occurrence. The agent follows this rule; the package does not enforce it in a scheduler. The companion Check Catalog Reports plugin checks for missing reports. A shared platform outage can prevent both work and alerts.

## Installation and review

This package is in a private draft pull request. It has not been submitted to Anthropic or tested through a Claude installation. See the repository's [marketplace review notes](../../deployments/automation-catalog/marketplace-review.md).

The Claude manifest is in .claude-plugin. Portable and Codex manifests are also included. The repository-level marketplace lists both plugins. Each host still needs its own connections and permissions.

## Local checks

From this plugin folder:

```sh
python3 -m unittest discover -s tests -v
python3 skills/automation-catalog/scripts/catalog.py skills/automation-catalog/assets/example-inventory.json --output /tmp/catalog-example
```

Use a new output directory for another run. The example is fictional. Its authority fields describe checks made through connectors. They do not grant permission.

## Maintenance

Version: 0.2.0, a private review version. Owner: Rachael Quisel. Report problems in the existing Skills repository. Include the version, expected result, actual result and sanitized evidence. Do not include credentials or private client details in a public issue.

Review changes before adopting an update. Keep the previous commit for rollback. Restoring a plugin does not undo documents or messages it changed. The included tests are separate from the repository's top-level maintained-skills tests.
