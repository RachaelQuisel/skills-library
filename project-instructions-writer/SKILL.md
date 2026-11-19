---
name: "project-instructions-writer"
version: 1.0.0
description: "Write or fix the project instructions for a Project in Claude (coordinator plus threads at claude.ai/code, the desktop Code tab or the mobile app). Use when someone sets up a Claude Project, asks what to put in project instructions, or says their project threads keep guessing or going off track."
---

# Project instructions writer (Projects in Claude)

This skill writes project instructions for one specific thing: a **Project in Claude**, the redesigned feature built on Claude Code.

## Confirm it's the right kind of project

A Project in Claude has a coordinator conversation, threads that do the work in the background, an Overview panel and a Library tab. It lives at claude.ai/code, in the Code tab of the Claude desktop app, or in the Claude mobile app.

Check which one the user means before you start. These are different things:

- **Earlier Projects in claude.ai chat or Cowork:** a folder of chats and reference files with no coordinator or threads. Its instructions box works differently. Tell the user this skill is built for the redesigned Projects, then offer to help with their chat Project anyway.
- **A repository's `CLAUDE.md` file:** rules about one code repository. Those belong in the repository, not in project instructions.
- **The `claude project` command in the terminal:** unrelated to Projects in Claude.

If the user mentions threads, a coordinator, the Overview panel or claude.ai/code, it's a Project in Claude. If it's unclear, ask one question: "Is this a project with a coordinator and threads, or a project in regular Claude chat?" Send that question by itself and wait for the answer before asking anything else. If the answer is the chat kind, the seven questions below would be wasted on the wrong project.

## Step 1: Gather what you need

Pull answers from the conversation and any files the user shared first. Ask only for what's missing, in one message, using these seven questions:

1. What is this project for? (One ongoing area of work, such as "my weekly content" or "running client onboarding.")
2. Who are you, and who is the work for?
3. How should the writing sound? Include tone, length, format and words to avoid.
4. Where do things live? List files in the Library, connected apps (Notion, Google Drive, Gmail) and GitHub repositories, plus what's in each.
5. How should a thread check its work before calling it done?
6. What needs your go-ahead first? (Common answers: sending email, publishing, deleting, spending money, merging code.)
7. How should the coordinator run threads? Cover four standing rules: whether to propose threads and wait for a go-ahead before starting them, how many threads can run at once, whether to post only when something finishes or is blocked, and whether follow-ups in an area go to the thread already working on it.

Leave out requests the user makes in the moment, such as "give me a status update on every thread" or "do this one with a smaller model." Those are things to say to the coordinator when the situation comes up. Written into instructions, they either do nothing or apply at the wrong time.

If the project sounds like a single task ("write one blog post"), say so. A Project in Claude is for ongoing work that keeps producing new tasks. One task belongs in a normal chat or a single session.

## Step 2: Draft the instructions

Use this structure. Fill every bracket with the user's own answers. Leave a section out when the user has nothing for it, rather than inventing content.

```
This project is for [what it's for].

About me: [who the user is and who the work is for]

How to write: [tone, length, formatting rules, words to avoid]

Where things live: [Library files, connected apps, repositories, and what's in each]

Before you call work done: [how to check it]

If something you need is missing, such as a file, an app connection, a repository or a password, say exactly what's missing in your first message and stop. Don't guess, substitute or make things up.

Ask me in the thread before: [actions that need approval]

How to run threads: [the standing rules from question 7, for example: propose threads and wait for my go-ahead; run at most two at a time; only post when something finishes or is blocked; send follow-ups to the thread already working on that area]
```

Rules for the draft:

- Keep the "if something is missing" section in every draft. Without it, threads tend to guess or work around the gap.
- Say "ask me in the thread" for approvals. Approvals happen inside each thread; a "go ahead" in the main project conversation doesn't reach a waiting thread.
- Write rules as plain statements a thread can follow without extra context. "Fact-check every claim and list sources at the end" works. "Be careful" doesn't.
- Put rules about one code repository (build commands, test commands) in that repository's `CLAUDE.md` instead, and tell the user why.
- Keep it under 16,000 characters. Shorter is better; every thread reads all of it.

### Example

A user says: "It's my project for client onboarding at my bookkeeping firm. Client files are in a Google Drive folder called Onboarding. Plain, friendly emails. Don't email anyone without asking me, and don't make up account numbers."

The draft:

