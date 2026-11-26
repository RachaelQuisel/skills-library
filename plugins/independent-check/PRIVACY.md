# Data handling

Independent Check is an instructions-and-local-scripts plugin. It has no publisher-operated service, no telemetry, and no bundled background process.

## What the scripts read

- `scripts/check.py` reads the config file the user points it at, the external standard file named in that config, and the product file named in that config. All three are local paths under the user's working directory.
- `scripts/verify_claim.py` reads the evidence file the user points it at. The evidence file is a local JSON path.
- `scripts/rehearse.sh` reads the plugin's own `fixtures/good/` and `fixtures/bad/` folders.

The scripts make no network requests. They read no credentials. They do not read files outside the paths explicitly passed as arguments.

## What the scripts write

- `scripts/check.py` writes a timestamped Markdown blocker report under `./alerts/` when a check fails, unless `--no-alert` is passed. The report names the failing assertions and quotes the acceptance and never sentences from the config.
- `scripts/verify_claim.py` writes nothing to disk. It prints the verdict to stdout and exits 0 or 1.
- `scripts/rehearse.sh` prints the two check runs' output to stdout and exits 0 or 1.

## What the host may read when assisting

When a user asks the plugin to set up a check, the host may read skill instructions, the user's product files, the user's external standard files, failure reports, and any evidence files the user supplies. Those materials can contain personal, client, operational, or confidential information. The user is responsible for what they route through the checker.

## Alert destinations beyond the local file

The plugin's default alert is a local file. Any external destination (Slack incoming webhook, SMTP email, GitHub issue) is configured per-install by the user, drafted locally, verified against a test destination first, and fired against the live destination only after the user says to. Credentials for those routes stay in the host's supported secret store. They do not go into `check.json`, SKILL.md, or chat. Those third-party services process the sent content under their own terms.

## Retention

Local files remain in their respective destinations until removed under those systems' retention rules. The plugin adds no separate storage service or telemetry. Deleting a blocker report removes it from disk. Credentials are revoked through the service that issued them.

## Host permission limits

The host's enabled tools and permissions determine which actions the plugin can take. The plugin inherits the host's permissions; it does not widen them. These are instructions and scripts, not technical access controls.

## Contact

Through the repository's [issue tracker](https://github.com/RachaelQuisel/Skills/issues).
