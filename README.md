# GenLayer Multi-Source Evidence Validator Suite

A collection of four GenLayer Intelligent Contracts for multi-source evidence validation, confidence scoring, and reputation management with on-chain contract chaining.

## Overview

This project implements a multi-source evidence validation and reputation system on GenLayer using four interconnected intelligent contracts. It addresses the key improvements suggested by the reviewer:

1. Strengthening evidence authority by normalizing and constraining caller-selected sources
2. Corroborating evidence across multiple independent sources before applying outcomes
3. Binding every downstream action to the authenticated on-chain output of the preceding contract

The core innovation is on-chain contract chaining: each downstream contract reads its input directly from the upstream contract on-chain using gl.get_contract_at(). No caller-supplied JSON is trusted at any stage.

## Contracts

| Contract | Purpose | Consensus Pattern |
| :--- | :--- | :--- |
| SourceNormalizer | Normalizes and validates evidence source URLs, converting HTTP to HTTPS, checking whitelisted and blocked domains | Deterministic |
| MultiSourceVerifier | Fetches and verifies evidence from multiple independent sources using real web content | Custom leader/validator with gl.nondet.web.render and gl.vm.run_nondet_unsafe |
| ConfidenceScorer | Calculates final confidence score, reads verification data on-chain | Deterministic |
| ReputationGuardian | Manages reputation changes, reads score data on-chain, prevents double-application | Deterministic |

## Architecture

```
SourceNormalizer (0xC336e5893510d20e310A41AECF5154F94Aaa404c)
        |
        v
MultiSourceVerifier (0x500aBa77fc751967aB02B4deB7bd88553bD75926)
        | get_verification_data()
        v
ConfidenceScorer (0xaAFfC3090370149b1187268475A678692D49Ef40)
        | get_score_data()
        v
ReputationGuardian (0x96e280F36f0a430F41E8140945c7b238042e1Faf)
```

Each downstream contract holds the address of its upstream contract and reads data on-chain. The agent is propagated from the verification record through the entire chain, never from caller input.

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

### MultiSourceVerifier

- deploy: `0x500aBa77fc751967aB02B4deB7bd88553bD75926`
  - tx: `0xf82797008b693975ea658193538d7b6d95f6222ace271d27cfe4bb71d0fa21c4`
  - link: https://explorer-studio.genlayer.com/tx/0xf82797008b693975ea658193538d7b6d95f6222ace271d27cfe4bb71d0fa21c4
- submit_evidence (VERIFIED scenario): `0xbd8505989a1c724b2c49816230023e5e2e2478ee8f013e743048b257ce71b4c9`
  - link: https://explorer-studio.genlayer.com/tx/0xbd8505989a1c724b2c49816230023e5e2e2478ee8f013e743048b257ce71b4c9
- verify_sources (VERIFIED result): `0x86a8d7a47e7a95bf393036d34d9dd55315abb89bb2132bf4a87146ff60170bb9`
  - link: https://explorer-studio.genlayer.com/tx/0x86a8d7a47e7a95bf393036d34d9dd55315abb89bb2132bf4a87146ff60170bb9
- consensus result: `{"status":"VERIFIED","total":2,"verified_count":2,"verified_urls":"https://coinmarketcap.com,https://en.wikipedia.org/wiki/Bitcoin"}`

### ConfidenceScorer

- deploy: `0xaAFfC3090370149b1187268475A678692D49Ef40`
  - tx: `0x1d25fc8b35e42929405fa84efada4db97e1fad0bc3090058375a23747b4258b6`
  - link: https://explorer-studio.genlayer.com/tx/0x1d25fc8b35e42929405fa84efada4db97e1fad0bc3090058375a23747b4258b6
