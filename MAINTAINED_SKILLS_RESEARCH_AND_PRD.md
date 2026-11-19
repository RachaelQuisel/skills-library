# A subscription to skills that stay useful

Market research, revenue scenarios and short product requirements

### Decision: run a narrow paid pilot

A maintained collection could support a small recurring-revenue business. The evidence does not yet establish a large standalone market or venture-scale demand. Start by selling responsibility for a handful of recurring workflows: supported versions, repeatable tests, fixes and evidence of what worked. Your existing audit work is a useful starting point; its implementation has not been reviewed for this report.

### What the market evidence actually says

| Evidence | Implication |
| --- | --- |
| Demand proxy: 46% of respondents distrust AI accuracy versus 33% who trust it in Stack Overflow’s 2025 developer survey. [1] | Reliability is a real concern. This global, self-selected survey does not measure U.S. agencies’ willingness to buy maintained skills. |
| Direct competitor: Agensi sells skills with one-time or monthly pricing and advertises security scanning and manual review; creators keep 70% of net revenue. [2] | Paid skill subscriptions already exist. Auditing and recurring billing alone are not differentiation. |
| Commercial signal: TrustMRR reports Agensi at $3,026 tracked lifetime revenue, $38 MRR and 3 active subscriptions at retrieval. [3] | Evidence of early transactions, not proof of a large market. The connected-account figures do not establish total marketplace sales, seller income or profit. |
| Tooling substitutes: LangSmith Plus starts at $39/seat/month plus usage; Langfuse Core at $29/month plus usage. [4–5] | Customers can buy evaluation infrastructure cheaply. The subscription must earn its premium through maintenance and useful outcomes. |
| Platform competition: Anthropic’s skill-creator supports evaluations, benchmarks, trigger testing and comparisons with and without a skill. [6] | A test harness is increasingly a platform feature. Own the workflow expertise, customer relationship and quality of the regression suite. |

### Initial customer and positioning

Proposed beachhead: small U.S. automation agencies maintaining client workflows. They can reuse the same skills across engagements and feel the cost of breakage repeatedly. Zapier’s official partner program provides a prospecting channel, not a validated market-size estimate. [7] Start with one integration and one agent runtime; choose the combination from paid design partners.

Positioning: “We maintain the skills your agents depend on, and show you the evidence that each supported version still works.” A U.S. base may help sales and support; geography alone is not a defensible advantage.

## Revenue potential and delivery economics

Test $199 per agency workspace per month for five shared skills, tested updates and hosted audit history. This is a pricing hypothesis. Bound usage and support explicitly; price bespoke development separately. Retaining installed files after cancellation is compatible with charging for ongoing maintenance and hosted services.

| Active subscribers | Monthly revenue | Annual recurring run-rate |
| --- | --- | --- |
| 25 | $4,975 | $59,700 |
| 100 | $19,900 | $238,800 |
| 500 | $99,500 | $1,194,000 |

Formula: active subscribers × $199 × 12. These are customer milestones, not forecasts or first-year cash receipts. Roughly 4,188 subscribers would be needed for $10 million ARR at this price; neither the research nor these scenarios establish that level of demand.

### Base case at 100 customers

| Monthly assumption | Cost |
| --- | --- |
| Payment fees/refunds allowance: 5% of revenue | $995 |
| Hosting, models and evaluation: $15/customer | $1,500 |
| Support: 0.5 hour/customer at $60/hour replacement cost | $3,000 |
| Shared catalogue maintenance: 24 hours at $60/hour | $1,440 |
| Fixed infrastructure | $300 |
| Revenue less these delivery costs | $12,665 (63.6%) |

These are unvalidated budget assumptions, not supplier quotes. The remainder is not profit: it excludes acquisition, initial product development, administration, tax and unplanned incidents. Founder maintenance and support labor is costed rather than treated as free.

### The critical sensitivity is support time

If support rises to two hours per customer monthly, the same business leaves only $3,665 after those delivery costs—a margin of 18.4%. Support plus catalogue maintenance becomes 224 hours per month, beyond a normal solo workload. Standardized workflows and a narrow compatibility matrix are essential.

At the base assumptions, each customer contributes $144.05 before shared costs. Thirteen customers cover the $1,740 shared delivery budget; this is not full business break-even. At 25 customers the remainder is only $1,861 per month before the excluded expenses.

### How to monetize and reach buyers

Begin with direct subscriptions and founder-led sales. Sell a recurring outcome such as maintaining reliable Airtable operations, rather than access to a generic file collection. Use agencies’ recurring incidents to select the first collection. Ask for paid commitments before expanding it.

For scale context only: starting from zero, about 10 new paid accounts every month with 3% monthly churn would yield roughly 102 active accounts after a year. Both acquisition and churn are assumptions. An open marketplace can wait until customers renew and outside authors can meet the same maintenance obligations.

