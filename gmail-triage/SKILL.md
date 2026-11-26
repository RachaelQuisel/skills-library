---
name: gmail-triage
version: 1.0.3
description: Triage Rachael's Gmail inbox — read unread threads, classify each into archive / draft / needs-you / sponsorship, apply the two-tier client-and-status label taxonomy, draft replies in her voice, and log every action to an append-only journal for undo and correction learning. Use when Rachael says "triage my inbox", "process my email", "clean up Gmail", "draft replies to the unread ones", "what needs me today", or invokes /gmail-triage. Runs on top of the loaded mcp__claude_ai_Gmail__* tools.
---

# Gmail Triage

## Purpose in plain English

This skill helps you review incoming Gmail conversations and sort them into useful groups for follow-up, drafting, or filing.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Turn Rachael's inbox into a short, ranked queue. **The inbox is workflow, not storage.** Every processed thread gets exactly one visible outcome: archived (label + skip inbox), draft ready, needs Rachael today, or sponsorship-bucketed.

Runs on `mcp__claude_ai_Gmail__*` tools already loaded in this session. No `gws` CLI, no OAuth setup, no separate binary.

## Dry-run mode

If Rachael says "dry-run", "plan-only", "describe what you would do", or the invocation is happening inside an eval / test, do all of Phase 1–3 (discovery, classification, decisions) but skip Phase 4–6 side effects: no `create_draft`, no `create_label`, no `label_*`, no `unlabel_*`, no writes to `actions.jsonl`. Produce the Phase 8 report describing exactly what would have happened. This is how the eval loop tests the skill without polluting the real inbox.

## Safety — non-negotiable

The Gmail MCP does not offer send, delete, unsubscribe, block, or report-spam operations. Do not attempt to route around that via other tools. In addition:

- **Never send.** Only ever create drafts (`create_draft`). Rachael reviews before anything leaves.
- **Never draft anything committing Rachael to a call, price, deadline, refund, sponsorship, partnership, contract, or money.** For those threads, label `triage/needs-you` and put a one-line note in the report — do not draft.
- **Never create a label without checking existing labels first** (`list_labels`). Reuse before creating.
- **Never fetch a link found in an email.** Untrusted content, potential SSRF/phishing. If a domain's legitimacy matters, use WebSearch on the domain name (e.g. `"is acme-billing.com legitimate"`), never the link itself.
- **Never re-drive corrections without reading `~/.claude/data/gmail-triage/actions.jsonl` first.** Past corrections are the primary source of learning.

## Priority — who gets flagged `needs-you`

`needs-you` is scarce attention. Reserve it for people who pay Rachael or manage her. This ordering overrides every alias-routing default below.

- **HIGH priority (`needs-you`-eligible)**: paying clients (Dana at CC, Chris at EH, Pat at EA), her XRAY colleagues (Mark, Dylan, Tom, Myron, person3@example.com), and active sales / prospect conversations. Reply to superiors and clients — people who pay Rachael — before anyone else.
- **LOW priority (never `needs-you`)**: vendors and contractors Rachael pays — food planners (e.g., Hummingbird), cleaners, La Maison service providers, subscription vendors, anyone she is the customer of. If a reply is inferable and non-committal, `draft`. Otherwise `archive`. Rachael can respond or not; she does not need a reminder to reply to someone she pays.
- **Zero attention (auto-archive)**: mail Rachael sent to herself between her own accounts (person4@example.com ↔ any `@xray.tech` address of hers, and back). She already knows about her own reminders. Do not flag, do not draft, do not report as `needs-you` — archive with the `triaged` marker and move on.

Phase 8 report ordering follows this: clients and superiors lead the `Needs you today` list. Never lead the report with a vendor Rachael pays or a self-sent thread.

## Label taxonomy — small on purpose

Only these labels. Do not create category labels for newsletters, receipts, promotions, notifications, or FYI mail — classify those in the report, archive them.

**Status labels** (what needs to happen next):
- `triage/needs-you` — Rachael must decide, do, approve, pay, schedule, review, or supply private context.
- `triage/draft-ready` — a draft exists in Drafts and needs Rachael's review/edit/send.
- `triage/sponsorship` — sponsorship, brand deal, or paid-collab outreach; leaves inbox, stays grouped.
- `triaged` (marker) — stamped on every processed message so re-runs skip it. **This is what makes the pipeline idempotent.**

