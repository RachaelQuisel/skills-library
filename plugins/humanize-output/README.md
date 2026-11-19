# Humanize Output

![Humanize Output icon](icon.png)

Improve the copy you already have through a short conversation. Choose the reader, tone, and editing depth. Review each suggestion before it changes your draft.

## Start

- Use Claude Code with Python 3.10 or later.
- Install from this repository:

```text
claude plugin marketplace add RachaelQuisel/humanize-output
claude plugin install humanize-output@humanize-output
```

- Run `/humanize-output:humanize-output`. Paste a draft or select a text file.
- For local development, load this folder with `claude --plugin-dir .`.
- This release's executable workflow has not been verified in chat or cloud Cowork.

## Questions and review

- If information is missing, the plugin asks one question at a time.
- “Who will read this?” sets the intended audience.
- “How should it sound?” sets the tone. You can choose warm, direct, professional, or another tone.
- “How much should I change?” sets the editing depth. Light cleanup keeps the structure. Sentence revisions change sentence wording. Structural changes can reorganize the draft.
- Answers already given are reused. A selected saved checklist can supply the tone. Current answers apply to this draft.
- Ask to skip questions if you want the plugin to use labeled defaults.
- Review the numbered suggestions or a requested rewrite preview. Accept selected edits or explicitly approve the displayed rewrite.
- Change an answer to request new suggestions. Previous approval does not apply to the new version.
- Reject an edit to keep its original wording. Cancel to end the edit pass without writing a revision.

This example uses fictional text:

> User: Improve “It's worth noting that our workshop starts Friday.”
>
> Plugin: Who will read this?
>
> User: Our customers.
>
> Plugin: I’ll use wording for your customers. How should it sound?
>
> User: Warm.
>
> Plugin: I’ll use a warm tone. How much should I change? Choose light cleanup, sentence revisions, or structural changes.
>
> User: Light cleanup.
>
> Plugin: 1. Remove “It's worth noting that.” This opening adds no information. Suggested version: “Our workshop starts Friday.” Would you like to apply edit 1?
>
> User: Apply 1.
>
> Plugin: The revision is saved in a new file. Friday is unchanged.

Read [how it works](scripts/2026-10-03-humanize-output-how-it-works.md) for the complete process and error paths.

## Saved preferences and data

- Saving a voice checklist is optional. Writing samples are optional.
- The plugin asks you to review proposed rules before saving them. An explicit request to save supplied rules counts as review.
- A checklist without writing samples records chosen preferences. It is not a learned personal voice.
- Profiles stay under `~/.local/share/de-slop/profiles/` by default. Choose another directory with `--data-dir`.
- Saving an existing `profile_id` replaces that checklist. See [the tool reference](skills/humanize-output/references/editing-tools.md) for exact fields and commands.
- Claude reads the drafts and profiles you select. Claude's account data handling applies.
- The bundled tool works with local files. It makes no network requests. It sends no drafts to another humanizer service.
- Public plugin files contain no user drafts or profiles.

## Checks and limits

- The phrase scan finds common writing patterns. Claude proposes the edits and reviews changes in meaning.
- Names, dates, and other required wording are protected phrases. The tool also checks numbers and quotations.
- Literal checks do not prove that every nuance stayed the same.
- Accepted edits go into a new file. The original file and existing outputs are not overwritten.
- The final scan lists remaining issues, including rejected phrases that still match a check.
- Humanize Output evaluates writing quality. It does not determine whether artificial intelligence wrote the text.

## Development and license

- Validate the plugin manifest with `claude plugin validate .claude-plugin/plugin.json`.
- Validate the marketplace with `claude plugin validate .claude-plugin/marketplace.json`.
- Run checks with `python3 -m unittest discover -s tests`.
- The MIT license covers the original plugin code and instructions. Users retain responsibility for their writing and third-party material.
