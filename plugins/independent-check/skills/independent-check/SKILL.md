---
name: independent-check
version: 1.0.0
description: Guard an automated job with an executable gate that can actually fail it. Write the acceptance sentence in the customer's words, write the never sentence, name the external standard the checker measures against, ship a planted bad fixture that must fail and a good fixture that must pass, rehearse both in front of the maker, and refuse completion claims that have no fresh verification evidence. Use when someone is building, maintaining, or auditing an automated job that has not yet failed a planted bad example in private; or when they are about to say work is done, fixed, or passing and want that claim gated behind evidence; or when they ask to design a check, acceptance criteria, never sentence, blocker alert, or rehearsal for an automation they already run.
---

# Independent Check: A Gate That Can Fail

## Purpose in plain English

This skill gives an automated job a check that can actually fail it. It sets the fences before the work runs, measures the product against a standard outside the maker, and keeps a planted bad example on hand that the checker has to catch in front of you before its green lights count. It also refuses to let the agent claim work is complete without fresh verification evidence.

## Three sentences to say before touching code

Keep these taped to the top of the plan. They decide what the plugin will do next.

1. **Check the product, not the story about the work.** The checker reads the output file, record, or command result directly. It never reads the maker's summary of its own job.
2. **Averages negotiate. Gates do not.** Some failures stop the line at any score. The `never` sentence is a gate, not a grade.
3. **A check you have never seen fail is a decoration.** The planted bad example runs before the real traffic does.

## When to use this skill

- The user is building a new automation and wants acceptance criteria written before the build.
- The user says a job is "self-checked" today (same model, same conversation, same instructions makes the summary) and wants an outside check added.
- The user is about to claim something is `done`, `fixed`, `passing`, `working`, or `shipped` and wants the claim gated by fresh evidence.
- The user asks to design a blocker alert, a rehearsal, or a never sentence for an automated job they already run.
- The user wants to audit an existing checker and find out what bad example it has ever caught.

## Start the conversation (ask up to four questions)

If the request has no details, ask:

1. "Which automated job should the check guard? Name the one job that would hurt most if it were wrong in public."
2. "What does good look like in your customer's words, in one sentence?" (acceptance sentence)
3. "What is the one thing this job must never do, at any average score?" (never sentence)
4. "What standard outside the maker can the checker measure against? A record, a price list, a calendar, a facts file. Where does it live?"

Wait for the answers; preserve them verbatim. Use them in the plan. Do not invent a never sentence on the user's behalf.

## Follow this process

### 1. Write the fences before the work

- Save the acceptance sentence, the never sentence, and the external standard's location into a `check.json` config in the same folder as the product. The `scripts/check.py` runner in this plugin reads that config. See `examples/weekly-update/check.json` for the shape.
- The acceptance sentence names what good looks like for a real customer.
- The never sentence is a single gate. The runner treats any assertion tagged `"gate": true` as a hard fail (exit code 2).
- The standard is a file or record the maker did not write: a customer record, a price list, a calendar entry, a facts file with its date.

### 2. Ship a working checker, not instructions

Hand the user a check that runs. The plugin provides:

- `scripts/check.py --config <path-to-check.json>` - loads the standard, loads the product, runs each assertion, exits 0 (pass), 1 (quality fail), or 2 (gate tripped). On failure it writes a timestamped blocker report under `./alerts/`.
- `scripts/rehearse.sh` - runs the checker against the good and bad fixtures and fails the rehearsal itself if either outcome is wrong.
- `scripts/verify_claim.py --claim ... --evidence ...` - the completion-claim gate. See step 6.
- Fixtures under `fixtures/good/` and `fixtures/bad/` - demonstrated to work before the real check ever runs on production.

The supported assertion kinds are listed in `references/honest-limits.md`. When the user's job needs a check kind that is not listed there, say so plainly and add it in the user's own fork rather than claiming the plugin already handles it.

### 3. Plant the bad example on purpose

