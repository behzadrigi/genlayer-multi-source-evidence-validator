# Contracts Documentation

This document describes the four intelligent contracts in the GenLayer Multi-Source Evidence Validator Suite.

## Contract Overview

| Contract | Purpose | Consensus Pattern |
| :--- | :--- | :--- |
| SourceNormalizer | Normalizes and validates evidence source URLs | Deterministic |
| MultiSourceVerifier | Verifies evidence from multiple sources with identity-bound submission and independent validator recomputation | Custom leader/validator with gl.nondet.web.render and gl.vm.run_nondet_unsafe |
| ConfidenceScorer | Calculates confidence score, reads on-chain from MultiSourceVerifier, reverts on PENDING, prevents double-scoring | Deterministic |
| ReputationGuardian | Manages reputation changes, reads on-chain from ConfidenceScorer, uses lazy default of 50, prevents double-application | Deterministic |

---

## 1. SourceNormalizer

### Purpose
Normalizes and validates evidence source URLs before they are used in verification.

### State Variables
- `sources: TreeMap[u256, NormalizedSource]` - stores normalized sources
- `next_id: u256` - counter for source IDs

### Storage Structure
```python
@allow_storage
@dataclass
class NormalizedSource:
    evidence_id: u256
    original_url: str
    normalized_url: str
    domain: str
    trust_score: u256
    is_whitelisted: bool
    status: str
```

### Write Methods
- `normalize_source(raw_url: str) -> u256` - normalizes URL, checks whitelist/blacklist, returns evidence_id

### Read Methods
- `get_source_status(evidence_id: u256) -> str`
- `get_source_details(evidence_id: u256) -> str`
- `list_sources() -> str`

### Rules
- Converts HTTP to HTTPS
- Removes spaces and trailing slashes
- Blocks localhost, 127.0.0.1, example.com, pastebin.com
- Whitelist: court.gov, justice.gov, archive.org, blockchain.com, etherscan.io, ipfs.io
- Trust score: whitelist (+50), HTTPS (+15), no tracking params (+10)

---

## 2. MultiSourceVerifier

### Purpose
Fetches and verifies evidence from multiple independent sources. Submission is identity-bound to the real transaction sender. A validator independently recomputes every consequential field.

### State Variables
- `verifications: TreeMap[u256, VerificationRecord]` - stores verification records
- `next_id: u256` - counter for verification IDs

### Storage Structure
```python
@allow_storage
@dataclass
class VerificationRecord:
    evidence_id: u256
    agent: str
    claim: str
    sources: str
    verified_count: u256
    total_sources: u256
    status: str
    verified_urls: str
```

### Write Methods

**`submit_evidence(claim: str, sources: str) -> u256`**
- Agent is derived from gl.message.sender_address, not from caller input.
- At least 2 sources required.
- Each source is normalized:
  - HTTP to HTTPS
  - Trailing slash removed
  - Whitespace removed
  - Query string removed
- Uniqueness enforced:
  - No duplicate normalized URLs.
  - No two sources from the same domain.
- Sources stored in normalized form.

**`verify_sources(evidence_id: u256) -> bool`**
- Requires status == "PENDING".
- Requires at least 2 sources.
- Requires source count matches stored total_sources.
- Uses gl.nondet.web.render to fetch each source.
- Uses gl.vm.run_nondet_unsafe for leader/validator consensus.
- Status: VERIFIED (all), PARTIAL (at least half), REJECTED (less than half).
- If a fetch fails, the source is treated as not corroborated (no error).

### Read Methods
- `get_verification_status(evidence_id: u256) -> str`
- `get_verification_details(evidence_id: u256) -> str`
- `get_verification_data(evidence_id: u256) -> str` (raw data for downstream contracts)
- `list_verifications() -> str`
- `get_agent_verifications(agent: str) -> str`

### Validator Recomputation

The validator does not trust the leader's status label. Five independent checks:

1. Shape validation: types, bounds, and total consistency.
2. Independent recomputation: fetch every source, recompute verified_count and status.
3. Invariant check: status must equal compute_status(count, total).
4. Scalar comparison: validator_count == leader_count and validator_status == leader_status.
5. Set comparison: the set of verified URLs must match exactly.

All five checks must pass.

---

## 3. ConfidenceScorer

### Purpose
Calculates a final confidence score based on verification results. Reads verification data on-chain. Reverts on PENDING. Prevents double-scoring.

