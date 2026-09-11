# GenLayer Multi-Source Evidence Validator Suite

A collection of four GenLayer Intelligent Contracts for multi-source evidence validation, confidence scoring, and reputation management.

## Overview

This project addresses the key improvement suggested by the reviewer: strengthening evidence authority by normalizing caller-selected sources and corroborating them across multiple independent sources before applying reputation outcomes.

The core innovation is contract chaining: each downstream contract reads input directly from the upstream contract on-chain, preventing fabrication of approved scores.

## Contracts

| Contract | Purpose |
| :--- | :--- |
| SourceNormalizer | Normalizes and validates source URLs, checks whitelist/blacklist |
| MultiSourceVerifier | Verifies evidence from multiple sources using real consensus |
| ConfidenceScorer | Calculates confidence score, reads on-chain from MultiSourceVerifier |
| ReputationGuardian | Manages reputation, reads on-chain from ConfidenceScorer |

## Architecture

SourceNormalizer (0xC336e5893510d20e310A41AECF5154F94Aaa404c)
        ↓
MultiSourceVerifier (0x500aBa77fc751967aB02B4deB7bd88553bD75926)
        ↓
ConfidenceScorer (0xC8c2Eb37AF740bC4f327C4D0fe3D26BF3D6C401C)
        ↓
ReputationGuardian (0x20d1e42064Bc02dE8421b3925448bFEdC82BF49b)

## Deployed Contracts and Tests

### SourceNormalizer
- Contract: https://explorer-studio.genlayer.com/address/0xC336e5893510d20e310A41AECF5154F94Aaa404c
- Deploy Tx: https://explorer-studio.genlayer.com/tx/0xb5b58c2400a61d8da6c38500526cd7955f71f3cf968133a0356344968822832f
- Tests: T1-T6 passed

### MultiSourceVerifier
- Contract: https://explorer-studio.genlayer.com/address/0x500aBa77fc751967aB02B4deB7bd88553bD75926
- Deploy Tx: https://explorer-studio.genlayer.com/tx/0xf82797008b693975ea658193538d7b6d95f6222ace271d27cfe4bb71d0fa21c4
- Tests: T1-T7 passed (consensus PARTIAL)

### ConfidenceScorer
- Contract: https://explorer-studio.genlayer.com/address/0xC8c2Eb37AF740bC4f327C4D0fe3D26BF3D6C401C
- Deploy Tx: https://explorer-studio.genlayer.com/tx/0x10dd6110c08a58027a8a9bc2632df57ae0c09f216e59b372ff9aae19cb045da3
- Tests: T1-T5 passed (read on-chain)

### ReputationGuardian
- Contract: https://explorer-studio.genlayer.com/address/0x20d1e42064Bc02dE8421b3925448bFEdC82BF49b
- Deploy Tx: https://explorer-studio.genlayer.com/tx/0xc16b6d48f8768f2de162629e294c132a7bdb9a398255aabe79543a5aad897567
- Tests: T1-T8 passed (on-chain enforced)

## Security Model

1. Fabricated scores prevented: ReputationGuardian reads directly from ConfidenceScorer
2. Fabricated verifications prevented: ConfidenceScorer reads directly from MultiSourceVerifier
3. Tampered evidence prevented: Real consensus with independent validators

## License

MIT
