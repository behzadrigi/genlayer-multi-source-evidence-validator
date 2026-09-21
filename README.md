# GenLayer Multi-Source Evidence Validator Suite

A collection of four GenLayer Intelligent Contracts for multi-source evidence validation, confidence scoring, and reputation management with on-chain contract chaining, independent validator recomputation, and identity-bound evidence submission.

## Overview

This project implements a multi-source evidence validation and reputation system on GenLayer using four interconnected intelligent contracts. It addresses every concern raised by the reviewer across multiple rounds of feedback:

1. Strengthening evidence authority by normalizing and constraining caller-selected sources
2. Corroborating evidence across multiple independent sources before applying outcomes
3. Binding every downstream action to the authenticated on-chain output of the preceding contract
4. Making the validator independently recompute every consequential field
5. Binding each verification's agent to the real transaction sender
6. Allowing scoring only after the upstream verification reaches a final status, without consuming PENDING records
7. Removing early reputation claim via lazy default initialization
8. Enforcing genuinely distinct evidence sources by URL and by domain

The core innovations are:

- On-chain contract chaining: each downstream contract reads its input directly from the upstream contract on-chain.
- Independent validator recomputation: the validator fetches every source itself, recomputes verified_count, total, status, and verified_urls, and checks the invariant that status equals compute_status(count, total).
- Identity-bound submission: the agent is derived from gl.message.sender_address, never from caller input.
- Lazy reputation default: no explicit initialization step, eliminating the race to claim an agent first.
- Source independence: URLs are normalized, deduplicated by URL and by domain, and stored normalized.
- Final-status-only scoring: calculate_score reverts on PENDING, and never marks a record as scored unless it reaches a final status.
- Double-application prevention: each score_id can only be applied once, and each verification_id can only be scored once.

## Contracts

| Contract | Purpose | Consensus Pattern |
| :--- | :--- | :--- |
| SourceNormalizer | Normalizes and validates evidence source URLs, converting HTTP to HTTPS, checking whitelisted and blocked domains | Deterministic |
| MultiSourceVerifier | Fetches and verifies evidence from multiple independent sources with identity-bound submission and independent validator recomputation | Custom leader/validator with gl.nondet.web.render and gl.vm.run_nondet_unsafe |
| ConfidenceScorer | Calculates final confidence score, reads verification data on-chain, reverts on PENDING, prevents double-scoring | Deterministic |
| ReputationGuardian | Manages reputation changes, reads score data on-chain, prevents double-application, uses lazy default of 50 | Deterministic |

## Architecture

```
SourceNormalizer (0xC336e5893510d20e310A41AECF5154F94Aaa404c)
        |
        v
MultiSourceVerifier (0xFA4331084CE100F086bDCFcCe16028BFbd374BcF)
        | get_verification_data()
        v
ConfidenceScorer (0x9a9F31f2f36778cF99aB31c97AB3ace362Cf8A06)
        | get_score_data()
        v
ReputationGuardian (0x4555Ac4138D751DBF52Dd75B8da6FdA1Fdcc73FE)
```

Each downstream contract holds the address of its upstream contract and reads data on-chain. The agent is propagated from the verification record through the entire chain, never from caller input.

## Validator Recomputation

The MultiSourceVerifier's validator does not trust the leader's status label. It performs five independent checks:

1. Shape validation: leader_count, leader_total, leader_status, and leader_count bounds.
2. Independent recomputation: fetches every source, recomputes verified_count and status.
3. Invariant check: expected_status = compute_status(leader_count, leader_total) must equal leader_status.
4. Scalar comparison: validator_count == leader_count and validator_status == leader_status.
5. Set comparison: the set of verified URLs must match exactly.

All five checks must pass for the result to be accepted.

## Identity Binding

submit_evidence no longer accepts an agent parameter. The agent is derived from gl.message.sender_address. This prevents any caller from submitting evidence on behalf of another agent.

## Source Independence

submit_evidence enforces:

- URL normalization (HTTP to HTTPS, trailing slash removal, query string removal).
- Uniqueness by normalized URL: duplicate URLs are rejected.
- Uniqueness by domain: two sources from the same domain are rejected.

## Final-Status-Only Scoring

calculate_score:

- Reverts if the upstream verification is still PENDING.
- Reverts if the verification was already scored.
- Only marks scored_verifications on the successful path.

This ensures a PENDING record is never permanently consumed.

## Lazy Reputation Initialization

ReputationGuardian no longer exposes initialize_reputation. A lazy default of 50 is provided by self.reputation.get(agent, u256(50)) on first encounter. This removes the attack surface where anyone could claim an agent before its real owner.

## Deployed and Tested on GenLayer Studio

### SourceNormalizer (unchanged)

- deploy: `0xC336e5893510d20e310A41AECF5154F94Aaa404c`
  - tx: `0xb5b58c2400a61d8da6c38500526cd7955f71f3cf968133a0356344968822832f`
- normalize_source (valid URL): `0xeb1fbde40b98840ddd95c22f6b5dca370a02140e32b93fc2072fb3bf16347788`
- normalize_source (HTTP to HTTPS): `0x3fecdcc0a013db49eacd1cb3036a9bb18496ee2ab65ac2cc63f94f0c02c34a6a`
- normalize_source (blocked domain): `0xdaeb19f4101c746aef76d8ff6b300fbb0b54e32f1ce374dbaef2d919fd997533`
- normalize_source (invalid URL): `0xa9954cdf3992b923b66184bf13966c4c4e1a00626ab40ea4004c0de9d80bbb2b`

