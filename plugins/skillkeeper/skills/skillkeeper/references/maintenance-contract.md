# Maintenance contract

Use this contract to design or inspect a maintained skill collection.

## Inventory

Each registered skill needs:

- a stable identifier and repository path;
- a named responsible owner;
- an immutable baseline commit and content hash;
- declared supported hosts, models, APIs, and permissions;
- a last verified compatibility date with an evidence link;
- registered regression case identifiers;
- a maintenance README.

Empty compatibility fields mean unverified. Changed content is a review signal, not an automatic failure or approval.

## Regression evidence

Each case needs a stable identifier, suite location, expected outcome, sanitized fixture, and evidence output. Missing, skipped, failed, or uncollectable required cases make the result non-passing. New tests may run automatically, but required case identifiers prevent old coverage from disappearing silently.

Tests must distinguish offline behavior from live host and API compatibility. Record test setup failures separately from failed assertions.

## Releases

Each approved release record needs:

- the new and previous immutable commits;
- the reason for change;
- regression cases run and their evidence;
- live compatibility evidence, if any;
- known limits and unresolved risks;
- approving owner and approval date;
- rollback target.

Adoption is explicit. A moving default branch is not a pinned installed version.

## Workflow

Run checks on pull requests, accepted changes, manual requests, and a periodic schedule. Save a readable summary, structured results, and test logs. Retain durable release evidence in version control even when build artifacts expire.

If setup fails before evidence exists, report the result as unknown. Artifact upload failures must remain visible.

## Support

Name a person responsible for coordinating fixes and a clear intake route. Do not promise a response time or automatic repair unless a staffed service and service-level agreement actually exist.
