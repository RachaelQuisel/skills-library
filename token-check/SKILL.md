---
name: token-check
version: 1.0.1
description: Estimate token usage of a skill while creating or editing it. Use when the user asks to check tokens, measure skill size, audit skill efficiency, or wants a token report on a skill in progress. Also use when creating a skill and the user says "how big is this" or "check the tokens."
tags:
  - skill
---

# Token Check

## Purpose in plain English

This skill helps you estimate how much space a skill's instructions use in an assistant's working context.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Estimate and report token usage for a skill that is being created or edited. Provide actionable feedback to keep skills lean.

## How to Estimate Tokens

Use these approximations (accurate within ~10% for English text):

- **Word count method**: tokens ≈ word_count × 1.33
- **Character count method**: tokens ≈ char_count ÷ 3.5
- Run `wc -w` and `wc -c` on each file, then apply both formulas and average them.

## What to Measure

For the skill being worked on, measure and report:

| Component | File(s) | Words | Est. Tokens |
|-----------|---------|-------|-------------|
| Frontmatter + description | SKILL.md (yaml only) | — | — |
| SKILL.md body | SKILL.md (markdown) | — | — |
| Each reference file | references/*.md | — | — |
| **Total always-loaded** | frontmatter + body | — | **—** |
| **Total on-demand** | references/ | — | — |
| **Grand total** | all files | — | **—** |

Do not measure scripts/ or assets/ — they are not loaded into context unless explicitly read.

## Budgets and Guidance

Use these thresholds (from skill-creator best practices):

| Component | Budget | Status |
|-----------|--------|--------|
| Description | < 1024 chars | |
| SKILL.md body | < 500 lines / ~5000 tokens | |
| Any single reference | < 3000 tokens (aim for < 1500) | |
| Total always-loaded | < 6000 tokens | |

Flag each component:
- **Under budget** — no action needed
- **Near limit** (>80% of budget) — mention it, suggest watching
- **Over budget** — list specific content to move to references or trim

## Report Format

Print a concise report like:

```
## Token Check: [skill-name]

| Component | Words | ~Tokens | Budget | Status |
|-----------|-------|---------|--------|--------|
| Description | 42 | 56 | 200 | ok |
| SKILL.md body | 380 | 505 | 5000 | ok |
| references/schema.md | 1200 | 1596 | 3000 | ok |
| **Always-loaded total** | **422** | **561** | **6000** | **ok** |
| **Grand total** | **1622** | **2157** | — | — |

No issues found. / [List specific recommendations]
```

## Recommendations to Give

When over budget, suggest these actions in priority order:

1. **Move examples to a reference file** — examples are heavy and only needed sometimes
2. **Move lookup tables / schemas to references** — only loaded when relevant
3. **Trim redundant explanations** — if Claude already knows it, cut it
4. **Split large references by topic** — so only the relevant one loads
5. **Replace prose with bullet points** — typically 30-40% fewer tokens
6. **Check for duplication** — content already in CLAUDE.md or other skills
