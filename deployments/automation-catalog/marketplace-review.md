# Marketplace review

Reviewed October 11, 2026 with Publish a Plugin, Ghibli Icon Maker and Voice Align.

## Packages

| Display name | Plugin identifier | Package path |
| --- | --- | --- |
| Update Automation Catalog | automation-catalog | plugins/automation-catalog |
| Check Catalog Reports | automation-catalog-failure-check | plugins/automation-catalog-failure-check |

Both are private review version 0.2.0. Their shared marketplace is rachael-quisel-skills. The catalog identifier stays unchanged so existing references still work. Display names use plain English.

## Verified here

- Both packages contain a Claude manifest, skill instructions, README, privacy notice, license status and icon.
- The repository marketplace points to both package folders. Entry names match the plugin names.
- Both icons are 1024 by 1024 RGBA PNGs. They have no embedded text or metadata chunks. Compression preserved identical decoded pixels.
- Catalog icon: 725,248 bytes. Report-check icon: 653,520 bytes. Both are below the Publish a Plugin skill's observed 768 KiB threshold. This threshold is not an official published size rule.
- All 18 catalog-helper tests passed. They cover identity matching, business boundaries, duplicate prevention, coverage gaps and publication planning.
- Both skill folders passed the skill frontmatter validator.
- An isolated agent used the report-check skill with eight fictional cases. It correctly handled success, a missing report, an explained partial result, six catalog attempts, a disabled task, a duplicate alert, unreadable evidence and exhausted alert delivery. It made no external writes. This does not verify Claude runtime behavior.
- The report checker passed the Publish a Plugin preflight. The catalog preflight reports one documentation finding: the required dollar-prefixed Codex skill invocation. That line does not execute a shell command or read credentials. The helper was inspected separately and makes no network calls. The syntax was preserved and the scanner was not modified.

## Still unverified

Claude Code is not installed in this environment. The official strict validator, marketplace installation, plugin loading and Claude runtime evaluation have not run. Local preflight and offline tests are not substitutes for those checks.

The repository is private. The packages retain all rights and do not grant a public license. Public distribution terms and a release version must be selected before public submission. The packages have not been submitted, approved or listed in Anthropic's directory.

## Claude verification steps

Use a checkout of the feat/automation-catalog-plugin branch in an authorized Claude Code environment. Run these commands from the repository root. Use Claude Code 2.1.281 or later so directory listing fields are recognized.

```sh
claude --version
claude plugin validate . --strict
claude plugin validate ./plugins/automation-catalog --strict
claude plugin validate ./plugins/automation-catalog-failure-check --strict
claude plugin marketplace add .
claude plugin install automation-catalog@rachael-quisel-skills
claude plugin install automation-catalog-failure-check@rachael-quisel-skills
claude plugin details automation-catalog@rachael-quisel-skills
claude plugin details automation-catalog-failure-check@rachael-quisel-skills
```

Start a new session and test both commands with fictional fixtures before using live services. Confirm required connections and permissions in that host. These packages do not transfer ChatGPT credentials or schedules to Claude.

## Sources

- [Anthropic manifest reference](https://code.claude.com/docs/en/plugins-reference).
- [Create a marketplace](https://code.claude.com/docs/en/plugins/create-marketplace).
- [Publish and distribute a plugin](https://code.claude.com/docs/en/plugins/publish).

Anthropic distinguishes a private Claude Code marketplace from its public directory. A valid package is not proof of directory approval. Installing a package is also separate from configuring cloud execution.

## October 15 merge review

All 18 helper tests and the package checker passed again. The shared marketplace preserves the existing Skillkeeper, Automation Briefing and Zite Prompt entries. The package checker now checks these two catalog plugins without assuming they are the only entries. The Codex invocation scanner finding remains a documented false positive. Claude strict validation and installation remain unverified. Packaged icons are the earlier assets; replacing them with the subsequently selected blue and peach images remains unfinished.
