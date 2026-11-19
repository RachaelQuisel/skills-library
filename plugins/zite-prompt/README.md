# Zite Prompt

Write short, paste-ready Zite prompts. Resolve facts outside Zite, use known IDs, and focus each prompt on the next build step.

## How it works

- **Trigger:** Ask what to tell Zite, request a prompt, or ask to shorten or correct one.
- **Inputs:** Your current build step, earlier decisions, relevant source files, and known table or field IDs.
- **What happens:** The agent resolves facts from available sources, keeps the next step narrow, and asks one question only if a required fact or decision is missing.
- **Output:** One paste-ready prompt, usually under 250 words, or one concise question.

The included [examples](skills/zite-prompt/references/examples.md) cover La Maison's mobile scheduling screen, shortening a prompt, conflicting cleaner names, a product decision, and discovery that only Zite can answer. Example IDs and business rules are context, not defaults for other projects.

## Install in Claude Code

```text
claude plugin marketplace add RachaelQuisel/Skills
claude plugin install zite-prompt@rachael-quisel-skills
```

Use `/zite-prompt:zite-prompt` or ask for a Zite prompt in plain English. Repository access is required. Installation has not been tested in this build environment.

## Connections and limits

This is an instruction-only plugin. It does not bundle GitHub, Airtable, Twilio, or Zite connectors. It uses source material and authorized tools available in the host. Missing access can limit verification.

It drafts prompts without executing them in Zite. Execution requires a separate user request. It does not create tables, send messages, or install integrations by itself.

The standalone skill at `zite-prompt/` remains available for existing users. Keep its instructions, references, and evaluation cases in sync with this packaged copy.

## Validation status

JSON, package paths, and skill structure are checked locally. Claude CLI validation and installation are unavailable in this environment. No directory submission has been made. A directory listing icon has not been added.

See [PRIVACY.md](PRIVACY.md) for data handling.
