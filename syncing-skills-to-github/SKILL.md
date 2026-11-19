---
name: syncing-skills-to-github
version: 1.0.1
description: >
  This skill should be used when the user wants to sync skills to GitHub, push skill changes
  to a remote repository, or back up local skills. Syncs Claude Agent Skills from
  ~/.claude/skills/ (local) to a GitHub repository using git commands. Generates semantic
  commit messages and pushes to the remote.
user-invocable: true
tags:
  - skill
---

# Syncing Skills to GitHub

## Purpose in plain English

This skill helps you save approved skill changes to their GitHub repositories.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


**This skill runs in Claude Code with access to your terminal and git credentials.**

## Purpose
Sync Claude Agent Skills from `~/.claude/skills/` (local machine) to a GitHub repository with detailed commit history. Skills are stored in a flat directory structure.

## When to Use
Trigger this skill after:
- Creating or updating skills locally
- Weekly batch sync of multiple skills
- Any changes to skills in `~/.claude/skills/`

## How It Works
1. **Detect** changes in `~/.claude/skills/` using git status
2. **Review** what changed (new files, modifications, deletions)
3. **Identify** affected skill directories
4. **Generate** semantic commit messages based on changes
5. **Commit** to local git repository
6. **Push** to GitHub remote
7. **Report** summary of sync operation

## Prerequisites

### Environment
- **Claude Code** running in terminal (has access to git credentials)
- Git installed and configured with GitHub authentication
- `~/.claude/skills/` is a git repository
- A configured remote (e.g., `origin` pointing to your skills repo on GitHub)

### Default remote behavior
- Push to `origin` only, unless the user explicitly names another remote.
- If multiple remotes exist (e.g., personal + work), ask before pushing to anything other than `origin`.

### Directory Structure
```
~/.claude/skills/
├── .git/                          # Git repository
├── README.md                      # Optional skill index
├── skill-a/
│   └── SKILL.md
├── skill-b/
│   ├── SKILL.md
│   └── references/
└── [other skills...]
```

## Implementation

### Step 1: Verify Git Repository

```bash
cd ~/.claude/skills

# Check if this is a git repo
if [ ! -d .git ]; then
    echo "Not a git repository. Initialize first:"
    echo "  cd ~/.claude/skills"
    echo "  git init"
    echo "  git remote add origin git@github.com:your-username/your-skills-repo.git"
    exit 1
fi

# Check remote
git remote -v
```

### Step 2: Detect Changes

```bash
cd ~/.claude/skills

# Get status
git status --porcelain

# Parse output:
# M  = Modified file
# A  = Added file (staged)
# D  = Deleted file
# ?? = Untracked file
# R  = Renamed file
```

### Step 3: Identify Affected Skills

```bash
# Parse git status to identify which skill directories changed
git status --porcelain | \
  grep -E "SKILL.md|references/" | \
  sed 's|^...||' | \
  cut -d'/' -f1 | \
  sort -u

# Output: list of skill directory names with changes
```

### Step 4: Generate Commit Message

**Single Skill:**
```
[CREATE|UPDATE|FIX] skill-name: Brief description

- What changed specifically
- Why this change was made
- Impact or benefit
```

**Multiple Skills:**
```
[SYNC] Updated N skills

New skills:
- skill-a: Description
- skill-b: Description

Updated skills:
- skill-c: What changed
- skill-d: What changed

Deleted skills:
- skill-e: Reason for removal
```

**Semantic Prefixes:**
- `[CREATE]` - New skill added
- `[UPDATE]` - Existing skill modified
- `[FIX]` - Bug fix or correction
- `[REFACTOR]` - Code improvement, no functionality change
- `[DOCS]` - Documentation updates only
- `[SYNC]` - Batch commit of multiple changes
- `[RETIRE]` - Skill archived or deprecated

### Step 5: Stage and Commit