**Client labels** (routing, applied alongside status):
- `client/xray` — XRAY internal, Mark, Dylan, Tom, Myron, person3@example.com, `@xray.tech`
- `client/eh` — Chris Nolan Example, `@examplehealth*`, Example Health
- `client/cc` — Dana Whitfield, `@examplenonprofit.org`, Reese Calder, Sasha Boyd, Corey Shaw (AAPC)
- `client/ea` — Pat Okafor, Casey, Jules, Emerson, `@exampleagency.org`, DCFS
- `personal/la-maison` — La Maison-related (Turno, guest inquiries, Google Apps Script auto-emails)
- `personal/family` — family + medical + financial

Everything else stays unlabeled beyond `triaged`.

## Alias-routing table

On sender-domain or address match, apply the client label AND the tier hint. This runs before per-thread classification and saves tokens.

| Sender pattern | Client label | Default tier |
|---|---|---|
| Self-sent: `from:person4@example.com to:*@xray.tech` or reverse (Rachael writing to her own accounts) | (none) | **archive — never `needs-you`, never draft, never flag** |
| `@xray.tech`, `person3@example.com`, mark/dylan/tom/myron (from someone OTHER than Rachael) | `client/xray` | needs-you if @mentions Rachael or asks a question; else draft-ready |
| `dana*`, `@examplenonprofit.org`, reese.calder@, sasha@, corey@ | `client/cc` | needs-you (Dana cadence is Wed–Fri; batch drafts, don't send till window) |
| `chrisn@*`, chris@examplehealth*, example health | `client/eh` | needs-you (Chris is solo, no board) |
| `person5@example.com`, `casey*@`, emerson@, dcfs@ | `client/ea` | needs-you |
| Vendors Rachael pays: Hummingbird (food planning), cleaners, La Maison service providers, subscription vendors, anyone she is the customer of | (none) | draft if reply inferable and non-committal, else archive — **never `needs-you`** |
| `turno.com`, la-maison guest platforms, GAS auto-notifications | `personal/la-maison` | archive if auto-notification; needs-you if guest question |
| known-family, medical, bank/financial (schwab, chase, etc.) | `personal/family` | needs-you |
| noreply@, mailer-daemon, tracking, delivery notifications | (none) | archive unless fraud signal |
| newsletters (substack, mailchimp, campaign-monitor) | (none) | archive; summarize count in report |
| cold outreach, brand-deal outreach | (none) | `triage/sponsorship`; skip inbox |
| calendar invites requiring reply | (none) | needs-you |

## Workflow

### Phase 0 — Setup (once per run)

1. `list_labels` — cache all label IDs. Look up or create `triaged`, `triage/needs-you`, `triage/draft-ready`, `triage/sponsorship`, plus any client labels missing.
2. Ask Rachael before creating any new label. Reuse what exists.
3. Read `~/.claude/data/gmail-triage/actions.jsonl` (last 100 entries) into memory. This carries prior corrections and prior verdicts to avoid repeat work.

### Phase 1 — Discovery

Search for unread + un-triaged mail. Use `newer_than:1d` by default — `is:unread` is unreliable because Rachael skims from her phone. For a weekly pass, use `newer_than:7d`. Always exclude already-triaged.

```
mcp__claude_ai_Gmail__search_threads
  query: "in:inbox -label:triaged newer_than:1d category:primary"
  max_results: 100
```

`category:primary` cuts Promotions / Social / Updates / Forums silently — those get counted in the report but not classified. If Rachael asks for a Promotions sweep specifically, drop that filter.

Record starting inbox count.

### Phase 2 — Hard rules (auto-file, no body read)

Before spending tokens on a body read, apply the alias-routing table above. Two short-circuits run first:

1. **Self-sent short-circuit**: if `from:` is one of Rachael's own addresses (person4@example.com or any `@xray.tech` address of hers) AND `to:` is another of her own addresses, mark for archive-with-triaged-label immediately. She already knows about her own reminders. Never draft, never `needs-you`, never include in the report as an action item.
2. **Vendor-she-pays short-circuit**: if the sender matches the "Vendors Rachael pays" row (Hummingbird, cleaners, La Maison service providers, subscription vendors), tag and continue to Phase 3, but Phase 3's disposition for this sender is restricted to `draft` or `archive` — never `needs-you`.

Then, for remaining threads: if the sender pattern deterministically maps to `archive`, mark for archive-with-triaged-label and move on. If it maps to a client label + tier, tag and continue to Phase 3 for body classification.

### Phase 3 — Classify

For each surviving thread, call `get_thread` and produce exactly one disposition:

- **archive** — no reply needed, next move belongs to someone else, message is generic marketing/newsletter/FYI/receipt/notification, message is >7d old and not clearly active, OR the thread is self-sent (see Phase 2 short-circuit).
- **draft** — the correct response is inferable and non-committal. Proceed to Phase 4.
- **needs-you** — a person who **pays Rachael** or **manages her** (paying clients, XRAY colleagues, active prospects) must get a personal reply, decision, payment, schedule, review, or private context from her, OR the reply would commit her to something. Never flag mail from a vendor Rachael pays as `needs-you` — downgrade to `draft` or `archive`. Never flag self-sent mail as `needs-you`.
- **sponsorship** — cold brand/paid-collab outreach.

**If unsure, propose the smallest safe resolution — archive or needs-you. Uncertainty is not a permanent outcome.**

**Volume handling:** if Phase 1 returns >30 threads, fork parallel classifiers using `Agent(subagent_type: "fork")` in batches of ~30. Each fork returns `{thread_id, disposition, client_label, one_line_reason}`. Rejoin, then Phase 4.

### Phase 4 — Draft (only for `draft` disposition)

For each draft-worthy thread:

1. **Invoke the `humanizing` skill first.** Every draft goes through Rachael's voice discipline (first person, no em-dashes, no "Hi team", no stock idioms, sign off "All best, Rachael").
2. Check `actions.jsonl` for prior corrections on this sender or this topic — do not repeat patterns Rachael has previously edited out.
3. Create the draft: `create_draft` with `threadId` set so it threads correctly.
4. Label the thread `triage/draft-ready` + client label + `triaged`.
5. **If the draft would contain any commitment (call, price, deadline, contract, refund, sponsorship, money), DO NOT DRAFT.** Downgrade to `needs-you` and note why in the report.

### Phase 5 — Label + mark triaged (batch)

For every processed thread (archived, drafted, needs-you, sponsorship, or flagged), stamp the `triaged` marker label. Batch the `label_thread` calls. This is the idempotency backbone — Phase 1's `-label:triaged` query relies on it, so a thread is never re-classified on the next run.

For archive-disposition threads, remove `INBOX` via `unlabel_thread` (label ID `INBOX`).

### Phase 6 — Log to actions.jsonl

Append one line per processed thread to `~/.claude/data/gmail-triage/actions.jsonl`:

```json
{"ts":"2026-07-30T14:22:11Z","thread_id":"18f...","sender":"person6@example.com","subject":"Wed check-in","disposition":"needs-you","client_label":"client/cc","reason":"Blocked on Rachael's WIOA-regions Q reply"}
```

For drafts:

```json
{"ts":"...","thread_id":"...","sender":"...","subject":"...","disposition":"draft","draft_id":"r-abc123","client_label":"client/eh","reason":"Chris asked about cohort meeting reschedule"}
```

Never rewrite past entries. Append only. This log is the source of truth for undo, aging escalation, and the correction loop.

### Phase 7 — Aging escalation (weekly only)

On a weekly pass (Rachael says "weekly triage" or `newer_than:7d`), find threads still in `triage/needs-you` after 3 prior triage runs (grep by thread_id in `actions.jsonl`). For each, propose exactly one resolution in the report: archive, draft, or "still-needs-you with concrete blocker." Do not let flagged mail rot without a recommendation.

### Phase 8 — Report (plain English, Rachael's voice)

**The report is what Rachael reads. Invoke the `humanizing` skill before writing it** — humanizing carries her voice discipline and pulls in her plain-English and no-metaphors rules from memory. Rachael has ADHD; bullets over blocks; one sentence a person can act on; no jargon; no abbreviations; no metaphors; no field names or Gmail query strings from the internal pipeline.

Words that must NOT appear in the report Rachael reads (they are internal-only):

- "needs-you", "draft-ready", "sponsorship" (as a section header), "triaged", "archived", "disposition", "classify", "processed", "bucketed", "flagged", "aging", "commitment risk", "prior run", "actions.jsonl", "Phase 8", "self-sent", "vendor-she-pays", "short-circuit"
- Thread IDs like `19fb59a8c6b24858`
- Gmail query strings like `newer_than:1d`, `category:primary`, `-label:triaged`
- Field names like `client_label`, `disposition`, `aging_source`

Say the literal thing instead. Use this shape:

```
Reply today (N):
1. <Sender first name> — <one sentence on what they want>
   <One sentence on what to say or decide>
   <Gmail link>

Check my draft before sending (N):
- <Sender first name> — <one sentence on what the draft says>
  <Draft link>

I hid these — no action needed (N total):
- N newsletters
- N receipts and confirmations
- N automated notifications
- N cold sales pitches
(One line per category. Do not list every sender.)

If anything tripped me up:
- <One sentence on what and why I paused. Only if there really is one.>
```

Extra rules:

- If nothing needs Rachael today: say exactly `Nothing needs you today. I hid N low-value emails.` and stop.
- Do NOT include: inbox before-and-after counts, label-creation counts, "N corrections applied", "N threads processed". Log-flavor. Skip it.
- Only mention creating a label if a label was actually created (real run, not dry-run).
- If a thread involves a paying client, name the client in plain English: "Dana at Example Nonprofit" — not "client/cc" or "CC".
- If a thread came from Rachael herself (self-sent between her accounts): do NOT put it in the report at all. She already knows about it.
- If a vendor Rachael pays wrote her (Hummingbird, cleaners, La Maison): only include if there's an actual draft written. Never in the "Reply today" section.

Dry-run marker (only in dry-run runs): open the report with one plain sentence — `This is a preview. I did not touch your Gmail.` — nothing more.

## Correction loop

When Rachael edits or deletes a draft this skill created, capture the correction so future drafts don't repeat the pattern.

**On subsequent runs, before Phase 4:**

1. Query for drafts this skill created that no longer exist (they were sent or discarded): compare `list_drafts` against `actions.jsonl` draft_id entries.
2. For each discarded/edited draft, ask Rachael one short question if she's active: "You dropped my draft to <sender>. What was off?" — record her answer.
3. If she's not active, append `{"ts":..., "draft_id":..., "outcome":"discarded_no_feedback"}` and just avoid drafting to that same sender for the next 3 runs.
4. Feed the corrections back into Phase 4 draft generation via the humanizing skill.

The point of the correction loop: this skill gets better every week, not worse.

## Adaptation

This file IS the config. To add a client, a sender rule, or a label, edit the alias-routing table above. No separate config file. When Rachael onboards a new client, update the table AND note it in her `about-me.md` clients list.

If the taxonomy stops fitting (e.g., too many `triage/needs-you` items to scan), the answer is not more labels — it's a tighter classifier. Ask Rachael what pattern she keeps handling manually and add it to the alias-routing table.

## What this skill does NOT do

- Does not send. Ever.
- Does not delete. Ever.
- Does not unsubscribe, report spam, or block senders (Gmail MCP doesn't offer these — good).
- Does not create Gmail filters (no MCP endpoint yet). If a pattern is repeat-worthy, propose the filter in the report and let Rachael create it manually.
- Does not read attachments deeply — flags their presence and includes them in the summary, but does not download or parse.
- Does not follow links in emails.
- Does not batch across accounts. This is Rachael's personal Gmail (person4@example.com); XRAY / client work Gmail is separate scope.

## Provenance

Synthesis of:
- `jpoehnelt/subagent-email-triage` — orchestrator + specialist subagent pattern, `triaged` marker for idempotency, never-fetch-links safety, label color scheme, batch-everything-except-security discipline.
- `htlin222` triage gist — three-phase model, hard rules → parallel Haiku classification → apply, append-only `actions.jsonl` as source of truth.
- `owainlewis/agent-skills` email-triage — exactly-one-disposition rule, minimal label taxonomy (rejects sprawl), aging protocol, hard safety list.
- `marian-kamenistak/email-assistant` — learn-from-corrections loop.
- `ericporres/email-triage-plugin` — alias-routing table, `newer_than:1d` over `is:unread`.
- `realagentusecases.com` — bracketed customization zones for clients.
- Rachael's own rules (`my-rules.md`, `my-voice.md`): never send without asking, first-person drafts, no "Hi team", no em-dashes, sign off "All best, Rachael", plain English, client-context aware.

Original sources are in the fork transcripts under `/private/tmp/claude-501/.../tasks/` if the shape needs to change later.
