---
name: dissonance-radar
version: 1.0.3
description: Surface high-leverage questions Rachael missed asking in one conversation or across recent client transcripts. Use when Rachael says "dissonance radar," "EOD review," "evening wrap-up," "what am I missing," "what didn't I ask," "what shifted today," "what should I be curious about," "review today's transcripts," or "did anything change today"; when operating or debugging the scheduled cloud Dissonance Radar; or when GitHub Actions reports that the Radar failed.
---

# Dissonance Radar

## Purpose in plain English

This skill helps you review recent conversations for important changes, missed questions, and matters that need closer attention.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


## Why this exists

Rachael's default mode is "radical agency" — she assumes any friction is hers to fix, takes on blame that isn't only hers, and doesn't ask the questions that would surface the actual dynamic. The classic miss: a stakeholder dropped out of meetings for a month and she didn't ask why. Turned out the stakeholder was frustrated with the build. She found out two weeks later via NotebookLM mining the transcripts.

The skill is the pause button that catches what her default misses. **It produces questions, not statements.** Inward questions ("what should I be noticing?") and outward questions ("what should I ask Casandra?") — never drafts of outbound communication. The point is to spark dialogue, not to send messages.

## When to run

- **Manually:** any time Rachael wants a check on a conversation she just had ("run the radar on this transcript") or a sweep of the day ("EOD review")
- **Scheduled:** autonomously in GitHub Actions at 5:00 AM and 1:00 PM Eastern, using unprocessed Debrief meetings from the last seven days. See "Cloud automation" below.

## Input modes

The skill accepts any of:

1. **Pasted transcript text** — Rachael drops a transcript directly in the prompt
2. **File path(s)** — e.g. `~/Claude-Work/CLIENTS/CCRES_Dylan_Sumser/Transcripts/Example Client-Transcript-2026-08-25-XRAY_CCRES_Weekly.md`
3. **Auto-discover recent (manual/local)** — when run with no input locally, run `~/Claude-Work/PROJECTS/dissonance-radar/prepare_sources.py`. It syncs Debrief first and returns files by meeting date for exactly Example Client, Example Nonprofit, and Example Agency.
4. **Date-specific** — pass the requested date as both `--cutoff` and `--through` to `prepare_sources.py`

If multiple transcripts exist for today, process them as ONE batch so cross-client patterns can surface (the same stakeholder vocabulary showing up across two clients, for example).

**Scheduled source scope.** Debrief in Airtable is the source of truth for the cloud Radar. `cloud_radar.py` fetches records by meeting date, filters out IDs already saved in `state/processed-records.json`, and creates one report per client. Its allowlist is exactly Example Client, Example Nonprofit, and Example Agency. Do not add other clients, glob local folders, use modified time as the conversation date, or treat Meeting Prep as a transcript source. A failed fetch is a failed run, not an empty radar.

**Meta-conversations are a valid input mode too.** Rachael's coaching sessions, retros, or solo reflection notes can also feed the radar — when the source IS a conversation about other conversations, expect the output to lean toward inward questions ("what should I be noticing?") rather than outward ones ("what should I ask Casandra?"). Both shapes are fine.

## The lenses (apply each one to the transcript)

Full pattern catalog is in `references/lenses.md`. Load it when needed. Brief version:

### GRPI — every conflict traces to one of four roots (Evan Michner's framework, 2026-06-04)

- **G — Goals.** Are people working toward the same outcome? "My goal is new customers, yours is keep existing customers" — looks aligned until effort allocation comes up.
- **R — Roles.** Does everyone know whose job is what? "I thought that was your job" / "She doesn't have the technical ability but is making technical calls."
- **P — Process.** Is there a shared method? "We don't have a way to capture decisions" / "Every meeting we start from scratch."
- **I — Interpersonal.** Is there friction between specific people that isn't about the work? Usually a downstream consequence of G/R/P breakdowns, but sometimes the root.

### Rachael-specific dissonance patterns (the things her default mode misses)

- **Disappearance.** Someone who was in the last N meetings isn't in this one. The skill asks: *"Where did [X] go? Are they OK with the current direction?"* — **but only if they were on the invite list to begin with.** Many of Rachael's client meetings are 1:1 by design (e.g. Rachael ↔ Jessica at EA). If an operational stakeholder was never expected to attend, don't apply this lens; surface them as an *ask* instead ("how does [X] hear about this change?").
- **In-meeting disagreement.** Two stakeholders contradict each other in the same transcript — Rachael often doesn't register this in the moment.
- **Sentiment shift.** Someone who was enthusiastic last week is curt this week, or vice versa. Tone-change is information.
- **Topic avoided.** Something Rachael raised got deflected or buried. Was that on purpose?
- **New vocabulary.** A new term or framing enters the conversation that wasn't there before — sometimes signals a priority shift the speaker hasn't named yet.
- **Commit drift.** Rachael said she'd do something last week and the transcript shows it didn't happen. Why?
- **Radical-agency tell.** Rachael takes on blame in the transcript that isn't only hers ("I should have known," "that was on me"). Flag for self-review — is there a question she should have asked instead?
- **Pace mismatch.** Client expects faster delivery than the scope allows, but Rachael is absorbing the gap by working until 2am. The transcript shows the gap without the gap getting named.

## Workflow

