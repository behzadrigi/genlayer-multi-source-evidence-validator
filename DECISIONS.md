# Design Decisions

## Why 4 separate contracts instead of one

Each stage of evidence handling — normalizing a source, corroborating a claim across
sources, scoring confidence, applying a reputation outcome — has a genuinely different
risk profile and a genuinely different need (or lack of need) for LLM/validator
consensus. Splitting them keeps each contract's safety properties independently
auditable and lets each one be reused on its own by other projects.

## Why MultiSourceVerifier fetches sources itself instead of trusting a caller-supplied result

Our first design let the caller pass a `leader_result` JSON string directly into
`verify_sources`, i.e. the caller simply asserted which sources were "verified." That
is not corroboration — it's a caller-authored claim with no independent check behind
it, which defeats the entire purpose of a contract named "verifier." The corrected
design has the contract itself call `gl.nondet.web.render` on every source URL and
`gl.nondet.exec_prompt` to judge corroboration, then only accepts a result once
independent validators re-run that exact routine and agree. This follows the same
principle that shaped our EdVista suite after the original `genlayer-contracts`
rejection: an LLM should never judge a claim of fact without the contract fetching the
underlying material itself.

## Why the multi-source requirement (≥2) instead of a single evidence URL

A single source, however well-fetched, can still be wrong, outdated, or one-sided.
Requiring at least two independent sources and comparing their corroboration status is
a direct, concrete implementation of the "corroborate across multiple independent
sources" improvement suggested on our prior submission, rather than only fetching one
caller-chosen link.

## Why `verified_count`/`status` are compared across validators, not just range-checked

We previously had a rejection where a payout-relevant percentage was only range-checked
inside the leader function, not actually compared across independent validator runs —
which meant the leader's number was trusted rather than agreed on. Here,
`validator_fn` recomputes `check_sources()` from scratch and requires an exact match on
both `status` and `verified_count` before accepting the leader's result, so the
verification outcome is genuinely bound by consensus.

## Why SourceNormalizer, ConfidenceScorer, and ReputationGuardian are fully deterministic

None of these three involve judging an ambiguous real-world claim — they involve
string/URL processing, arithmetic on numbers already produced by a consensus step, and
bookkeeping. Using GenLayer's non-deterministic/consensus machinery where it isn't
needed only adds gas cost and complexity without adding any real safety guarantee.
Restricting LLM/consensus usage to the one contract that actually needs to judge a
real-world claim (MultiSourceVerifier) is a deliberate design choice, not an omission.

## Why helper logic lives in module-level functions, not undecorated instance methods

GenLayer Studio fails to load a contract's schema ("Could not load contract schema")
if a `gl.Contract` subclass has any plain instance method without a `@gl.public.write`
or `@gl.public.view` decorator. All private helper logic (`clean_url`, `extract_domain`,
`calculate_trust`, `is_valid_url`, `check_sources`) is therefore implemented as a
module-level function instead of a method on `self`.

## Why no contract calls another on-chain

Each contract is independently deployed and callable on its own, and a caller (or an
off-chain orchestrating agent) is expected to read one contract's output and pass it
as input to the next. This keeps each contract's interface simple and testable in
isolation, and matches the design already used in our EdVista suite.

## Known limitation / next test still needed

Every scenario tested so far (`Ethereum price is over $3000`, `Bitcoin is the largest
cryptocurrency by market cap`) resulted in `REJECTED` or `PARTIAL` verification, which
in turn produced a `ConfidenceScorer` score below 50 (`REJECTED`). This means
`ReputationGuardian.apply_reputation_change`'s main path — actually applying an
`INCREASE`/`DECREASE` from a genuinely `APPROVED` score — has not yet been exercised
end-to-end; only its guard rail (rejecting a non-approved score, tests T3/T5) has been
confirmed. Before submission, one more evidence item should be tested with two sources
that fully corroborate the same claim (`VERIFIED`, 2/2) so the full pipeline can be
proven to reach an actual reputation change on-chain.
