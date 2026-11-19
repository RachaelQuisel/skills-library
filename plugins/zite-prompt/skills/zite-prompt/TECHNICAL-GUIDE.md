# zite-prompt

<!-- skill-maintenance:start -->
## Maintenance

### Trigger

- GitHub checks the collection when the main branch changes, when a pull request opens or changes, and every Monday at 15:30 UTC.
- A separate cloud task checks for failed or missing runs every hour. Your computer can stay off.

### Inputs

- Read [SKILL.md](SKILL.md) for this skill's instructions.
- Read the [collection register](../maintenance/collection.json) for its recorded version and owner.
- Use saved check results and synthetic prompt examples. Do not send test prompts to Zite or use customer data.

### What happens

1. The routine checks that this skill is registered and has an owner and README.
2. It reruns the registered offline suites. The examples in `evals/` are stored evidence but are not yet executed by the scheduled runner.
3. If a check fails, gets stuck, or no successful collection run appears for eight days, the alert task notifies Rachael.
4. A confirmed fix is prepared on a separate branch for review. Rachael decides whether to merge or adopt it.
5. Installed copies are not replaced automatically.

### Outputs

- Test results and failure details appear in [GitHub Actions](https://github.com/RachaelQuisel/Skills/actions/workflows/maintained-skills.yml).
- Actionable alerts appear in La Maison Slack `#automations`, with ChatGPT as the fallback.
- Use the [support form](https://github.com/RachaelQuisel/Skills/issues/new?template=skill-maintenance.yml) to report a live problem.
- Follow the [maintenance guide](../maintenance/README.md) to review changes or return to an earlier version.

**Owner:** Rachael Quisel. **Live compatibility:** unverified.
<!-- skill-maintenance:end -->