## Short PRD • Maintained Skills v1

Goal: prove that agencies will repeatedly pay for maintained skills, with enough shared maintenance to support healthy delivery margins. Primary user: an agency operator accountable for a client workflow.

### Scope and commercial offer

Pilot: five related skills, one integration, one supported runtime and explicit model/API compatibility. Airtable operations are a candidate, subject to partner demand. Proposed price: $199/workspace/month, up to 1,000 logged runs and 30-day audit retention. Include a one-business-day incident acknowledgement; do not promise a universal fix time. No open marketplace or unlimited custom work in v1.

### Required experience

| Capability | Minimum requirement |
| --- | --- |
| Install and verify | Versioned release with owner, release hash, supported environment, suite version, pass counts, last verified date and known limitations. After seven days without verification, display “unverified”; distinguish that from a known failure. |
| Observe outcomes | A deployed collector stores tenant-scoped run, event and attempt IDs, skill/runtime versions, timestamps and evidence. Separate execution status, verified business outcome and collection health. Missing evidence means “unknown,” not success. The audit skill explains collected records. |
| Create safe regression cases | Opt-in sharing only. Prefer synthetic reproductions; remove secrets and identifiers, preserve the failure mechanism, and review before adding a case to the shared suite. Keep customer traces tenant-isolated. Redaction alone is not proof of anonymity. |
| Repair and release | Reproduce a failure, fix it, run the complete suite, review the change, and publish a versioned update. Support pinned versions and rollback. Never replay a customer’s production writes simply to run a test. |
| Show continued value | Monthly change log: incidents fixed, tests added, supported compatibility and unresolved issues. Allow audit export and cancellation; installed files remain usable while hosted services and future updates stop. |

### Release and acceptance criteria

Start with 20 meaningful cases per skill, repeated three times on the supported configuration. Include held-out cases and compare against the prior release and a no-skill baseline. Require all critical privacy, permission and duplicate-write checks to pass; use a proposed 95% threshold on other cases. This is a suite release rule, not a claim of 95% real-world reliability.

Acceptance: a synthetic incident fails on the old version and passes on the fix; earlier cases remain passing; timeouts and missing telemetry produce the correct status; no cross-tenant access or secret leakage enters shared tests; version rollback is demonstrable. Subjective outcomes need a documented human rubric.

### Dependencies and boundaries

The existing audit tools need verified event collection and outcome checks. Schedule tests weekly and on supported dependency changes only once a running service is deployed. Exclude compliance certification, blanket “safe” guarantees, all-runtime support and training a foundation model on customer data.

## Validation plan and sources

### A 90-day experiment

| Stage | Proposed decision gate |
| --- | --- |
| Days 1–15: choose the repeated problem | Interview 15 qualified U.S. agency buyers. Document incidents, current workaround, actual support time and willingness to pay. Choose one workflow shared by several buyers. |
| Days 16–45: deliver a paid pilot | Secure three $199/month accounts. Get explicit telemetry/test-reuse consent. Establish before-and-after outcome and labor baselines. If 15 qualified offers cannot produce three paid pilots, revise the offer before building more. |
| Days 46–90: assess renewal and costs | Seek two monthly renewals from at least two of the initial three customers and independently confirmed recurring value. This is an early signal, not statistical validation. Track every support and maintenance minute; target ≤30 support minutes/customer/month after onboarding. |
| Next gate: expand cautiously | Move toward ten paying accounts only after the initial renewal signal. Recalculate delivery margin from observed costs; target ≥60% at 100 accounts under realistic maintenance load. If requests are mostly bespoke, sell a separately priced service instead of subsidizing it through the catalogue. |

### What could invalidate the business

Buyers may prefer free skills plus their own test tooling; platform-native features may absorb the audit layer; customer configurations may prevent shared fixes; model upgrades may eliminate the need for individual skills. Simultaneous API breakage can also overwhelm a small maintainer. Track renewals, successful outcomes, support hours and maintenance cost per shared skill—not downloads alone.

Research limit: no reliable count of U.S. buyers for this exact product was established. A defensible market estimate should follow a prospect list and measured conversion, retention and account value. The revenue table deliberately avoids applying an arbitrary share to the broad AI market.

### Sources • retrieved 5 October 2026

[1] Stack Overflow, 2025 Developer Survey: AI
https://survey.stackoverflow.co/2025/ai

[2] Agensi, Sell skills: pricing model and vendor claims
https://www.agensi.io/sell

[3] TrustMRR, Agensi: connected revenue dashboard; figures can change
https://trustmrr.com/startup/agensi

[4] LangChain, LangSmith pricing
https://www.langchain.com/pricing

[5] Langfuse, pricing
https://langfuse.com/pricing

[6] Anthropic, Improving skill-creator: test, measure and refine agent skills
https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills

[7] Zapier, Solution Partner program
https://zapier.com/l/solution-partner