### Constructor
```python
def __init__(self, verifier_address: str):
    self.next_id = u256(0)
    self.verifier_contract = verifier_address
```

### State Variables
- `scores: TreeMap[u256, ConfidenceRecord]`
- `scored_verifications: TreeMap[u256, bool]`
- `next_id: u256`
- `verifier_contract: str`

### Storage Structure
```python
@allow_storage
@dataclass
class ConfidenceRecord:
    evidence_id: u256
    verification_id: u256
    agent: str
    trust_score: u256
    source_count: u256
    final_score: u256
    status: str
    verifier_address: str
```

### Write Methods

**`calculate_score(verification_id: u256) -> u256`**

Order of operations (critical):
1. Read verification data on-chain.
2. Assert status != "PENDING" (reverts on PENDING).
3. Assert verification_id not in scored_verifications.
4. Compute final_score.
5. Write ConfidenceRecord.
6. Mark scored_verifications[verification_id] = True (last line, successful path only).

### Read Methods
- `get_score(evidence_id: u256) -> str`
- `get_score_details(evidence_id: u256) -> str`
- `get_score_data(evidence_id: u256) -> str`
- `is_verification_scored(verification_id: u256) -> str`
- `list_scores() -> str`

### Scoring Formula
```
base_score = (verified_count / total_sources) * 100
multiplier = VERIFIED: 1.0, PARTIAL: 0.7, REJECTED: 0.3
final_score = int(base_score * multiplier)
status = APPROVED if final_score >= 50 else REJECTED
```

### Security
- Does NOT trust caller-supplied JSON.
- Reads verification directly from MultiSourceVerifier on-chain.
- Reads agent from the on-chain verification record.
- Reverts on PENDING, so PENDING records are not consumed.
- scored_verifications prevents double-scoring.

---

## 4. ReputationGuardian

### Purpose
Manages reputation changes based on approved confidence scores. Reads score data on-chain. Uses lazy default of 50. Prevents double-application.

### Constructor
```python
def __init__(self, scorer_address: str):
    self.next_id = u256(0)
    self.scorer_contract = scorer_address
```

### State Variables
- `changes: TreeMap[u256, ReputationChange]`
- `next_id: u256`
- `reputation: TreeMap[str, u256]`
- `applied_scores: TreeMap[u256, bool]`
- `scorer_contract: str`

### Storage Structure
```python
@allow_storage
@dataclass
class ReputationChange:
    change_id: u256
    agent: str
    score_id: u256
    final_score: u256
    change_type: str
    status: str
    scorer_address: str
```

### Write Methods

**`apply_reputation_change(score_id: u256) -> u256`**
- Asserts score_id not in applied_scores.
- Reads score data from ConfidenceScorer on-chain.
- Reads agent from the score record, never from caller.
- Asserts status == "APPROVED".
- Uses lazy default: current_reputation = self.reputation.get(agent, u256(50)).
- INCREASE if new >= current + 10.
- DECREASE if new <= current - 10.
- NEUTRAL otherwise (rejected).
- Marks applied_scores[score_id] = True.

**`initialize_reputation`**
- REMOVED. Not part of the public interface anymore.
- Lazy default of 50 is applied on first encounter.

### Read Methods
- `get_reputation(agent: str) -> str`
- `is_score_applied(score_id: u256) -> str`
- `get_change_status(change_id: u256) -> str`
- `get_change_details(change_id: u256) -> str`
- `list_changes() -> str`
- `get_agent_changes(agent: str) -> str`

### Security
- Does NOT trust caller-supplied JSON.
- Reads score data directly from ConfidenceScorer on-chain.
- Reads agent from the on-chain score record.
- applied_scores prevents double-application.
- No initialize_reputation removes early-claim attack surface.

---

## Contract Chaining

The v6 architecture uses on-chain chaining:

```
SourceNormalizer -> MultiSourceVerifier -> ConfidenceScorer -> ReputationGuardian
```

- ConfidenceScorer holds MultiSourceVerifier address.
- ReputationGuardian holds ConfidenceScorer address.
- Each downstream contract reads from upstream using gl.get_contract_at(Address(...)).view().get_..._data().
- The agent is propagated from the verification record through the entire chain.

This prevents fabrication of approved scores, agent spoofing, duplicate sources, PENDING consumption, early reputation claim, double scoring, and double application.
