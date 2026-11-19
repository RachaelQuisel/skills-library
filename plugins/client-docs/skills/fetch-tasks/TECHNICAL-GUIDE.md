# fetch-tasks

Fetches open tasks from the XRAY task hub for one client, sorts them into Blocked, In Progress, At Risk, and Carried, and runs a hygiene check that reports duplicates, missing names, and Done status mismatches. It never changes a record.

Read [SKILL.md](SKILL.md) for the full instructions.

## Maintenance

- Owner: RachaelQuisel.
- This skill is registered in the collection check. Its behavior is not yet covered by the scheduled test runner, so a passing check does not prove it works.
- Report a problem through the skill-maintenance issue form.
