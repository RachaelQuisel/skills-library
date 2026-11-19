---
name: airtable-backup-and-migrate
description: Back up an Airtable base (schema + records + attachment bytes) to a local directory. Use whenever the user asks to back up, snapshot, dump, export, or archive an Airtable base, or wants a rollback point before a risky change. Trigger on casual phrasing too ("save a copy of the CC base", "dump appXXX to disk", "I need a snapshot before this migration"). This is the canonical XRAY backup tool; do not hand-roll a one-off dump script when this exists.
license: MIT
metadata:
    version: '0.1.0-mvp'
    author: rachael-quisel (for XRAY CTO)
    created: 2026-08-11
---

# airtable-backup-and-migrate

MVP. One script that dumps an Airtable base to disk. No restore yet — that's a separate build once there's a dev workspace to test against.

## What it does

Given a base ID and a PAT, writes to `<out-dir>/<base-slug>-<UTC-timestamp>/`:

```
schema.json              # every table + field + choice, all IDs
records/tblXXX.json      # one file per table, records keyed by cellValuesByFieldId
attachments/tblXXX/recXXX/<original-filename>    # attachment bytes on disk
MANIFEST.json            # counts + ISO timestamps + base name at backup time
```

Read-only against the source base. Nothing is written to Airtable.

## How to run it

```bash
python ~/.claude/skills/airtable-backup-and-migrate/backup.py \
    --base-id appXXXXXXXXXXXXXX \
    --pat-path ~/.config/xray/xray-backup-pat \
    --out-dir ~/Claude-Work/AIRTABLE-BACKUPS \
    [--min-free-gb 5.0]         # preflight disk-space threshold, default 5 GiB
    [--skip-attachments]        # dump schema + records only, no attachment bytes
```

Stdlib only — no `pip install`. Requires Python 3.10+.

The PAT file contains just the token (`patXXX…`), no header, no whitespace matters (script strips).

PAT scopes needed: `data.records:read`, `schema.bases:read`, `data.recordComments:read` (optional; unused in MVP), on the source base. Best-practice is a base-scoped PAT, not a user-scoped one.

**Disk-space handling.** The script preflights free space on the `--out-dir` partition and refuses to start if less than `--min-free-gb` (default 5 GiB) is available. It also checks free space before every attachment download and aborts cleanly (with a `MANIFEST.json` documenting where it stopped) rather than filling the disk. Use `--skip-attachments` when you only need the schema + record cell data and the base's attachments are too large for available space.

## The five gotchas the script handles for you

These are the traps from `~/.claude/rules/airtable-best-practices.md`. Named here so the CTO sees what the script is protecting against, and so any future hand-rolled variant doesn't lose them.

1. **`returnFieldsByFieldId=true` on every raw REST GET, including pagination.** Without it, records come back keyed by field NAMES. A rename in the Airtable UI later silently breaks any downstream code. The script always passes it and keys the backup JSON by `fld` IDs. (§3 of best-practices — silent-failure trap.)

2. **Attachment URLs expire in ~2 hours.** A backup that stores URLs instead of bytes silently rots inside the same afternoon. The script downloads bytes to disk. URLs are preserved in the JSON for debugging, but the file on disk is the durable form. (§9 of best-practices.)

3. **IDs first, names in parens.** `schema.json` and `records/*.json` are keyed by `tbl`/`fld`/`sel` IDs. Display names are captured alongside for human legibility. Any downstream tool that needs to write back must use IDs.

4. **Rate limit: 5 req/sec per base.** Airtable's documented cap. Script sleeps 0.2s between requests. On HTTP 429, backs off per `Retry-After` (default 30s) once, then aborts if still throttled.

5. **`appQAdxI2hDNJj1g5` is read-only from the outside.** Backing it up is fine (reads are allowed for verification). Restoring TO it is banned per `~/.claude/CLAUDE.md` — writes to that base must go through `tasks.xray.tech/api`. This MVP is read-only so the ban is theoretical here, but any future restore script must enforce it.

## What's NOT backed up (out of MVP scope)

- **Interfaces, automations, views.** Airtable's meta API doesn't expose these programmatically in a restore-able shape. Document manually per client base.
- **Base collaborators / permissions.** Recreate in the UI.
- **Sync configurations.** A synced table's DATA is backed up like any other; the sync relationship itself isn't exposed on the meta API. On a future restore, the destination gets a plain table and the CTO reconnects the sync.
- **Restore.** Deferred entirely. When ready, build against a dev workspace using the two-pass write pattern (records first, then patch linked-record fields to handle circular refs).

## Verification (after backup)

The last line of stdout on a successful run reads:

```
BACKUP OK: base=appXXX tables=N records=N attachments=N bytes=N dir=<path>
```

Exit code is `0` iff every table completed AND every attachment downloaded without a size mismatch. On any failure, exit code is non-zero and the specific table/record/attachment is named in the log.

`MANIFEST.json` is written LAST. **A backup directory without `MANIFEST.json` is presumed incomplete** — do not treat it as a restore source.

## Extending (when the CTO hits a real limit)

The MVP deliberately skips these. Add them when a real use case demands, not before:

- `--resume-from tblXXX` for partial-failure recovery on huge bases
- `--exclude-tables` for filtering
- Per-file sha256 in the MANIFEST (currently: only file counts and total bytes)
- Atomic write (`.tmp` → `rename`) — currently a crash mid-run leaves a partial file
- S3 / GDrive push — use `rclone` or `aws s3 sync` on the output directory
- Cron scheduling — use `launchd` (macOS) or `crontab` pointing at the script
- Restore — separate script; see the gotcha list above for what it has to protect
