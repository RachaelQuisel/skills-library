# Drive storage

Read this before creating, listing, or saving snapshot files. SKILL.md decides when a log is read or written. This file is the Google Drive procedure.

## Create a snapshot file

Load the connected Google Drive tool definitions. Use create_file with parentId, textContent, contentMimeType application/json, and disableConversionToGoogleType true. It cannot update JSON contents; save a new version instead. If this schema is unavailable, report the limitation.

Creating the blank permission-check file uses this same call. Inspect the returned file's actual audience.

## List every snapshot

Before every query or write, search_files with the exact `parentId = '<folder-id>'`, application/json, and title prefix `relationship-memory_`. Follow every pageToken until exhausted, even when a page is empty or smaller than pageSize. Read every matching snapshot; do not substitute a remembered file ID or cached session copy for a live read.

## Save and verify a new head

Re-list immediately before saving to ensure the expected head is still current. Create a uniquely named `relationship-memory_r<revision>_<snapshot-id>.json` in the selected folder. Keep all prior snapshots. Read back the returned file ID, compare its JSON, check its actual audience, and re-list to confirm the unique new head. If search lags or a competing write creates a branch, report “saved, current revision unresolved” until resolved. Do not overwrite, delete, or claim the update is current without verification.
