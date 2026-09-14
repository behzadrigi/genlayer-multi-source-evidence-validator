# GenLayer Multi-Source Evidence Validator Suite

A collection of four GenLayer Intelligent Contracts for multi-source evidence validation, confidence scoring, and reputation management with on-chain contract chaining and independent validator recomputation.

## Overview

This project implements a multi-source evidence validation and reputation system on GenLayer using four interconnected intelligent contracts. It addresses the key improvements suggested by the reviewer:

1. Strengthening evidence authority by normalizing and constraining caller-selected sources
2. Corroborating evidence across multiple independent sources before applying outcomes
3. Binding every downstream action to the authenticated on-chain output of the preceding contract
4. Making the validator independently recompute every consequential field, not just trust the leader's status label

The core innovations are:

- On-chain contract chaining: each downstream contract reads its input directly from the upstream contract on-chain.
- Independent validator recomputation: the validator fetches every source itself, recomputes verified_count, total, status, and verified_urls, and checks the invariant that status equals compute_status(count, total).
- Agent binding: the agent is propagated from the verification record through the entire chain, never from caller input.
- Double-application prevention: each score_id can only be applied once, and each verification_id can only be scored once.

## Contracts

| Contract | Purpose | Consensus Pattern |
| :--- | :--- | :--- |
| SourceNormalizer | Normalizes and validates evidence source URLs, converting HTTP to HTTPS, checking whitelisted and blocked domains | Deterministic |
| MultiSourceVerifier | Fetches and verifies evidence from multiple independent sources using real web content and independent validator recomputation | Custom leader/validator with gl.nondet.web.render and gl.vm.run_nondet_unsafe |
| ConfidenceScorer | Calculates final confidence score, reads verification data on-chain, prevents double-scoring | Deterministic |
| ReputationGuardian | Manages reputation changes, reads score data on-chain, prevents double-application | Deterministic |

## Architecture

```
SourceNormalizer (0xC336e5893510d20e310A41AECF5154F94Aaa404c)
        |
        v
MultiSourceVerifier (0x8D9498DB50bEE3aCe284ecF438ea912F6a69846d)
        | get_verification_data()
        v
ConfidenceScorer (0x0eac9A014d9ab01F038E6C32d9dC4CDa23749F4a)
        | get_score_data()
        v
ReputationGuardian (0xa08c273F5288c9924d9cE7e681802D19E254bAc7)
```

Each downstream contract holds the address of its upstream contract and reads data on-chain. The agent is propagated from the verification record through the entire chain, never from caller input.

## Validator Recomputation (v3)

The MultiSourceVerifier's validator does not trust the leader's status label. It performs five independent checks:

1. Shape validation: leader_count, leader_total, leader_status, and leader_count bounds.
2. Independent recomputation: fetches every source, recomputes verified_count and status.
3. Invariant check: expected_status = compute_status(leader_count, leader_total) must equal leader_status.
4. Scalar comparison: validator_count == leader_count and validator_status == leader_status.
5. Set comparison: the set of verified URLs must match exactly.

All five checks must pass for the result to be accepted.

## Deployed and Tested on GenLayer Studio

### SourceNormalizer (unchanged)

- deploy: `0xC336e5893510d20e310A41AECF5154F94Aaa404c`
  - tx: `0xb5b58c2400a61d8da6c38500526cd7955f71f3cf968133a0356344968822832f`
  - link: https://explorer-studio.genlayer.com/tx/0xb5b58c2400a61d8da6c38500526cd7955f71f3cf968133a0356344968822832f
- normalize_source (valid URL): `0xeb1fbde40b98840ddd95c22f6b5dca370a02140e32b93fc2072fb3bf16347788`
  - link: https://explorer-studio.genlayer.com/tx/0xeb1fbde40b98840ddd95c22f6b5dca370a02140e32b93fc2072fb3bf16347788
- normalize_source (HTTP to HTTPS): `0x3fecdcc0a013db49eacd1cb3036a9bb18496ee2ab65ac2cc63f94f0c02c34a6a`
  - link: https://explorer-studio.genlayer.com/tx/0x3fecdcc0a013db49eacd1cb3036a9bb18496ee2ab65ac2cc63f94f0c02c34a6a
- normalize_source (blocked domain): `0xdaeb19f4101c746aef76d8ff6b300fbb0b54e32f1ce374dbaef2d919fd997533`
  - link: https://explorer-studio.genlayer.com/tx/0xdaeb19f4101c746aef76d8ff6b300fbb0b54e32f1ce374dbaef2d919fd997533
- normalize_source (invalid URL): `0xa9954cdf3992b923b66184bf13966c4c4e1a00626ab40ea4004c0de9d80bbb2b`
  - link: https://explorer-studio.genlayer.com/tx/0xa9954cdf3992b923b66184bf13966c4c4e1a00626ab40ea4004c0de9d80bbb2b

### MultiSourceVerifier (v3)

- deploy: `0x8D9498DB50bEE3aCe284ecF438ea912F6a69846d`
  - tx: `0x890e3484c93f28c444b825b10e602ca16cb5d52418556e6994838261f696dace`
  - link: https://explorer-studio.genlayer.com/tx/0x890e3484c93f28c444b825b10e602ca16cb5d52418556e6994838261f696dace
