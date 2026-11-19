# Automation Briefing

## Trigger

Ask for an automation brief or run it through an existing cloud schedule. The plugin covers Airtable, Zapier, Make, n8n, Pipedream, Fillout, and leading artificial intelligence (AI) tools that affect client work.

## Inputs

- Provide your reporting timezone, verified Slack recipient, and GitHub folder using the [setup guide](skills/automation-briefing/references/setup.md).
- Connect the tools needed to search the web, read earlier reports, send Slack messages, and save GitHub files.
- Give permission for the destinations you want it to use.

## What happens

1. Check earlier reports and messages to avoid repeating news or sending the same report twice.
2. Research official announcements, prices, access rules, software connections, limits, and features being retired.
3. Explain each important change in plain English. Recommend a small test, a workflow change, or something to watch. Prefer settings and consistent input formats before complex code changes.
4. Include useful AI workflow examples and checked demo links. These may include How I AI with Claire Vo.
5. Send the brief and save the same text when authorized. Check both results and report any failure.

## Outputs

- Receive a brief under 400 words with no more than five items, ordered by importance.
- See what changed, why it matters to client work, and one next step for each Test or Change recommendation.
- Receive confirmed links to the Slack message and saved GitHub report when available.

## Install

This repository is a private Claude Code marketplace. You need repository access.

```text
claude plugin marketplace add RachaelQuisel/Skills
claude plugin install automation-briefing@rachael-quisel-skills
claude plugin details automation-briefing
```

Use `/automation-briefing:automation-briefing` or ask for an automation briefing. Other Claude apps must support this plugin format before they can use it.

## Requirements and limits

The assistant running this plugin needs web research tools. Slack and GitHub must be connected separately. The package contains no connections, credentials, server, automatic startup actions, or scheduler.

To run each week while your computer is asleep, set up a supported cloud scheduler with the saved settings. Installing the plugin alone does not create a schedule. Test and Change are recommendations. The plugin does not change client tools or workflows.

See the [privacy notice](PRIVACY.md) for details about the information it reads, sends, and saves.

## Release status

Version 1.0.1 includes plain-English instructions based on Voice Align. It is a private package. It has not been approved for Anthropic's directory. Local package checks do not prove that installation or a live run works. See the [validation record](docs/validation.md).