```
This project is for onboarding new clients at my bookkeeping firm.

About me: I run a small bookkeeping firm. The work is for new small-business clients.

How to write: plain and friendly. Short emails, no jargon.

Where things live: client files are in the Google Drive folder "Onboarding."

If something you need is missing, such as a file, an app connection, a repository or a password, say exactly what's missing in your first message and stop. Don't guess, substitute or make things up. This includes account numbers.

Ask me in the thread before: sending any email.

How to run threads: propose threads and wait for my go-ahead.
```

The draft leaves out the "before you call work done" section because the user didn't say how to check work. Ask about it in your reply rather than inventing a check. "Don't make up account numbers" went into the "missing" section, where it does the most work.

## If the user already has instructions

When the user pastes current instructions or describes a problem with them ("my threads keep inventing client names"):

1. Read what they have before asking anything.
2. Match the problem to the section that should have prevented it. Invented details usually mean the "if something is missing" section is absent or vague. Threads starting work without asking usually mean the thread rules are missing.
3. Keep everything that works, in the user's own wording. Change only what's needed to fix the problem, then check the rest against the rules above.
4. Deliver the full revised instructions, plus a short list of what changed and why.

## Step 3: Deliver it

Return:

1. The finished instructions in one code block, ready to paste.
2. The character count. Count it with code when you can run code (for example, `len(text)` in Python), because counting by eye is unreliable. If you can't run code, give an estimate and label it as one ("about 1,200 characters").
3. Where to paste it: click the gear icon in the project header, then go to **Project settings > Memory > Project instructions**.
4. One line noting that changes apply to new threads only. Threads already running keep the old instructions.
5. A suggested first test: one small, real task. When it finishes, open the thread and check what it did. Fix any mistakes in the instructions, not only in that thread.

## What goes where

- **Project instructions:** rules the user writes. Every new thread and the coordinator receive them. Put must-follow rules here.
- **Project memory:** notes Claude keeps as it works (decisions, preferences, pitfalls). The user adds to it by saying "remember this." Preferences there are followed, but they aren't enforced limits.
- **Library:** reference files. Uploads are copies, so a changed file has to be uploaded again with **Replace**.

## Verified facts about Projects in Claude

Checked against Anthropic's documentation on October 4, 2026: https://code.claude.com/docs/en/claude-projects. Projects are in public beta, so recheck that page before quoting a setting or limit to a user.

The instructions template is adapted from "Claude Projects: The Complete Setup Guide" by Joshua Stevenson (@nocode.joshua) and from the example in Anthropic's documentation.

Access:

- Public beta on Pro and Max plans, rolling out gradually. Not on Team or Enterprise plans yet.
- Used at claude.ai/code, in the Code tab of the desktop app, or in the Claude mobile app. Not in the terminal CLI, the VS Code extension or the JetBrains plugin.
- No Projects in the sidebar means the rollout hasn't reached the account. Waitlist: https://claude.com/form/projects

Instructions, memory and files:

- Project instructions: up to 16,000 characters. Sent to each new thread and to Claude in the project conversation.
- Changes to instructions, repositories, plugins and environment reach new threads, not threads already running.
- Project memory: files Claude writes as it works. Every cloud thread reads the index file `MEMORY.md` when it starts. Read, edit and delete it in Project settings > Memory.
- A thread run on the user's own computer starts with the project's instructions but not its memory files.
- Preferences the user states in conversation (such as "run at most two threads") are saved to memory and followed, but they aren't enforced caps. Put anything that must be worded exactly in the instructions.

What threads can reach:

- Cloud threads use the connectors on the user's claude.ai account (claude.ai/customize/connectors). The project conversation itself has no connectors, so work that needs an app goes to a thread.
- Cloud threads don't pick up anything from the Claude Code setup on the user's own machine.
- Skills reach cloud threads two ways: skills enabled on the user's claude.ai account, and skills committed to a project repository under `.claude/skills/`.
- A project doesn't need a repository. Threads can research, write documents and deliver files to the Library tab.

Approvals and usage:

- A thread waiting on approval waits inside that thread. Telling the coordinator "go ahead" doesn't reach it.
- Default models: Opus everywhere, high effort for threads, low effort for the coordinator. Set in Project settings > General.
- Projects use the same plan limits as other Claude Code sessions, and use them faster. The enforced limit is 200 new threads per day across all projects.
- A thread that hits the plan limit waits and continues by itself when the limit resets.
- An idle thread watching a pull request wakes up and uses the plan when CI fails or a review comment arrives.
- A project belongs to one person and can't be shared during the beta.