# Skill check alerts

Monitor the existing Skill checks workflow in the private `RachaelQuisel/Skills` repository. Read this file and `maintenance/notification-policy.json` from current `main` at the start of each run. Keep the existing hourly schedule and task identity. These instructions replace the earlier per-run alerts and daily reminders.

Only two events call for a notification: a newly observed unresolved problem and verified recovery from a problem that was already reported. Do not send daily reminders, routine healthy reports, separate notices for another run with the same problem, or additional notices when a repair proposal is ready or an attempt stops. Put repair details in the existing GitHub repair record and pull request. Rachael's GitHub account email settings are separate and must remain unchanged.

## Read the evidence

### Check the live plugin copies and catalog

Use [the sync contract](plugin-sync.json) for the existing 28 catalog plugins, their private build IDs, and their full GitHub package paths. Read current `main`. An old checkout, saved Site draft, plugin cache, or prior verification date cannot establish current health.

1. Read each existing build's release ID, version, scope, and audience through Plugin Creator. Reuse previously verified hashes only when the immutable release ID is unchanged. When it changes, retrieve the current owned archive and check all its files.
2. Run [the read-only observer](observe_plugin_sync.py) with authorized GitHub source access. It fetches `main`, compares canonical files and skill inventories with saved archives, and reads the deployed artifact's `/api/plugin-sync` probe. The probe contains public catalog links and versions; it does not expose private tracking notes.
3. Pass a JSON object on hidden stdin. Its `plugins` list contains `{name, plugin, download_url}` records from Plugin Creator; `download_url` is needed only for a changed or previously unverified release. Run `python maintenance/observe_plugin_sync.py --cache <source-cache> --previous <prior-observation> --output <observation>`. A first capture can omit `--previous`. Use the existing private state branch for the prior observation. Do not write signed URLs, credentials, or private skill bodies into observation files or messages.
   - A hosted run without SSH can pass `source_revisions`, a map of every canonical repository to its current `main` commit. Use GitHub's compare-commits tool with base and head both `main`, taking `base_commit.sha` from an identical comparison. A file's blob SHA is not a branch revision. The observer reuses hashes only if these commits, current release IDs, and comparison rules still match. It still reads the deployed artifact live. A changed or missing identity requires a full capture; treat missing access as unverified and keep the existing alert episode open.
4. Validate the observation with `python maintenance/plugin_sync.py --observation <observation> --output <sync-report>`. If the runtime cannot access the required source, builds, artifact, or execution tools, record verification as unavailable. Never refresh an earlier timestamp in place. An unavailable source does not resolve a mismatch.
5. Save `plugin-sync-observation.json` on the existing private `skill-alert-state` branch. Save only metadata and hashes. Use the current file SHA for compare-and-set and read the saved bytes back. The GitHub workflow uses this same observation; it rejects missing or older-than-three-hour evidence.
6. Pass `--sync-report <sync-report>` to `maintenance/alert_policy.py` with the existing runs, reports, policy, and state. Open one episode per affected plugin, grouping its version, file, and link differences together. Repeated failures, new hashes, and newer run IDs update the same episode. Fresh matching evidence for that plugin can resolve it while another is still failing. A report in Actions and the hourly observer do not create separate alerts for the same problem.

These checks can prepare a fix through the existing draft-review process. They cannot merge a release, replace a saved plugin, deploy a Site, or submit anything to Anthropic. Leave existing Anthropic listings and status records alone.

### Check the existing GitHub workflow

Read Actions runs for `.github/workflows/release-consistency.yml`, scoped to `main`, covering at least the last eight days. Ignore historical Maintained skills runs and other workflows or branches. Select the newest completed result by run creation order and attempt, rather than announcing every failed run in history. A newer successful result supersedes earlier completed failures. Separately detect active runs older than 60 minutes and the absence of a successful run for eight days. Skipped or unknown results do not prove success. GitHub access failure means verification is unavailable.

