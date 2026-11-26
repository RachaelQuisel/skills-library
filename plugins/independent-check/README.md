# Independent Check: A Gate That Can Fail

Guard an automated job with a check that can actually fail it.

Give the plugin one automated job, one acceptance sentence in the customer's words, one never sentence, and one external standard the checker measures against. It ships a working gate - an executable script - plus a planted bad fixture that must fail and a good fixture that must pass. Rehearse both in front of the maker before the real traffic runs.

- Writes the fences (acceptance sentence, never sentence, external standard) before the work.
- Ships a runnable checker that reads the product itself, not the maker's summary of it.
- Fails a planted bad example in private on demand, so the green lights mean something.
- Refuses completion claims that have no fresh verification evidence.
- Writes a timestamped blocker report to a local file on every gate trip. Alert routes beyond that are opt-in.

## How it works

1. Answer four questions about the automated job: what it is, what good looks like in the customer's words, what it must never do, and what the checker measures against.
2. The plugin saves those answers into a `check.json` config alongside the product and the external standard.
3. It runs the shipped checker against a planted bad fixture and a known-good fixture. The bad one must fail. The good one must pass. If either outcome is wrong, the rehearsal itself fails.
4. It explains what the check now gates, what it only prepared, and which assertions are still decorations.

## Trigger

Use the plugin when someone is building, maintaining, or auditing an automated job that has not yet failed a planted bad example in private; when they are about to say work is done, fixed, or passing and want that claim gated behind evidence; or when they ask to design acceptance criteria, a never sentence, a blocker alert, or a rehearsal for an automation they already run.

## Inputs

- One automated job (described in one sentence, by cost of being wrong in public, not by how often it runs).
- An acceptance sentence in the customer's words.
- A never sentence. One unacceptable outcome that fails the check at any average.
- An external standard the checker measures against: a JSON file, a text file, a record exported to disk, a facts file with its date. Must not be written by the maker.
- A named human who gets the blocker alert, and the time budget for them to see it.

## What happens

1. The plugin inventories the job's current check, if one exists, and asks what bad example it has ever caught.
2. It writes the acceptance sentence, the never sentence, and the standard's location into a `check.json` config in the job's folder.
3. It drafts the assertion list from the never sentence. Every gate assertion gets `"gate": true`.
4. It copies the shipped `fixtures/good/` and `fixtures/bad/` into the job's folder and adapts them to the job's own standard.
5. It runs `scripts/rehearse.sh`. The good fixture must exit 0; the bad fixture must exit 2. On any other outcome, the rehearsal fails and the plugin reports why.
6. On a failure of the real check, `scripts/check.py` writes a timestamped blocker report under `./alerts/`. Any external alert route (Slack, email, GitHub issue) is wired only with explicit approval and verified against a test destination first.
7. Before any "done", "fixed", "passing", or "working" claim, `scripts/verify_claim.py` reads a fresh evidence file and refuses the claim if it contains hedge words, if the evidence is stale, or if the observed exit code does not match the expected one.

## Outputs

- A `check.json` config co-located with the product and the standard.
- A rehearsed pair of fixtures - one that must fail, one that must pass - with the exit codes observed in front of the maker.
- Timestamped blocker reports under `./alerts/` on each failing run.
- A plain-English report naming what was tested live, what was only prepared, and which assertions are still decorations.
- An approved or refused verdict on completion claims, backed by a fresh evidence file.

## Control and limitations

- The checker reads product and standard files the host can read. It does not log into live databases, Airtable bases, Google Sheets, or external APIs. For those sources, the user exports a snapshot and points the checker at the snapshot. The export is the user's step.
- The gate runs when it is called: from a CLI, a CI job, a pre-commit hook, or a scheduled task the user wires. It does not intercept arbitrary completion claims, status writes, or tool calls from an unrelated agent. A stop hook is self-attestation; the plugin never presents a stop hook as an independent outcome check.
- The default alert destination is a local Markdown file. Slack, email, and GitHub issue routes are opt-in, drafted locally, dry-run against a test destination, and fired live only after the user says to.
- After three consecutive failed repair attempts on the same check, the plugin stops and reports instead of retrying.
- A passing fixture run proves the checker's assertions do what they say. It does not prove that a live integration works.
- Installing the plugin does not start a scheduled check or a monitor. Those are separate setup steps the user owns.

See [the shipped assertion kinds and what is out of scope](skills/independent-check/references/honest-limits.md).

## Installation

This repository is private. Install only from an account that already has access.

```text
claude plugin marketplace add RachaelQuisel/Skills
claude plugin install independent-check@rachael-quisel-skills
claude plugin details independent-check
```

Or load from disk for local development:

```text
claude --plugin-dir /path/to/plugins/independent-check
```

Invoke `/independent-check:independent-check` or ask for a check that can actually fail an automated job. A newly installed skill may require a new Claude Code session before it appears.

## Try the shipped rehearsal

```bash
cd plugins/independent-check
bash scripts/rehearse.sh
```

The script runs the shipped checker against `fixtures/good/` (must pass) and `fixtures/bad/` (must fail). The planted bad fixture breaks the never sentence in four ways: an invented dollar amount, two unpromised dates, another customer's job name, and a unilateral discount phrase. The good fixture leaves all of those untouched.

## Data handling

See [PRIVACY.md](PRIVACY.md). This package contains instructions and executable local scripts only. It does not include a publisher-operated server, a hook, or a background process. Scripts read local files and write local alert files. External alerts require an opt-in route the user configures and verifies.

## Package status

Version 1.0.0. Private and proprietary. The shipped rehearsal has been run against both fixtures and produces the expected exit codes (0 for good, 2 for bad). Local validation only; no directory submission has been made.