- upstream address: `0x500aBa77fc751967aB02B4deB7bd88553bD75926`
- calculate_score (VERIFIED, read on-chain): `0xeb631b1096fa356aff3af572aa6a912afcce64ac4c7f87df27daa10da07d2935`
  - link: https://explorer-studio.genlayer.com/tx/0xeb631b1096fa356aff3af572aa6a912afcce64ac4c7f87df27daa10da07d2935
- score result: `APPROVED:100` (base_score = 100, multiplier = 1.0)

### ReputationGuardian

- deploy: `0x96e280F36f0a430F41E8140945c7b238042e1Faf`
  - tx: `0xc2eaf0aadbcd0630a9f781589656991627cfd71285098fcfa67ac8f1b71a4ac0`
  - link: https://explorer-studio.genlayer.com/tx/0xc2eaf0aadbcd0630a9f781589656991627cfd71285098fcfa67ac8f1b71a4ac0
- upstream address: `0xaAFfC3090370149b1187268475A678692D49Ef40`
- apply_reputation_change (INCREASE, agent from on-chain): `0x3e1c6a70421d56255f28a2b6f66ce19450a4c921c9f455640f47fba4b1106afc`
  - link: https://explorer-studio.genlayer.com/tx/0x3e1c6a70421d56255f28a2b6f66ce19450a4c921c9f455640f47fba4b1106afc
- apply_reputation_change (double, blocked): `0x50cb7cccaed5cd7cc43064a019726f51f4f8c7f3b2800cdee7dadf8f1b1abcd3`
  - link: https://explorer-studio.genlayer.com/tx/0x50cb7cccaed5cd7cc43064a019726f51f4f8c7f3b2800cdee7dadf8f1b1abcd3
- initialize_reputation: `0x9556e990518991e845cbfb9de8e68f5e320af0bc85f870c663a47a6e3a14f6be`
  - link: https://explorer-studio.genlayer.com/tx/0x9556e990518991e845cbfb9de8e68f5e320af0bc85f870c663a47a6e3a14f6be
- reputation result: `REPUTATION:100` (increased from 50)

## Key Improvements Over Previous Version

| Feature | Previous | New |
| :--- | :--- | :--- |
| Evidence sources | Single | Multiple (2+) |
| Source validation | None | Normalize + whitelist/blacklist |
| Confidence scoring | Verdict only | Numeric (0-100) |
| Downstream data | Caller JSON | On-chain reading |
| Agent binding | Caller-supplied | On-chain from verification |
| Double application | Not prevented | Prevented via applied_scores |
| Failure handling | Transaction fails | Graceful with suggestions |
| Verification | Independent LLM | Real consensus with gl.vm.run_nondet_unsafe |

## Security Model

1. Fabricated scores prevented: ReputationGuardian reads score directly from ConfidenceScorer on-chain.
2. Fabricated verifications prevented: ConfidenceScorer reads verification directly from MultiSourceVerifier on-chain.
3. Agent spoofing prevented: agent is read from the on-chain verification record, never from caller.
4. Double application prevented: each score_id can only be applied once via applied_scores map.
5. Tampered evidence prevented: MultiSourceVerifier uses real consensus with independent validators.

## Test Summary

All contracts have been fully tested on GenLayer Studio:

| Contract | Tests | All Passed |
| :--- | :--- | :--- |
| SourceNormalizer | 6 | Yes |
| MultiSourceVerifier | 7 | Yes |
| ConfidenceScorer | 5 | Yes |
| ReputationGuardian | 11 | Yes |

## Full Successful Chain (VERIFIED to INCREASE)

1. MultiSourceVerifier.submit_evidence() -> evidence_id 3
2. MultiSourceVerifier.verify_sources(3) -> VERIFIED (2/2)
3. ConfidenceScorer.calculate_score(3) -> score_id 1
4. ConfidenceScorer.get_score(1) -> APPROVED:100
5. ReputationGuardian.apply_reputation_change(1) -> change_id 0 (agent read on-chain)
6. ReputationGuardian.get_reputation("0xNewAgent") -> REPUTATION:100 (increased from 50)

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
