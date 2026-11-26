<!-- preflight-allow: documents-scanner-patterns -->

# Verification before completion

Adapted from the public skill at https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md . The plugin ships this as an executable gate at `scripts/verify_claim.py`, not only as a prose rule.

## The rule

Before claiming any work is complete, fixed, or passing:

1. Identify the command that proves the claim, in plain words.
2. Run that command fresh and in full.
3. Read the whole output, including exit code and failure counts.
4. Only then make the claim, with the evidence attached.

Without those steps, report the claim as unverified. Never approve the claim because another session finished successfully, because the lint passed, because the build logs look clean, or because the model remembers the test suite was green a few turns ago.

## What stops the claim

- The claim contains a hedge word. `should`, `probably`, `seems to`, `appears to`, `likely`, `might be`, `I think`. Any of them means the claim is not ready.
- The evidence file is missing a `proof_command`, a `stdout`/`stderr` capture, or a `timestamp`.
- The evidence `timestamp` is older than the configured maximum age. Default 300 seconds. A command whose output is five minutes old is not proof of what is true now.
- The observed `exit_code` does not match the expected exit code for the claim.
- The evidence timestamp is in the future (clock skew or forged evidence).

## What is never sufficient evidence

- A previous session's run of the proof command.
- A partial run (only a subset of the test suite, only the "quick" cases).
- Another agent's success report. ("The reviewer agent says the code is good.")
- The absence of an error in the chat buffer. (Silence is not proof.)
- A stop hook or a self-written completion log. Those are self-attestation by the maker. The point of this gate is independence from the maker.

## Evidence file shape

The evidence file is JSON. The agent (or the user) writes it fresh after running the proof command.

```json
{
  "proof_command": "pytest -q tests/test_payments.py",
  "exit_code": 0,
  "stdout": "...tail of the captured stdout...",
  "stderr": "",
  "timestamp": "2026-11-18T14:23:00Z"
}
```

A stable way to produce it in a shell:

```bash
set +e
OUT=$(pytest -q tests/test_payments.py 2>&1)
RC=$?
set -e
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
jq -n \
  --arg cmd "pytest -q tests/test_payments.py" \
  --arg out "$OUT" \
  --argjson rc $RC \
  --arg ts "$TS" \
  '{proof_command: $cmd, exit_code: $rc, stdout: $out, stderr: "", timestamp: $ts}' \
  > evidence.json
```

If `jq` is not installed, write the JSON with `python3 -c`. Do not hand-edit the file; generate it from the actual run.

## Calling the gate

```bash
python3 scripts/verify_claim.py \
  --claim "the payments test suite passes on current main" \
  --evidence evidence.json \
  --expected-exit 0 \
  --max-age-seconds 300
```

Exit codes:

- `0` - claim approved.
- `1` - claim refused with reasons.
- `3` - config problem (missing evidence file, malformed JSON).

## When the gate refuses

- Do not retry with a looser claim or a looser max-age.
- Fix the underlying problem: re-run the proof command fresh, rewrite the claim without hedges, or correct the expected exit code.
- A claim that fails this gate on the third repair attempt stops here. Report the refusal in plain words and hand it back.