```bash
cd ~/.claude/skills

# Stage all changes
git add .

# Or stage specific skill
git add skill-name/

# Commit with generated message
git commit -m "$COMMIT_MESSAGE"

# Verify commit
git log -1 --oneline
```

### Step 6: Push to GitHub

```bash
cd ~/.claude/skills

# Push to main branch on origin
git push origin main

# If push fails (e.g., branch diverged), pull and rebase
git pull --rebase origin main
git push origin main
```

Never force-push without explicit user confirmation.

### Step 7 (optional): Regenerate README

If a `generate-readme.sh` script exists in the repo, run it to refresh the skill index, then commit and push the result. Skip this step if the script is not present.

```bash
cd ~/.claude/skills

if [ -x ./generate-readme.sh ]; then
    ./generate-readme.sh
    git add README.md
    git commit -m "[DOCS] Update README with skill index"
    git push origin main
fi
```

## Usage Modes

### Mode 1: Single Skill Sync

**Trigger:** "Sync the [skill-name] skill to GitHub"

**Process:**
1. Verify the skill exists in `~/.claude/skills/`
2. Check git status for that skill only
3. If no changes: inform user, exit
4. If changes: show what changed
5. Generate a commit message scoped to that skill
6. Commit and push to `origin`

### Mode 2: Batch Sync (All Changes)

**Trigger:** "Sync all changed skills to GitHub" or "Sync skills to GitHub"

**Process:**
1. Run `git status` to detect all changes
2. Identify all affected skill directories
3. Show summary of changes
4. Generate batch commit message
5. Commit all changes
6. Push to `origin`
7. Optionally regenerate README (Step 7 above)

### Mode 3: Dry Run (Preview Changes)

**Trigger:** "Show what would sync to GitHub" or "Preview git sync"

**Process:**
1. Detect changes (do not commit)
2. Show what would be committed
3. Display the generated commit message
4. Ask for confirmation before proceeding

## Error Handling

### Not a Git Repository
```
~/.claude/skills is not a git repository.

To fix:
1. cd ~/.claude/skills
2. git init
3. git remote add origin git@github.com:your-username/your-skills-repo.git
4. git add .
5. git commit -m "[INIT] Initial skill repository"
6. git push -u origin main
```

### Push Rejected (Diverged Branches)
The remote has commits the local repo does not. Default to:
```bash
git pull --rebase origin main
git push origin main
```
Only force-push with explicit user permission.

### Merge Conflicts
List the conflicted files and walk the user through resolution. Do not auto-resolve.

### No Changes Detected
Inform the user there is nothing to sync and report the last commit hash and message.

## Best Practices

### Commit Hygiene
- **Atomic commits:** One logical change per commit when possible
- **Descriptive messages:** Always explain WHY, not just WHAT
- **Consistent prefixes:** Use [CREATE], [UPDATE], [FIX], etc.

### Sync Frequency
- After each skill creation: immediate sync
- After bulk updates: end-of-day sync
- Before major changes: commit current state first

### Branch Strategy
Default to a single `main` branch. Skills are standalone, so feature branches add overhead without much benefit.

## Security & Privacy

### Repository
- Treat the skills repo as private by default — it may contain proprietary workflows or client references.
- No public sharing without an explicit ask.

### No Sensitive Data
- Never commit API keys, tokens, or credentials.
- Use placeholder values in examples.
- Sanitize client information before committing.
- Review the diff before committing.

### Git Credentials
- Claude Code uses existing git credentials from the environment (SSH keys or HTTPS tokens).
- No credentials are stored in the skill itself.

## Dependencies
- Claude Code (terminal access with git credentials)
- Git installed and configured
- A configured GitHub remote on `~/.claude/skills/`
- Bash shell for git commands

## Notes
- Pushes to `origin` by default. Confirm with the user before pushing to any other remote.
- Works with both SSH and HTTPS git remotes.
- Supports single-skill, batch, and dry-run modes.