### MultiSourceVerifier (v4)

- deploy: `0xFA4331084CE100F086bDCFcCe16028BFbd374BcF`
  - tx: `0xd53785753a922cf5b28b2ba87457243ce63c0fc27bee9fa54867ad82400d29b0`
- submit_evidence (no agent param): `0x077a106c7dcc2e298f0008b855231bfba38965bba2fa7beae1b2f82b21b65937`
- submit_evidence (duplicate URL, blocked): `0x718acc1dcf8c219a4879d1a4d37bf6acbdbd66cf2c7bc4f6a25147793bdd0680`
- submit_evidence (duplicate domain, blocked): `0x1c2306cfbbd44f1b3658d1a0d8c9ff86cf632a9aa4a61a735edac452a3ab9a59`
- submit_evidence (PENDING test): `0x8dc721ab949a6267885bb71334e56ea674d2443b294f0623390807da639fce76`
- verify_sources (VERIFIED): `0xd8c7f5251bcf39b1d8477aa7e694444506b89bdd655d8752a523f8cba72c68d2`
- verify_sources (REJECTED): `0x4d2d9602fa032b055843b91b21bfd7ff5d6a21500c6932455b2bb6176168bc08`

### ConfidenceScorer (v5)

- deploy: `0x9a9F31f2f36778cF99aB31c97AB3ace362Cf8A06`
  - tx: `0x8d4cc5906d499a1fc21494cad176a501014e62dcb0e5624ebf38558b77a0230a`
- calculate_score on PENDING (reverted, expected): `0xfc34cb7f291ccb42d18f86ddd5e9ddbc2a06259d8a975fb5addb5ee484a9dd83`
- calculate_score after verify (REJECTED): `0x19eeff89ef2f702534362a0872613c57c41230119461615a72cea3be9e3b5e84`
- calculate_score after verify (VERIFIED): `0xbddee6e180fb156ffddec89b2e4fb8313207d760842713d6f25ade92a743459f`
- calculate_score double (blocked): `0x23ffa0233e89793126b1858108716e2d067749e3703ad22542efed44560197a6`

### ReputationGuardian (v6)

- deploy: `0x4555Ac4138D751DBF52Dd75B8da6FdA1Fdcc73FE`
  - tx: `0x3524889d2d9e43dd359fe32a4044cc8d2d45caf3e5155de3a12c8ee10b9a9aa1`
- apply_reputation_change (INCREASE, agent from on-chain): `0x018599cc7cf824e4a304b23fe26b193aa1ed30c0e97563b97f25e78479cd1edd`
- apply_reputation_change (double, blocked): `0xd08a21b8cd0676a261a82a30de6ca830031cdafec2f5d39266b1357c42a85a9d`

## Key Improvements Over Previous Version

| Feature | Previous | New |
| :--- | :--- | :--- |
| Evidence sources | Single | Multiple (2+) |
| Source validation | None | Normalize + whitelist/blacklist |
| Source independence | Not enforced | Unique URL and unique domain |
| Confidence scoring | Verdict only | Numeric (0-100) |
| Downstream data | Caller JSON | On-chain reading |
| Agent binding | Caller-supplied | gl.message.sender_address |
| Validator checks | Status label only | Independent recomputation of every field |
| PENDING handling | Could be consumed | Reverts, never consumed |
| Reputation init | Explicit, race-prone | Removed, lazy default of 50 |
| Double scoring | Not prevented | Prevented via scored_verifications |
| Double application | Not prevented | Prevented via applied_scores |
| Verification | Independent LLM | Real consensus with independent recomputation |

## Security Model

1. Fabricated scores prevented: ReputationGuardian reads score directly from ConfidenceScorer on-chain.
2. Fabricated verifications prevented: ConfidenceScorer reads verification directly from MultiSourceVerifier on-chain.
3. Agent spoofing prevented: agent is derived from gl.message.sender_address, never from caller.
4. Duplicate sources prevented: URL and domain uniqueness enforced at submit time.
5. PENDING consumption prevented: calculate_score reverts on PENDING and only marks scored on success.
6. Early reputation claim prevented: initialize_reputation removed, lazy default of 50 applied on first use.
7. Double scoring prevented: each verification_id can only be scored once.
8. Double application prevented: each score_id can only be applied once.
9. Leader manipulation prevented: validator independently recomputes every consequential field.

## Test Summary

All contracts have been fully tested on GenLayer Studio:

| Contract | Tests | All Passed |
| :--- | :--- | :--- |
| SourceNormalizer | 6 | Yes |
| MultiSourceVerifier | 8 | Yes |
| ConfidenceScorer | 10 | Yes |
| ReputationGuardian | 9 | Yes |

## Full Successful Chain (VERIFIED to INCREASE)

1. MultiSourceVerifier.submit_evidence() -> evidence_id 0 (agent from sender_address)
2. MultiSourceVerifier.verify_sources(0) -> VERIFIED (2/2)
3. ConfidenceScorer.calculate_score(0) -> score_id 1
4. ConfidenceScorer.get_score(1) -> APPROVED:100
5. ReputationGuardian.apply_reputation_change(1) -> change_id 0
6. ReputationGuardian.get_reputation(agent) -> REPUTATION:100 (lazy default 50 -> 100)

## Files

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
```

## License

MIT
