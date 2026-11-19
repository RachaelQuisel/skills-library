# Airtable Schema Contract

Read this file before accessing Airtable. This repair uses one fixed upstream base
and one optional client project-management base. Treat every upstream identifier
as an expected value. Verify each value live with `tasks-xray-tech` before reading
task data or making an update.

## Contents

- Credential routing
- Base routing
- Expected upstream schema
- Mismatch query
- Allowed mutation boundary

## Credential routing

- `tasks-xray-tech`: required Airtable CLI profile backed by the tasks.xray.tech
  PAT. Use it for upstream base discovery, schema reads, task and meeting reads,
  manifest-listed Tasks updates, and read-back verification.
- `project-management`: optional Airtable CLI profile backed by the Project
  Management PAT. Use it only to discover and read the named client's XRAY
  project-management base and meeting interface.
- Never place PAT values in commands, logs, reports, this file, or `SKILL.md`.
- Never ask the user to paste a PAT into the conversation.
- Check profile availability with `whoami` output redirected to `/dev/null`.
  Report only whether the named profile is configured or unavailable.
- Stop without upstream task reads or writes when `tasks-xray-tech` is missing.
  Continue without the optional interface check when `project-management` is
  missing.

Every Airtable CLI command must include an explicit profile:

```sh
airtable-mcp <upstream-read-tool> --profile tasks-xray-tech ...
airtable-mcp update-records-for-table --profile tasks-xray-tech --input - -q
airtable-mcp <client-read-tool> --profile project-management ...
```

Never omit `--profile` during discovery, retries, or verification.

## Base routing

### Upstream repair base

- Name: `Projects & Tasks at XRAY`
- ID: `appQAdxI2hDNJj1g5`
- Credential: `tasks-xray-tech`
- Purpose: find mismatches, prove client ownership, update `Debrief Tasks`, and
  verify every update

### Client project-management base

- Credential: `project-management`
- Purpose: optional read-only confirmation that repaired tasks appear on the
  client's meeting page
- Resolution: search accessible bases for exactly one name containing XRAY and
  the canonical client name or approved abbreviation, in either order
- Known client terms: `Coding Clarified`; `Guardians of Love` or `GOL`; `CCRES`
- Do not hard-code the client base ID. Report the exact live name and ID when one
  base resolves.
- Do not update a client project-management base; its task data is a viewing layer.
- Treat zero or multiple base matches as an unavailable interface check. Do not
  guess. This does not block an upstream repair that passed client-ID scope checks.

## Expected upstream schema

| Object | Expected name | ID | Required type or target |
| --- | --- | --- | --- |
| Base | Projects & Tasks at XRAY | `appQAdxI2hDNJj1g5` | Exact name/ID pair |
| Table | Tasks | `tblvlJq7I2GvIQEyP` | n/a |
| Table | Debrief Recordings | `tblYLGhD3Ii7EkGZY` | n/a |
| Table | XRay's Clients | `tblVS1aUCNeqtVq5U` | n/a |
| Tasks field | Debrief Recordings | `fldmzmZy2D1yh5B7p` | `multipleRecordLinks` to `tblYLGhD3Ii7EkGZY`; inverse `fld7GZxz1qvjcm8vq` |
| Tasks field | Debrief Tasks | `fldXbCPMQBosF9Vre` | `multipleRecordLinks` to `tblYLGhD3Ii7EkGZY`; inverse `fld323h3XdO5zI941` |
| Debrief reciprocal | Source-task backlink | `fld7GZxz1qvjcm8vq` | `multipleRecordLinks` to `tblvlJq7I2GvIQEyP`; inverse `fldmzmZy2D1yh5B7p` |
| Debrief reciprocal | Meeting-page task backlink | `fld323h3XdO5zI941` | `multipleRecordLinks` to `tblvlJq7I2GvIQEyP`; inverse `fldXbCPMQBosF9Vre` |
| Debrief field | XRay's Client | `fld9YZme9QfpVSYgm` | `multipleRecordLinks` to `tblVS1aUCNeqtVq5U`; require one value at runtime |

## Mismatch query

Request both Tasks link fields and page through all results:

```json
{
  "operator": "and",
  "operands": [
    {"operator": "isNotEmpty", "operands": ["fldmzmZy2D1yh5B7p"]},
    {"operator": "isEmpty", "operands": ["fldXbCPMQBosF9Vre"]}
  ]
}
```

Use returned linked-record `id` values for comparisons and writes. Names are
evidence for people and must not determine scope.

## Allowed mutation boundary

- Base: `appQAdxI2hDNJj1g5`
- Table: `tblvlJq7I2GvIQEyP`
- Field: `fldXbCPMQBosF9Vre`
- Records: only task IDs in the revalidated, client-scoped manifest
- Value: exactly the unchanged source meeting ID set from
  `fldmzmZy2D1yh5B7p`

Discover current tool names and access classifications before use. Treat
`update-records-for-table` as destructive. Airtable replaces the linked-record
field's complete value. Populate only a freshly reverified empty target. Send one
task per request unless the discovered tool offers a conditional revision check.
