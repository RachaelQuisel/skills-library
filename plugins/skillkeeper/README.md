# Skillkeeper: Skill Maintenance

Know what was tested, what needs attention, and who owns the fix.

Give Skillkeeper a repository of agent skills and the person responsible for it. Get a maintenance review or, when requested, a system for checking updates and recording failures.

- Assign an owner and record the version of each skill.
- Turn confirmed failures into tests that catch the same problem again.
- Track when supported tools were last checked live.
- Prepare update and rollback records for the owner's decision.
- Define useful failure alerts and verify delivery when authorized.

## How it works

1. Choose the repository and request setup, a health check, a failure investigation, or release preparation.
2. Skillkeeper reads the files and evidence, runs reviewed checks when available, and makes authorized changes.
3. Receive the findings, evidence links, and one next step for each issue.

## Trigger

Use the plugin when someone asks to maintain, audit, test, version, release, roll back, or monitor a collection of agent skills.

## Inputs

- A local skill repository or an authorized GitHub repository.
- The person responsible for maintenance and release decisions.
- Existing skill files, tests, failure reports, and supported-system evidence.
- The desired alert destination when notifications are requested.

## What happens

1. The plugin inventories skills and records the exact version being evaluated.
2. It identifies missing owners, documentation, tests, and compatibility evidence.
3. It turns confirmed, sanitized failures into named regression cases.
4. It separates offline test results from live host and API compatibility.
5. It prepares release and rollback records without silently adopting an update.
6. It explains failures using recorded facts, inference, and unknowns.
7. When alerting is authorized, it defines actionable failure and stale-run notifications and verifies that the delivery path actually runs.

## Outputs

- A maintenance inventory with owners and pinned versions.
- A coverage and freshness report.
- A regression register and test evidence.
- Release and rollback records.
- Plain-English failure explanations and one next step.
- Notification rules that stay quiet when the routine is healthy.

## Control and limitations

The plugin does not approve or install updates on its own. It does not treat a recent file edit as compatibility evidence. A passing fixture test does not prove that a live integration works. Missing telemetry does not prove success. The responsible owner decides whether to adopt or roll back a release.

The current reference implementation is in the repository's [maintenance folder](https://github.com/RachaelQuisel/Skills/tree/main/maintenance). It is separate from the installed plugin. Its workflow covers registered suites, not every live use of every skill.

For this repository's configured routine, see [where to see updates](../../maintenance/README.md#where-to-see-updates) and the [notification and repair policy](../../maintenance/notification-policy.json). The existing task sends short updates to La Maison Slack #automations, prepares fixes for review, and stops after three unsuccessful repair attempts. Rachael still approves merging. These are this repository's settings, not behavior enabled by installing the plugin.

Installing Skillkeeper does not start scheduled checks or failure alerts. Those require a separately configured runner and verified notification destination. Access to private repositories and external services depends on the host's connected tools and permissions.

## Installation

This repository is private. Install only from an account that already has access.

```text
claude plugin marketplace add RachaelQuisel/Skills
claude plugin install skillkeeper@rachael-quisel-skills
claude plugin details skillkeeper
```

Invoke `/skillkeeper:skillkeeper` or ask Skillkeeper to check your skill collection. A newly installed skill may require a new Claude Code session before it appears.

## Data handling

See [PRIVACY.md](PRIVACY.md). This package contains instructions and documentation only. It does not include a publisher-operated server, hook, or background process.

## Package status

Version 1.0.1. The package is private and proprietary. Anthropic directory submission and official Claude installation testing remain unverified. See the [validation record](docs/validation.md).
