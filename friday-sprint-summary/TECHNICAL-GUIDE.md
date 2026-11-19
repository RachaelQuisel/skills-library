# friday-sprint-summary

<!-- skill-maintenance:start -->
## Maintenance

### Trigger

- GitHub checks the collection when the main branch changes, when a pull request opens or changes, and every Monday at 15:30 UTC.
- A separate cloud task checks for failed or missing runs every hour. Your computer can stay off.

### Inputs

- Read [SKILL.md](SKILL.md) for this skill's instructions.
- Read the [collection register](../maintenance/collection.json) for its recorded version and owner.
- Use the saved check results and a made-up example of any reported failure.

### What happens

1. The routine checks that this skill is registered and has an owner and README.
2. It reruns the tests listed for this skill. This skill is registered, but its behavior is not yet covered by the scheduled test runner. A passing collection check does not prove this skill works.
3. If a check fails, gets stuck, or no successful collection run appears for eight days, the alert task tells Rachael in ChatGPT.
4. Rachael coordinates the fix. A confirmed fix gets a regression test so the same problem is checked again.
5. Rachael decides whether to adopt an update. Installed copies are not replaced automatically.

### Outputs

- Test results and failure details appear in [GitHub Actions](https://github.com/RachaelQuisel/Skills/actions/workflows/maintained-skills.yml).
- Actionable alerts appear in ChatGPT. They cover recorded check failures, not unrecorded live use.
- Use the [support form](https://github.com/RachaelQuisel/Skills/issues/new?template=skill-maintenance.yml) to report a live problem.
- Follow the [maintenance guide](../maintenance/README.md) to review changes or return to an earlier version.

**Owner:** Rachael Quisel. **Live compatibility:** unverified.
<!-- skill-maintenance:end -->
