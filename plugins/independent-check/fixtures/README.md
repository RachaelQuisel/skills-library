# Fixtures

Two paired folders used by `scripts/rehearse.sh`:

- `good/` - a weekly customer-update draft whose values all trace to the customer record. The checker must exit 0.
- `bad/` - the same shape with four planted failures (invented dollar amount, two unreceipted dates, another customer's job name, a unilateral discount phrase). The checker must exit 2 (gate tripped).

The draft files contain real dollar amounts (4,800 and 6,500 with a leading dollar sign) because those strings are what the currency assertion is designed to catch. A security scanner may flag the dollar-prefixed tokens in these files; a reviewer confirms they are prose, not shell variables. The scanner-skip marker used in some reference docs is NOT used here - that marker is reserved for files whose plain-English purpose is documenting a scanner-triggering pattern, which these fixture drafts are not.
