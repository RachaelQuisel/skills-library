---
name: github-skill-library
version: 1.0.2
description: Find, choose, and use workflows in Rachael Quisel's imported GitHub skill repertoire. Use when the user asks what skills are available, wants a skill by name, or needs help choosing from the imported collection.
---

# GitHub skill library

## Purpose in plain English

This skill helps you find and choose a skill from the imported GitHub collection for the task you want to complete.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Read `../../catalog/skills.md` or `../../catalog/skills.json` to find a matching skill. Select the smallest useful set for the user's task. If the record names `available_in_plugin`, use that existing plugin's skill. Otherwise read the chosen `../<name>/SKILL.md` and its required resources. A shared skill lives in one current plugin; this collection keeps its source and routing information.

The catalog records each canonical GitHub path, version, and verified commit. Public adaptations and private operating workflows remain separately identified when their instructions differ. Prefer the unsuffixed private working version for Rachael's own client work, and a public variant when the user asks for a portable or public workflow.

Some imported skills use local executables, local files, Claude-specific tooling, or existing app connections. Resolve bundled relative resources from the selected skill's directory. Use equivalent available tools when they support the same requested action. If a required runtime, file, or connected app is unavailable, identify the specific missing requirement and complete the supported part without claiming the external action succeeded. An imported skill supplies instructions and resources; account access and action authorization still come from the current user and connected tools.

Use `../../catalog/source-aliases.json` for exact duplicates and `../../catalog/import-notes.json` for header repairs and excluded build artifacts. Build releases from the canonical source map in the private Skills repository. Update the existing platform records and public catalog together under `RELEASING.md`. Report unavailable destinations as pending. A saved ChatGPT update or GitHub push does not prove directory publication.
