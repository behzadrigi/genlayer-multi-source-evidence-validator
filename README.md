# Multi-Source Evidence Validator Suite

A 4-contract GenLayer Intelligent Contract suite that validates evidence claims by
corroborating them across **multiple independent sources**, then applies reputation
outcomes only once real validator consensus is reached — rather than trusting a single
caller-chosen URL or a caller-supplied verdict.

## Why this exists

Most simple evidence-checking designs (including our own earlier suite) fetch and judge
a single caller-chosen source. A single source can be wrong, outdated, or misleading.
This suite requires at least two independent sources per claim, has each source fetched
live on-chain, and only accepts a verification result once independent GenLayer
validators agree on it.

This directly follows up on steward feedback from our prior submission (Deliverable
Arbitration Suite v2 / EdVista), which suggested normalizing/constraining sources and
corroborating claims across multiple independent sources before applying reputation
outcomes.

## Architecture

```
Caller
  │
  ▼
1. SourceNormalizer          deterministic — cleans a URL, extracts its domain,
                              checks it against a whitelist/blocklist, scores trust
  │
  ▼
2. MultiSourceVerifier        non-deterministic, consensus-based — fetches every
                              source URL live via gl.nondet.web.render, asks the
                              model whether each page corroborates the claim, and
                              only accepts the result once independent validators
                              agree on both the status and the verified count
  │
  ▼
3. ConfidenceScorer            deterministic — converts the verification status into
                              a 0-100 score and an APPROVED/REJECTED decision
  │
  ▼
4. ReputationGuardian          deterministic — applies an INCREASE/DECREASE to an
                              agent's reputation, but only for an APPROVED score
```

The four contracts are deployed independently and are not wired to call each other
on-chain; a caller (or off-chain agent) passes each contract's output into the next
step. This mirrors the design of our EdVista suite and keeps each contract's safety
properties independently auditable.

## Use case

An insurer verifying a claim (e.g. a police report, scene photos, and a medical
report) before adjusting a party's trust score — a decision should not rest on a
single, unverified document.

## Contracts and addresses (GenLayer Studio)

| Contract | Address |
|---|---|
| SourceNormalizer | `0xC336e5893510d20e310A41AECF5154F94Aaa404c` |
| MultiSourceVerifier | `0x47B07b947953a25AbdD572Ed62b575022E0868af` |
| ConfidenceScorer | `0xEbccF9Af883AA7B3A46F08dcf455B2b55D74077c` |
| ReputationGuardian | `0xb49467e57718A5F8940D6C43cfC14D542FEC10C0` |

See [CONTRACTS.md](./CONTRACTS.md) for per-contract detail and [DECISIONS.md](./DECISIONS.md)
for design rationale. Integration tests live under [tests/](./tests).

## Repo structure

```
contracts/
  SourceNormalizer.py
  MultiSourceVerifier.py
  ConfidenceScorer.py
  ReputationGuardian.py
tests/
  test_source_normalizer.py
  test_multi_source_verifier.py
  test_confidence_scorer.py
  test_reputation_guardian.py
README.md
CONTRACTS.md
DECISIONS.md
LICENSE
```
