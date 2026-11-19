# Maintaining this skill collection

Owner and final update decision: **Rachael Quisel (@RachaelQuisel)**.
Support intake: [report a skill problem](https://github.com/RachaelQuisel/Skills/issues/new?template=skill-maintenance.yml).
The assigned owner coordinates fixes. The hourly Skill Check Alerts task is authorized to investigate confirmed failures and prepare fixes on separate branches. It opens draft pull requests for Rachael's review. This is not a promised response-time contract.

## What is set up

- A register of all 163 maintained skill paths, including nested plugin skills and their standalone copies in this repository, with a responsible owner and an exact baseline revision. This counts repository paths; it is different from the number of unique skills in the cross-repository ChatGPT collection.
- Offline regression tests for the audit plugin, Execute logging, maintenance controls, and alert-state transitions. Other skills are registered but have no behavioral coverage in this runner yet.
- A fixed list of regression case IDs. A missing or skipped registered test fails the check. New tests in the configured suites also run automatically.
- A GitHub Actions workflow for each main-branch push, pull request, manual run, and Mondays at 15:30 UTC. It requires GitHub Actions to be enabled and runner capacity. Check the Actions page for actual successful runs before calling it active.
- Timestamped JSON, plain-English summaries, and test evidence retained as Actions artifacts for 30 days. Keep release evidence in Git for longer retention.
- A safe way to prepare an exact version in a separate folder. No installed skill is automatically upgraded.
- A maintenance README for every registered skill. Missing README files fail the inventory check.
- The existing hourly ChatGPT task, now named Skill Check Alerts, monitors the combined Skill checks workflow. Its canonical instructions are in [ALERT-TASK.md](ALERT-TASK.md), with destinations and thresholds in [notification-policy.json](notification-policy.json). Its saved instructions, hourly schedule, and active state were read back during the November 2 consolidation. Scheduled Slack delivery remains unverified until an actual event is delivered and read back.

## Where to see updates

- **Slack:** [La Maison #automations](https://lamaisonsanta-8tm8179.slack.com/archives/C0C7XQK3TTR) receives one opening message per unresolved problem and one verified recovery notice. Repeated failed runs, repair progress, and healthy unchanged checks stay quiet.
- **Reports:** [Skill checks in GitHub Actions](https://github.com/RachaelQuisel/Skills/actions/workflows/release-consistency.yml) holds combined release, inventory, and regression results. Downloads are retained for 30 days.
- **Proposed fixes:** [Pull requests](https://github.com/RachaelQuisel/Skills/pulls) hold changes for Rachael to review. Repair attempt records stay on the candidate branch and are linked from the pull request.
- **Fallback:** If Slack delivery fails, the task reports the problem in ChatGPT.

The [manual Slack delivery test](https://lamaisonsanta-8tm8179.slack.com/archives/C0C7XQK3TTR/p1791738615563109) was sent and read back on October 11, 2026. This verifies that message, not future scheduled delivery or the full automatic repair process.

## How to check the collection

The combined check also verifies the existing catalog plugins against fresh evidence. The hourly alert task reads the full GitHub package, current saved build, and deployed catalog. Its observation contains file hashes and version metadata on the private `skill-alert-state` branch. GitHub Actions rejects a missing or stale observation rather than reporting a match. Local runs without `--sync-observation` check the contract structure only. See [the alert contract](ALERT-TASK.md#check-the-live-plugin-copies-and-catalog).

Each plugin's source/build/catalog mismatch is one alert episode. Changes to its evidence do not send another opening alert. Recovery requires fresh matching evidence for that plugin. The existing notification channel, task schedule, and GitHub email settings stay the same.

From a full clone of this repository:

```sh
python3 -m venv .maintenance-venv
.maintenance-venv/bin/python -m pip install -r maintenance/requirements.txt
.maintenance-venv/bin/python maintenance/run_checks.py --output /tmp/skill-check-results --check-base HEAD^
```

`release-registry.json` holds canonical versions and source mappings. `collection.json` is the maintenance inventory. Each entry points to its actual skill directory, including `plugins/<plugin>/skills/<skill>`. IDs and paths must be unique. Skill folders under `.trash/` (removed copies) and `synced/` (the mirror of the claude.ai account skills) are copies, not maintained skills, so the check does not report them as unregistered. A nested entry can use the ID `<plugin>:<skill>`, matching both path components, when its skill name is also used by a standalone copy. Existing nested entries may keep their unqualified skill ID. Nested entries may use `readme_path` to point to the plugin README. A skill's tree hash covers its bundled files, not just SKILL.md. Checks flag new, missing, and changed skills. Changes are review signals; passing the offline tests does not approve those changes or establish API compatibility.

The alert task saves problem episodes, delivery claims, and verified receipts in `alert-state.json` on the private `skill-alert-state` branch. That branch holds runtime state only. A new run ID does not create a new alert for the same unresolved problem. Conditional updates and saved delivery claims prevent two task runs from sending the same pending event. A timeout is reconciled before another send. Missing or unreadable state stops sending instead of resetting the alert history. Rachael's separate GitHub Actions email settings remain unchanged.

A passing offline test proves only its assertion against its supplied fixture. The audit database checks use a SQLite test double. They do not verify PostgreSQL policies or a deployed collector. Prompt behavior, host installation, live APIs, permissions, and model versions remain **unverified** until separately tested.

A seven-day freshness window applies to recorded behavioral verification, not a file edit, inventory check, or offline helper test. All live compatibility dates start empty. Never fill them just because the scheduled workflow passed.

## Supported-system changes

For each skill before calling it supported, record the exact agent host/model, integration/API version, permission requirements, official documentation URLs, a representative test, and an evidence link in its collection entry. Empty `supported_environments` means compatibility has not been established.

The weekly run repeats offline tests and reminds the maintainer that upstream review is required. It does **not** currently monitor all vendors' release notes or apply repairs automatically. For a confirmed failure, the hourly alert task can prepare a fix, run tests, and open a draft pull request. Rachael decides whether to merge. Review official change logs for the mapped systems, open an issue for relevant changes, reproduce the effect in a sandbox, and prepare a tested update. Keep uncertain compatibility visibly unverified.

## Automatic repair preparation

On October 11, 2026, Rachael authorized the existing hourly task to prepare fixes in this repository. It must confirm the problem still exists, reuse any existing repair branch or pull request, and save its attempt count before working. The limit is three attempts per unresolved problem across scheduled runs. After three failed attempts, or an access or validation blocker, it records what happened and one next step in the existing GitHub repair record. The November 2 notification policy permits only the opening problem and verified recovery to notify Rachael.

The task uses synthetic tests and the registered suite. It does not weaken checks to make them pass. It never merges, enables auto-merge, writes fixes directly to main, or changes installed copies or business systems. A saved proposal is not a resolved production problem. The updated task instructions are saved; an end-to-end scheduled repair has not yet been verified.

## Turn a recorded failure into a lasting test

1. Open the issue form with the skill, exact revision, runtime, expected result, observed result, and sanitized evidence. Do not commit client logs, tokens, names, or identifiers.
2. Recreate the failure with synthetic inputs. Record permission before reusing any customer-derived material. Review the result for privacy; replacing names alone is insufficient.
3. Add an executable regression case to a reviewed suite. Confirm it fails on the old code and passes on the fix. Preserve the old failure evidence and explain the confirmed cause.
4. Add its node ID to `regressions.json`. Every later check reruns the registered suites. Never remove an old regression just to make a check pass; a deliberate retirement needs a reviewed reason and replacement coverage.
5. Run the full offline suite and the relevant host/API behavioral checks. Put test evidence and limitations in the proposed change. Update that skill's baseline only after review.
6. Record release commit, previous commit, change reason, regression IDs, compatibility evidence, outstanding limits, and approval in `releases.json`. Users decide whether to adopt it.

To expand coverage, first inspect an existing test suite for network calls, production writes, secrets, and synthetic fixtures; then add it to `SUITES` in `check.py`. Do not auto-execute every script in the repository.

## Understand an audit result

Use the existing audit plugin and its event contract. Explain recorded actions using the exact skill/rule version, timestamps, test results, and destination evidence. Separate observed facts, inference, and unknowns. A test failure is evidence of a failed assertion, not proof of its root cause. Missing records do not prove success. Preserve the original event when recording a correction.

Reports identify failed or missing test IDs and their evidence files. Use those files to investigate before proposing a fix. For actual automation runs, use the recorded run timeline rather than the maintenance test log.

## Choose an update or rollback

Use a full immutable commit SHA. In a full clone, fetch the desired commit if needed, then prepare a separate version:

```sh
python3 maintenance/prepare_version.py --commit FULL_40_CHARACTER_SHA --destination /absolute/path/to/new-skill-version
```

The command refuses an existing destination and never changes the current checkout or installed skills. Review the diff, compatibility, and tests, then explicitly select the new folder using your agent host's supported installation process. Keep the previous folder and commit until the update works. To roll back, select the previous folder again or prepare its commit the same way. Reverting instruction files does not undo business actions, data migrations, or API changes.

The current GitHub collection and copies imported into ChatGPT/Claude are separate installations. This setup does not silently replace or synchronize those imported copies. Record the adopted commit for each installation; a moving `main` checkout is not a pinned release.

## Current coverage and limits

The initial 31 existing checks covered 22 audit-plugin/Execute cases and 9 Acuity export cases. The 9 Acuity export cases were retired on 2026-10-13 with the `addtoacuity` skill (see `archive/README.md`), so 22 remain; `baseline-report.json` predates that retirement. The maintenance tests cover freshness, missing owners or skills, missing README files, result interpretation, skipped or deleted tests, safe version preparation, and failure-alert decisions. See `baseline-report.json` for the latest local result and source revision. [The first cloud run](https://github.com/RachaelQuisel/Skills/actions/runs/38143233364) succeeded. The current run history is the source for later checks.

Other skills' existing tests are not yet wired into this runner. No claim is made that all historical fixes have regression coverage, all registered skills work, or that there is paid support. Expanding behavioral coverage and mapping supported environments remain explicit maintenance work.

## Documentation changes and versions

The new README files change each skill folder's recorded contents. The checker may therefore list those folders as changed since the original baseline. This is a review notice. It does not mean the skill failed or that a new version was approved. The existing skill instructions and scripts were not changed by the README update.