- submit_evidence: `0x122dd0277d52deab87dff26c7338ee536667295bae3899a09818dfe76fdee2f5`
  - link: https://explorer-studio.genlayer.com/tx/0x122dd0277d52deab87dff26c7338ee536667295bae3899a09818dfe76fdee2f5
- verify_sources (VERIFIED result): `0xbc7a01826d30aade0aa559c4e4877e47143d918d237ddff0314a335e8af59be0`
  - link: https://explorer-studio.genlayer.com/tx/0xbc7a01826d30aade0aa559c4e4877e47143d918d237ddff0314a335e8af59be0
- consensus result: `{"status":"VERIFIED","total":2,"verified_count":2,"verified_urls":"https://www.python.org,https://www.w3schools.com/python/"}`

### ConfidenceScorer (v4)

- deploy: `0x0eac9A014d9ab01F038E6C32d9dC4CDa23749F4a`
  - tx: `0xd64942738dc03c0d07ed2b9c0dd4ccd235b74ddee3ef37ee95f385d3564f8db9`
  - link: https://explorer-studio.genlayer.com/tx/0xd64942738dc03c0d07ed2b9c0dd4ccd235b74ddee3ef37ee95f385d3564f8db9
- upstream address: `0x8D9498DB50bEE3aCe284ecF438ea912F6a69846d`
- calculate_score (read on-chain): `0x574929066c4e849dd6eed7037c6a190b352c486b3479e2be1e52c335e615c25d`
  - link: https://explorer-studio.genlayer.com/tx/0x574929066c4e849dd6eed7037c6a190b352c486b3479e2be1e52c335e615c25d
- score result: `APPROVED:100`

### ReputationGuardian (v5)

- deploy: `0xa08c273F5288c9924d9cE7e681802D19E254bAc7`
  - tx: `0x62afb5681904dcfed46985dca59996fe4a8faf4f8a084772c53ffe713d1af400`
  - link: https://explorer-studio.genlayer.com/tx/0x62afb5681904dcfed46985dca59996fe4a8faf4f8a084772c53ffe713d1af400
- upstream address: `0x0eac9A014d9ab01F038E6C32d9dC4CDa23749F4a`
- initialize_reputation: `0x6441fcbc40594d3fded4f78d0186a50f287aa9e22d6ecdfa561336133f09a80e`
  - link: https://explorer-studio.genlayer.com/tx/0x6441fcbc40594d3fded4f78d0186a50f287aa9e22d6ecdfa561336133f09a80e
- apply_reputation_change (INCREASE, agent from on-chain): `0x5cb5e18136bbae1f71012645ae40bd237f67d917c7223047bfc0432ccfd2dd9c`
  - link: https://explorer-studio.genlayer.com/tx/0x5cb5e18136bbae1f71012645ae40bd237f67d917c7223047bfc0432ccfd2dd9c
- apply_reputation_change (double, blocked): `0x1cc293005fdc1971ed83222870b3ca23ac0aad7497cb0f2eb252d17bd765661e`
  - link: https://explorer-studio.genlayer.com/tx/0x1cc293005fdc1971ed83222870b3ca23ac0aad7497cb0f2eb252d17bd765661e
- reputation result: `REPUTATION:100` (increased from 50)

## Key Improvements Over Previous Version

| Feature | Previous | New |
| :--- | :--- | :--- |
| Evidence sources | Single | Multiple (2+) |
| Source validation | None | Normalize + whitelist/blacklist |
| Confidence scoring | Verdict only | Numeric (0-100) |
| Downstream data | Caller JSON | On-chain reading |
| Agent binding | Caller-supplied | On-chain from verification |
| Validator checks | Status label only | Independent recomputation of every field |
| Double scoring | Not prevented | Prevented via scored_verifications |
| Double application | Not prevented | Prevented via applied_scores |
| Verification | Independent LLM | Real consensus with independent recomputation |

## Security Model

1. Fabricated scores prevented: ReputationGuardian reads score directly from ConfidenceScorer on-chain.
2. Fabricated verifications prevented: ConfidenceScorer reads verification directly from MultiSourceVerifier on-chain.
3. Agent spoofing prevented: agent is read from the on-chain verification record, never from caller.
4. Double scoring prevented: each verification_id can only be scored once.
5. Double application prevented: each score_id can only be applied once.
6. Leader manipulation prevented: validator independently recomputes every consequential field.
7. Tampered evidence prevented: MultiSourceVerifier uses real consensus with independent validators.

## Test Summary

All contracts have been fully tested on GenLayer Studio:

| Contract | Tests | All Passed |
| :--- | :--- | :--- |
| SourceNormalizer | 6 | Yes |
| MultiSourceVerifier | 7 | Yes |
| ConfidenceScorer | 6 | Yes |
| ReputationGuardian | 10 | Yes |

## Full Successful Chain (VERIFIED to INCREASE)

1. MultiSourceVerifier.submit_evidence() -> evidence_id 1
2. MultiSourceVerifier.verify_sources(1) -> VERIFIED (2/2)
3. ConfidenceScorer.calculate_score(1) -> score_id 0
4. ConfidenceScorer.get_score(0) -> APPROVED:100
5. ReputationGuardian.apply_reputation_change(0) -> change_id 0 (agent read on-chain)
6. ReputationGuardian.get_reputation("0xTestAgent") -> REPUTATION:100 (increased from 50)

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
