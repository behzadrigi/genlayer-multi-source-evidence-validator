# Design Decisions

This document explains the architectural and design decisions behind the GenLayer Multi-Source Evidence Validator Suite.

## 1. Why Multi-Source Verification?

### Problem
In the previous version (EdVista), each piece of evidence was backed by a single source. If that source was wrong, fake, or misleading, the entire decision would be incorrect.

### Solution
The MultiSourceVerifier requires at least 2 independent sources for each evidence claim. This reduces the risk of a single point of failure and makes fabrication much harder.

### Trade-off
- More sources mean more gas and more processing time.
- But the security improvement is worth the extra cost.

---

## 2. Why URL Normalization?

### Problem
Without normalization, the same URL could be written in many different ways (`http://`, `https://`, trailing slash, extra spaces), leading to inconsistent verification results.

### Solution
The SourceNormalizer cleans and normalizes all URLs before they reach the verification stage. It also blocks dangerous domains and rewards trusted ones with a higher trust score.

### Trade-off
- Normalization adds an extra step.
- But it prevents a wide range of URL-based attacks and inconsistencies.

---

## 3. Why Deterministic Scoring Instead of LLM?

### Problem
Using an LLM to calculate the final confidence score would add cost, latency, and non-determinism.

### Solution
The ConfidenceScorer uses a simple, deterministic formula:
```
base_score = (verified_count / total_sources) * 100
multiplier = VERIFIED: 1.0, PARTIAL: 0.7, REJECTED: 0.3
final_score = base_score * multiplier
```

### Trade-off
- The formula is less flexible than an LLM.
- But it is fast, cheap, and fully predictable, which is critical for a scoring system.

---

## 4. Why Contract Chaining (v2)?

### Problem
In v1, downstream contracts (ConfidenceScorer, ReputationGuardian) trusted caller-supplied JSON for verification and score data. This allowed anyone to fabricate an approved score and change an agent's reputation without a verified evidence record.

### Solution
Each downstream contract now reads its input directly from the upstream contract on-chain:

- ConfidenceScorer stores the MultiSourceVerifier address and calls `get_verification_data()` on-chain.
- ReputationGuardian stores the ConfidenceScorer address and calls `get_score_data()` on-chain.

### Why This Matters
1. Only verified on-chain data can influence reputation.
2. No caller-supplied JSON can fabricate a score.
3. Every reputation change is traceable to a verified evidence record.

### Trade-off
- Contracts are now coupled through their constructors.
- But the security improvement is essential for a reputation system.

---

## 5. Why Include Verified URLs in Storage?

### Problem
Downstream contracts need to know not just how many sources were verified, but which specific sources were verified.

### Solution
The VerificationRecord stores a `verified_urls` field as a comma-separated string.

### Trade-off
- Storing URLs increases storage usage slightly.
- But it provides full transparency and traceability for every verification.

---

## 6. Why Two Separate Downstream Contracts?

### Problem
Why not combine ConfidenceScorer and ReputationGuardian into a single contract?

### Solution
Separating them provides:
- Single responsibility: each contract does one thing well.
- Easier testing: each contract can be tested independently.
- Better upgradability: one contract can be redeployed without affecting the other.

### Trade-off
- More contracts mean more deployment steps.
- But the modular architecture is easier to maintain and audit.

---

## 7. Why Use gl.vm.run_nondet_unsafe Instead of Simple LLM Calls?

### Problem
A single LLM call could be manipulated or produce inconsistent results.

### Solution
The MultiSourceVerifier uses `gl.vm.run_nondet_unsafe` with a leader/validator pattern:
- The leader fetches content and asks the LLM to check corroboration.
- Independent validators verify the leader's result.
- Consensus is required for the result to be accepted.

### Trade-off
- More complex and slower than a simple LLM call.
- But it provides real, independent verification, which is the core value of GenLayer.

---

## 8. Why Expose `get_..._data` View Methods?

### Problem
Downstream contracts need to read structured data from upstream contracts without parsing complex JSON.

### Solution
Each upstream contract exposes a dedicated view method:
- `get_verification_data(evidence_id)` in MultiSourceVerifier
- `get_score_data(evidence_id)` in ConfidenceScorer

These methods return a clean, minimal JSON payload specifically designed for downstream consumption.

### Trade-off
- Adds a few extra lines of code.
- But it makes the chaining clean, consistent, and easy to extend.

---

## Summary

| Decision | Reason |
| :--- | :--- |
| Multi-source verification | Reduces single point of failure |
| URL normalization | Prevents inconsistencies and attacks |
| Deterministic scoring | Fast, cheap, predictable |
| Contract chaining | Prevents fabrication of scores |
| Store verified URLs | Full transparency and traceability |
| Separate downstream contracts | Modular, testable, upgradable |
| Use gl.vm.run_nondet_unsafe | Real independent verification |
| Expose get_..._data methods | Clean, consistent chaining |

---

All decisions prioritize security, transparency, and modularity over minimalism, because a reputation system must be trustworthy above all else.
