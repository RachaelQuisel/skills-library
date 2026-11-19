# Save and publish without duplicates

## Boundaries

Resolve business identity from project/account evidence. Resolve Slack workspace and channel IDs from the service. Compare them with an approved route. Channel names alone are insufficient. Cross-business search permission is not cross-business sharing permission.

Keep a private ledger per business. A combined private register needs explicit approval and an appropriate audience. Route fields are records of independently checked authority, not permission grants. Never set approval fields just to pass a validator.

## Documents

Find guides by workflow ID, entry-point path and aliases. Reuse the canonical file and read its latest contents. Correct contradictory current guides or clearly mark them superseded with a link. Retain dated historical records.

Read current Git state. Follow branch rules and use expected revisions. Reconcile changed heads; never force over another writer. Save non-repository artifacts in durable document storage. A scratch file or download link alone is not a completed save.

## Slack actions

| Condition | Action |
|---|---|
| No posting authority | Save a draft and report not posted. |
| Business, audience or route unclear | Hold that item and ask one focused question. |
| Same content in an existing message | Leave it unchanged. |
| Changed content in an owned message | Edit in place. |
| No existing message after checking | Create one guide in the approved index thread. |
| Cannot edit | Use an authorized linked replacement. |
| Request timed out | Read/search for its result before retrying. |
| Partial failure | Keep successful receipts and report unfinished work. |

Record identity, file path, content hash, immutable URL, business/workspace/channel IDs, message ID and outcome. Update publication hashes only after successful writes and readback. Retain failure evidence and record corrections separately.

Do not delete messages or files during deduplication. Do not post a combined client catalog in one client's channel. Use each workflow's approved failure destination.

## Scheduled use

The plugin installs no scheduler or server. If recurring runs are requested, use the host's supported cloud automation service. Verify scope, routes and enabled status. Scheduled runs hold ambiguous writes and report gaps without waiting for live input. Do not claim the computer can sleep until the actual hosted setup is verified.