For a failure, read its jobs and the `skill-checks-<run-id>-<attempt>` artifact. Use the top-level `report.json`, checking its source commit and attempt against the run. Inspect logs if setup failed before a report could be written. Distinguish release errors, missing inventory entries, specific failing or missing tests, setup failures, and missing evidence. Never invent a cause or call a changed baseline hash a defect.

The pure functions and command interface in `maintenance/alert_policy.py` are the authoritative classification and state-transition rules. Obtain their current source before using them. The `plan` function accepts retrieved runs, policy, saved state, and reports keyed by run ID. It retains an open problem across new runs, uses stable keys based on the check and error, and creates a new episode only after recovery. A fully healthy check is required before reporting recovery; a proposed fix is insufficient. Reports and tests cover repository maintenance, not all live uses of every skill.

## Preserve the alert record

Read `alert-state.json` from the existing `skill-alert-state` branch in this same private repository. This branch stores runtime delivery state, not a second skill source. Never reset a missing or unreadable record to an empty state. Never write runtime state to `main`.

Use the current GitHub file or branch revision as a compare-and-set condition for every write. If another writer changed it, reload and recompute. Save planned events before attempting delivery. Before sending a pending event, use `claim_event` with a unique claim ID, save that claim conditionally, and read it back. Only the successful claimant may send. A claimed event from a previous attempt requires reconciliation, not another send. If the environment cannot persist and read back state, stop sends and repair writes; record the blocker once in this task's existing chat, using previous task messages to avoid another notification for the same blocker.

Every event uses `SKILL-CHECK:<event_id>` as its stable message marker. Check the saved receipt and the authorized Slack channel for that marker. Reuse a matching message. If a send times out or delivery is uncertain, leave the event claimed and reconcile the channel before doing anything else. Do not blindly retry, send a duplicate fallback, or create another event ID. An explicitly rejected send can be retried only after confirming no message exists, recording the rejection, and conditionally returning the claim to pending; allow at most three confirmed failed delivery attempts per event. Never reset that count across runs.

After reading back the delivered message, use `acknowledge` and save its verified permalink or message receipt. Persist a recovery event the same way. A problem that resolved before its first alert was sent does not need an opening or recovery message. Healthy unchanged observations remain quiet.

## Deliver only to the existing destination

Use La Maison Santa Barbara workspace `T0AT819U2UQ`, connection `link_6acb11be38d48191845021d2cc6cd53b`, and channel `C0C7XQK3TTR` (#automations) for Slack reads and sends. Never substitute XRAY or a direct message. Keep each opening or recovery message short: the observed issue or fix, its impact, a direct GitHub run or source link, and one next step if action is needed. Keep client records, credentials, and raw logs out of Slack.

Use the existing task chat as fallback only after a definite Slack delivery failure and no matching Slack message. Claim and record that fallback against the same event. Do not also notify in ChatGPT after verified Slack delivery. If delivery is uncertain, record the uncertainty without claiming that the alert was delivered. Never return a routine completion message for a healthy, unchanged run.

## Preserve the repair boundaries

For a confirmed code, skill, test, or documentation problem, read repository instructions and compare the failing commit with current main. Reuse any existing repair branch or draft pull request. Keep a stable issue key and save each attempt before working. Allow at most three attempts per unresolved problem across scheduled runs. Missing access, evidence, permissions, or required tools are reasons to stop, not controls to bypass.

Use synthetic tests. Reproduce a confirmed bug, add a regression where needed, and run the full Skill checks command. Do not weaken validation to get a passing result. Save the proposed change and its evidence in a draft pull request; include the problem, behavior, tests, limits, and rollback. Do not merge, enable automatic merging, write repairs to main, adopt releases, change installed copies, change business systems, or create more schedules. Keep proposed repair and recovery separate. Repair progress belongs in the existing GitHub record and does not generate another alert.