- Copy the good fixture into the user's job folder and name the thing their never sentence forbids. Change one value so that one assertion must fail. Save it under `fixtures/bad/`.
- Add the `gate: true` flag on the assertion that catches that specific bad example.
- Run `scripts/rehearse.sh` once, in front of the user. The rehearsal must show:
  - the good fixture produces exit code 0, and
  - the bad fixture produces exit code 2 (gate tripped).
- If either outcome is wrong, the rehearsal fails. Do not claim the check is installed. Fix it, then rehearse again.

### 4. Name the honest limits out loud

Read `references/honest-limits.md` and bring the relevant lines into the user's `check.json` folder as a short `README.md`. Do not oversell what the checker can read or what the gate can run. Specifically:

- Name the standard-source types supported today (JSON file, text file). If the user's source is an Airtable record, a Google Sheet, or an API, the user exports it first and the checker reads the export. Say so.
- Name what the gate cannot do. It does not intercept arbitrary agent completion writes, status writes, or tool calls. It is a script that runs when it is called.
- A stop hook is self-attestation. A scheduled run of `check.py` with real input is an independent outcome check. Say which is which; never present one as the other.

### 5. Design the alert route; do not fire a live test without the user's say-so

- Default behavior: on gate trip, `check.py` writes a blocker report under `./alerts/<timestamp>-blocker.md`. No external send. The user reads it.
- Only when the user explicitly says to wire Slack, email, or another destination, read `references/alerting.md` and propose the route. Say where credentials live (environment variables in the host, not in `check.json` or chat).
- Verify the route with a `--dry-run` that writes a would-send message to a file, and ask the user to confirm the message before any live send.
- A live alert test fires only after the user says to fire it.
- After three consecutive gate trips with no human acknowledgement, stop re-sending and surface a stale-run notice instead.

### 6. Gate completion claims behind fresh verification evidence

Use `scripts/verify_claim.py` before any "done", "fixed", "passing", or "working" claim. Procedure:

1. Identify the command that proves the claim, in plain words. ("`pytest -q` must exit 0", "`curl -sSf https://example.com/healthz` must return 200".)
2. Run the proof command fresh. Do not reuse an earlier session's output. Capture `exit_code`, `stdout`, `stderr`, and the UTC `timestamp` into a JSON evidence file.
3. Run `python3 scripts/verify_claim.py --claim "<claim>" --evidence <path-to-evidence.json> --expected-exit 0`.
4. The script refuses the claim if any of:
   - the claim contains a hedge word (`should`, `probably`, `seems to`, `appears to`, `likely`, `might be`, `I think`);
   - the evidence is older than the max age (default 300 seconds);
   - `exit_code` does not match the expected code;
   - the evidence is missing a `proof_command`, a `stdout`/`stderr` capture, or a `timestamp`.
5. If the script refuses, state the claim as unverified. Do not report completion.

Adapted from the superpowers public skill at https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md . The addition here is that the evidence lives in a file the user can review.

### 7. Report the result in plain words

After the rehearsal and the first real run, tell the user:

- What was tested live (name the fixtures, the assertions, the exit codes).
- What was only prepared (an alert route not yet wired, an assertion kind added but not rehearsed).
- Which sentences the check now gates (quote them back).
- Which checks are still decorations (the ones that have never been seen to fail).

## Boundaries

- Separate what was tested live from what was only prepared. Never describe an untested check as "working".
- After three failed repair attempts on the same check, stop and report. Hand it back to the named human.
- Ask before any write, send, or spend outside the user's working folder. Local files under the plugin and under the user's job folder do not require per-write confirmation.
- Credentials for an alert route stay in the host's supported secret store. They do not go into `check.json`, SKILL.md, or chat.
- The plugin reads what the host can read; it inherits the host's permissions. It does not add a publisher-operated service.

## References

- [verification-before-completion.md](references/verification-before-completion.md) - the full claim gate and its failure modes.
- [honest-limits.md](references/honest-limits.md) - supported job types, supported standards, supported destinations, and what the gate cannot do.
- [alerting.md](references/alerting.md) - how to wire a destination with the user's say-so and verify it before claiming notifications work.
- [writing-your-never-sentence.md](references/writing-your-never-sentence.md) - a short worksheet for the first conversation.
