# Verification and return

## Choose evidence appropriate to the change

Read the package/lockfile and compile against the actual Airtable SDK declarations. Test meaningful behavior, not text that happens to appear in the implementation. For mutation logic, useful fictional cases include failure, delayed/uncertain acknowledgement, repeat action, permissions, reassignment, existing attachments, exact links, duplicate reuse and filtered totals.

Use fictional records in local browser fixtures. Check desktop/mobile visuals, keyboard targets, reduced motion, long labels and large scrollable sections as relevant. Review test harness assumptions when results conflict with the actual product; a broken mock or serializer can produce a false conclusion.

Run the checks required by the change. After they pass, expand or repeat testing only when a new change/failure warrants it. A copied DOM control, mock save or opened upload dialog does not prove a live record change or binary upload. Record those boundaries plainly.

For authorized live write tests, use a clearly agreed fixture or target and verify exact persisted fields/links/attachments afterwards. Do not complete real staff work or attach a test file to a real family merely to demonstrate an interface. Stop at read-only verification when live mutations are outside scope.

## Preserve and return the exact source

1. Identify the actual base, page, custom element and version. Preserve previous complete source and version snapshots before replacement; use a separate page/version when requested or necessary for recoverability.
2. Read the current editor source through the supported UI or verified deployment route. A local build does not update Airtable. Do not fabricate an export, assume a local deploy command publishes the selected element, or use undocumented internal mutation endpoints.
3. Return the entire raw TSX. Exclude Markdown fences, patch markers and `@@` headers. Use the complete assembled source, not a stale partial fragment. Copy/paste text through supported browser/clipboard APIs where available.
4. Save and wait for the actual success/build result. Reload, inspect the render, reopen the editor and obtain its complete saved text independently.
5. Compare exact readback to the delivered file. The bundled [source_receipt.py](../scripts/source_receipt.py) reports byte sizes and SHA-256 without printing source content. A matching hash establishes file equality, not SDK correctness or live persistence.
6. Check Data settings and per-table actions as well as code. Native document details need an editable visible attachment field; preserve shared layouts by copying before refinement.
7. Publish when the user's scope authorizes it. Check the resulting live/collaborator URL and controls, rather than reporting success from a Publish click or creator preview.

From the skill folder, run this offline command with the two actual local paths:

```sh
python3 scripts/source_receipt.py --source delivered-source.tsx --readback saved-source-readback.tsx
```

An exact mismatch exits nonzero. Do not silently normalize whitespace or line endings to make the receipt pass. Investigate truncation, wrong version, browser transfer and genuine source changes.

## Diagnose the failing layer

- Missing data warning: excluded table/field, wrong mapping/type or not-yet-loaded records.
- Save failure: permission, incompatible field payload or stale eligibility.
- Invisible attachment area: record-detail layout and field editability.
- Source editor fails to load: the editor/export/browser route, not necessarily TSX.
- Build failure: exact SDK/import/type declarations and dependency/lockfile consistency.
- Test-only failure: mocked capabilities, serializers and fixture assumptions.

Prefer the direct supported route that works. Changing browser after a diagnosed editor loading issue can be appropriate; bypassing security or repeating the same failing action is not a fix. Use current UI state and actual errors to guide the next step.

## Deliver a truthful checkpoint

Record source/version/hash, preserved original, target IDs, checks and exact state: edited locally; returned and read back; saved/rendered; published; record/file write verified. Keep those claims separate. A successful earlier checkpoint does not certify later code, and stale README wording should not override a newer explicit installation/publication record.

Retain local proof screenshots after web changes and show a useful screenshot with the final result. Keep real family pixels, identifiers and signed attachment URLs outside public Git and plugin archives. Use sanitized notes and fictional preview images for distributable artifacts.

If the user wants a short how-it-works explanation, use Trigger, Inputs, What happens and Outputs with current status and the actual remaining step. Do not claim an installed plugin is loaded in the current/fresh chat until that surface is verified.
