# Honest limits

What the shipped checker can read, what it can do, and what it cannot. Keep this current. When a user's job needs something the checker does not support today, add it in a fork rather than widen this list to match the ask.

## Supported standard-source types (where the external standard lives)

- A JSON file on disk. Any nested structure; values are flattened for comparison.
- A plain text or Markdown file on disk.

Out of scope for v0.1.0, by design:

- Airtable record, Google Sheet, Salesforce record, Notion page, HTTP endpoint. For these, export a snapshot to a local JSON file and point the check at the snapshot. The export is the user's step; the check reads the export.
- Live databases (Postgres, MySQL, SQLite). Same pattern: export, then check.

## Supported product types (what the checker reads as the actual product)

- Plain text, Markdown, JSON on disk.
- A command's captured stdout, redirected to a file.

Out of scope for v0.1.0:

- PDFs, Word documents, spreadsheets. Convert to text first (`pandoc`, `pdftotext`, `xlsx2csv`) and check the text.
- Images and video. A visual check is a different plugin; this one does not claim to catch frozen frames or scene-change glitches.

## Supported assertion kinds (shipped with the plugin)

- `all-currency-in-standard` - every `$`-prefixed number in the product must appear as a value somewhere in the standard.
- `all-dates-in-standard` - every `YYYY-MM-DD`, `Month D, YYYY`, or `Mon D, YYYY` date in the product must appear as a `YYYY-MM-DD` value somewhere in the standard.
- `mentions-only-named-job` - the product must name the standard's `job_name` and must not mention any string in `forbid_other_jobs`.
- `required-phrases` - every phrase in `phrases` must appear in the product (case-insensitive).
- `forbidden-phrases` - no phrase in `phrases` may appear in the product (case-insensitive).

Any assertion can be marked `"gate": true`, which turns a failure into exit code 2 (gate tripped) instead of exit code 1 (quality miss).

Out of scope for v0.1.0:

- Numeric-range assertions (`agreed_amount` must be within 5%).
- Fuzzy string match (`levenshtein < 3`).
- Semantic match through an LLM. A separate skill can add this, but then the assertion reads a model's opinion as evidence, which breaks the "standard outside the maker" rule unless the model is explicitly independent.

## Where the gate can run

- From a CLI: `python3 scripts/check.py --config <path>`.
- From a CI job: run the CLI as a step; fail the job on a non-zero exit.
- From a pre-commit hook: the user wires the hook; the plugin does not install it.
- From a scheduled task (cron, launchd, GitHub Actions on a schedule): the user wires it; the plugin provides the executable.

Out of scope for v0.1.0:

- Intercepting arbitrary completion claims, status writes, or tool calls from an unrelated agent. The script is a check that runs when it is called; it is not a kernel hook.
- Stopping an in-flight Zap, Airtable automation, or Make scenario. The gate can be called by those systems if they can execute a shell command; many cannot.

## Where the alert can go

- A Markdown file under `./alerts/<timestamp>-blocker.md`. Always. No external send by default.

With the user's approval, via `references/alerting.md`:

- Slack incoming webhook.
- Email via SMTP.
- GitHub issue via `gh issue create`.

Out of scope until explicitly asked:

- SMS, PagerDuty, Opsgenie, phone calls. These need account setup that is per-user and not shipped here.

## What each shipped assertion will quietly miss

The assertion kinds catch only what their regexes and inputs match. A draft written in a format outside those bounds passes the gate without a flag. Name these limits out loud to the user when wiring the plugin to a real job.

- `all-currency-in-standard` requires a `$` prefix on numbers in the product. A draft that writes `USD 4,800`, `4800 dollars`, or `four thousand eight hundred` produces an empty `product_values` list, which the check reports as "no currency values in product" - a quiet pass. If the real job writes currency in any of those styles, widen the currency regex or switch to a check kind that reads structured fields.
- `all-dates-in-standard` catches `YYYY-MM-DD`, `Month D, YYYY`, and `Mon D, YYYY`. It does not catch `12/15/26`, `15 Dec 2026`, `Dec 15` (year omitted), `Q4 2026`, or `the 15th`. A draft using US-slash dates passes with zero dates seen.
- `mentions-only-named-job` reads the standard's `job_name` and the config's `forbid_other_jobs` list. It does not query the base to find every other customer's current job name. A new customer added after the config was written is not in the list, so a draft that confuses the two customers passes this assertion unless the config is updated too.
- `required-phrases` and `forbidden-phrases` are literal substring matches, case-insensitive. A near-miss ("no charge for this" caught; "no-charge add-on" not caught because the hyphen breaks the match; "free of charge" not caught at all) does not trip.

For each real job, write a bad example that exercises these edges, run the rehearsal, and widen the assertion kind or add a new one if the planted bad example waves through.

## What the plugin never claims

- It does not claim to intercept a completion claim an agent makes in its own chat unless the agent routes that claim through `verify_claim.py`.
- It does not claim a passing fixture run proves a live integration works. Fixture runs prove the checker's assertions do what they say; live correctness still requires real input.
- It does not claim installing the plugin starts a scheduled check or a monitor. Those are separate setup steps the user owns.
- It does not store or send user data. The scripts read local files, write local alerts, and exit.