1. **Load inputs** — pasted text, file paths, or auto-discovery (see Input modes).
2. **Read the full transcripts.** Don't skim. Sentiment + sequence matter.
3. **Apply each lens.** Walk GRPI, then walk Rachael-specific patterns. For each potential signal, capture: the excerpt that triggered it, which lens, and the candidate question.
4. **Filter aggressively.** **Strategic curiosity, not all curiosity.** A signal is worth surfacing only if asking the question could change the next decision Rachael makes. Cut anything that's interesting-but-actionless. Target output: 3-7 questions, not 15.
5. **Rank.** Lead with the question that, if Rachael asked it tomorrow, would move the most. Bury the lower-stakes ones at the bottom.
6. **Format.** See "Output format" below.
7. **Deliver.** For a manual/local run, save to `~/Claude-Work/PROJECTS/dissonance-radar/briefs/<YYYY-MM-DD>.md` and print the path. In cloud mode, let `cloud_radar.py` save timestamped per-client reports, post each successful report to its approved internal Slack huddle, and record only successfully posted meetings as processed.

## Output format

```markdown
# Dissonance Radar — <YYYY-MM-DD>
**Sources:** <list of transcripts read, with file paths or "pasted">
**Mode:** <manual | scheduled-EOD>

## 1. <The question, as a question>
**Lens:** <G | R | P | I | disappearance | sentiment-shift | etc.>
**Trigger:**
> [<speaker>] "<one-sentence excerpt>"
> — <source, e.g. "AYMG 2026-06-04 strategy">

<2-3 sentence read on why this is worth asking. What changes if Rachael asks it. What changes if she doesn't.>

**Next move:** <ONE sentence, exactly one of: "ask [stakeholder] directly in next 1:1" / "raise in next meeting opener" / "ask yourself before [trigger]" / "just notice for now". No multi-step paragraphs, no nested inward-then-outward chains.>

## 2. ...

(repeat for 3-7 questions, ranked by leverage)

---
## What I did NOT flag (and why)

<Optional. 1-3 bullets on signals you considered but cut because they wouldn't change a decision. Helps Rachael calibrate the filter over time.>
```

## Voice

Strategically curious, not anxious. Warm, not alarmist. "Worth asking, not urgent" is the tone. The skill's job is to help Rachael notice — not to overwhelm her. If the day was actually quiet, say so. **An empty radar is a valid output.** Don't manufacture dissonance.

**When the signal is about Rachael's own pattern (radical-agency tells, pace mismatch, commit drift), stay observational, not diagnostic.** Surface the pattern with a question; don't interpret her psychology. "What if the non-answer wasn't yours to absorb?" beats "you have a tendency to absorb." She's the one diagnosing — the radar just notices.

**Lead next-move suggestions with inquiry, not prescription, when the transcript shows emotion.** If someone is processing, nervous, grieving, distressed, or making a statement that could be grief OR a scope ask, open the next move with an inquiry-style question that lets Rachael ask before solving — *"I'm hearing this is a lot — can you walk me through what's in your head right now?"* / *"Where is this coming from for you?"* / *"Tell me more about that."* Then layer the tactical follow-up. The point of the radar is to spark dialogue, so the next move should model the dialogue, not jump past it.

No "ensure / utilize / facilitate." No "needs fixing" — "needs to be fixed." Match Rachael's voice rules in `~/Claude-Work/ABOUT-ME/my-voice.md`.

## Cloud automation

The scheduled Radar runs in the private `RachaelQuisel/dissonance-radar` GitHub repository. It does not depend on Rachael's Mac, launchd, `pmset`, or Apple Notes.

1. GitHub Actions fires at 5:00 AM and 1:00 PM Eastern, or via `workflow_dispatch`.
2. `cloud_radar.py` fetches the last seven days of approved Debrief records from Airtable.
3. Claude creates and voice-aligns a separate report for each client with new meetings.
4. The runner saves each report as an Actions artifact and posts it to that client's approved internal Slack huddle.
5. Only meetings whose reports posted successfully are added to `state/processed-records.json`; failed clients remain eligible for retry.

### Operate and debug

Use GitHub Actions as the source of truth:

| Action | Command |
|---|---|
| List recent runs | `gh run list --repo RachaelQuisel/dissonance-radar --limit 10` |
| Read the failed step | `gh run view <run-id> --repo RachaelQuisel/dissonance-radar --log-failed` |
| Trigger a manual run | `gh workflow run dissonance-radar.yml --repo RachaelQuisel/dissonance-radar` |
| Watch a run | `gh run watch <run-id> --repo RachaelQuisel/dissonance-radar --exit-status` |
| Run local tests | `python3 -m unittest -v` in a checkout of the repository |

For Slack `channel_not_found`, first read the run's `Slack identity` line. The three configured channel IDs are valid XRAY channels, so do not change them without rechecking Slack. Confirm that `SLACK_BOT_TOKEN` belongs to the XRAY workspace and that its app has `chat:write` and `channels:join`; reinstall the app after changing scopes, replace the repository secret, then run the workflow manually. Treat an artifact without a Slack post as failed delivery, not a successful Radar.

## Related skills

- `meeting-prep` — pre-meeting brief (BEFORE conversations). Complement, not overlap.
- `transcript-quotes-miner-local` — daily scheduled mining for funny/sweet quotes. Same scheduling shape, different lens.
- `humanizing` — apply if Rachael decides to actually send one of the questions as a message (turns the question into her voice for delivery)
- `~/Claude-Work/ABOUT-ME/my-voice.md` — voice rules
- `references/lenses.md` — full pattern catalog with worked examples
