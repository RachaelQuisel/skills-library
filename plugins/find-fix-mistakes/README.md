# Find & Fix Mistakes

An evidence-based review and repair workflow for prior assistant work, illustrated by a tiny smiling eraser clearing a pencil scribble.

## Included skills

- **Mistakes** reviews the request, evidence, actions, and claimed results. It hands substantiated findings to the bundled Fix Mistakes skill in the same turn.
- **Fix Mistakes** corrects authorized errors, verifies the saved result, and reports each finding as fixed and verified, already corrected, or blocked.

Invoke Mistakes to run the complete workflow. Ask for an audit only when you want findings without changes. Invoke Fix Mistakes directly when an audit already exists. Hosts expose their own skill or plugin pickers; typing a slash command alone does not establish that a plugin is installed.

Explicit user instructions take precedence. Repairs stay within the original task and existing authorization. The two skills preserve unrelated work, distinguish uncertainty from error, and avoid recursive review-repair loops.

## Package

`plugin.json` is the portable Agent Plugins manifest, with OpenAI presentation metadata and the shared icon. `skills/` contains both workflows and their Codex interface metadata. `.claude-plugin/plugin.json` provides a Claude Code compatibility manifest.

The plugin uses the host's existing tools and permissions. It adds no MCP servers, credentials, scripts, or lifecycle hooks.

For ChatGPT and Codex, use the existing Find & Fix Mistakes plugin in your account. The files here maintain that same plugin; do not create another copy to update it. A package comparison verifies the saved files. It does not prove how a model will behave in every session.

Official packaging instructions: https://developers.openai.com/plugins/build/plugins


## Source and releases

Version: **1.0.4**. This folder is the canonical source for the complete plugin: both skills, their interface files, all three manifests, the icon, and the privacy guide. [Open the source on GitHub](https://github.com/RachaelQuisel/Skills/tree/main/plugins/find-fix-mistakes). The repository is private, so access is required.

Edit this source first. Keep the package and both skill versions together in the repository's `release-registry.json`, run the release and maintenance checks, and update the existing built plugin from this folder. Compare the saved archive with the source before marking the release synchronized. Update the existing catalog entry rather than adding a duplicate.

This source package does not establish an Anthropic submission, approval, or public listing.
