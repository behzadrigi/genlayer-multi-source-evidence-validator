# Contracts Documentation

This document describes the four intelligent contracts in the GenLayer Multi-Source Evidence Validator Suite.

## Contract Overview

| Contract | Purpose | Consensus Pattern |
| :--- | :--- | :--- |
| SourceNormalizer | Normalizes and validates evidence source URLs | Deterministic |
| MultiSourceVerifier | Verifies evidence from multiple sources with independent validator recomputation | Custom leader/validator with gl.nondet.web.render and gl.vm.run_nondet_unsafe |
| ConfidenceScorer | Calculates confidence score, reads on-chain from MultiSourceVerifier, prevents double-scoring | Deterministic |
| ReputationGuardian | Manages reputation changes, reads on-chain from ConfidenceScorer, prevents double-application | Deterministic |

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
Fetches and verifies evidence from multiple independent sources using real web content and a validator that independently recomputes every consequential field.

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
- `submit_evidence(agent: str, claim: str, sources: str) -> u256` - registers a new evidence claim
- `verify_sources(evidence_id: u256) -> bool` - runs consensus verification with independent validator recomputation

### Read Methods
- `get_verification_status(evidence_id: u256) -> str`
- `get_verification_details(evidence_id: u256) -> str`
- `get_verification_data(evidence_id: u256) -> str` - raw data for downstream contracts
- `list_verifications() -> str`
- `get_agent_verifications(agent: str) -> str`

### Consensus Pattern (v3)

The validator does not trust the leader's status label. It performs five independent checks:

1. Shape validation:
   - leader_count must be int
   - leader_total must be int and must equal len(source_list)
   - leader_status must be in ("VERIFIED", "PARTIAL", "REJECTED")
   - leader_count must be in [0, leader_total]
2. Independent recomputation:
   - For each source in source_list, validator calls `_evaluate_one_source()`
   - validator_count = len(validator_urls)
   - validator_status = `_compute_status(validator_count, len(source_list))`
3. Invariant check on leader output:
   - expected_status = `_compute_status(leader_count, leader_total)`
   - if expected_status != leader_status: return False
4. Scalar comparison:
   - if validator_count != leader_count: return False
   - if validator_status != leader_status: return False
5. Set comparison:
   - leader_set = set of leader_urls_str split by comma
   - validator_set = set of validator_urls
   - if leader_set != validator_set: return False

All five checks must pass for the result to be accepted.

### Rules
- At least 2 sources required (checked at submit time and again at verify time)
- Source count must match the stored total_sources
- All sources must be valid URLs
- If fetch fails, source is treated as not corroborated (no error)

---

## 3. ConfidenceScorer

### Purpose
Calculates a final confidence score based on verification results, read on-chain from MultiSourceVerifier. Prevents scoring the same verification twice.

### Constructor
```python
def __init__(self, verifier_address: str):
    self.next_id = u256(0)
    self.verifier_contract = verifier_address
```

### State Variables
- `scores: TreeMap[u256, ConfidenceRecord]` - stores confidence records
- `scored_verifications: TreeMap[u256, bool]` - tracks verification IDs that have been scored
- `next_id: u256` - counter for score IDs
- `verifier_contract: str` - address of MultiSourceVerifier contract

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
- `calculate_score(verification_id: u256) -> u256` - reads from MultiSourceVerifier on-chain, returns score_id

### Read Methods
- `get_score(evidence_id: u256) -> str`
- `get_score_details(evidence_id: u256) -> str`
- `get_score_data(evidence_id: u256) -> str` - raw data for downstream contracts
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
- Does NOT trust caller-supplied JSON
- Reads verification data directly from MultiSourceVerifier on-chain using gl.get_contract_at()
- Reads agent from the on-chain verification record, not from caller
- Prevents scoring the same verification twice via scored_verifications map

---

## 4. ReputationGuardian

### Purpose
Manages reputation changes based on approved confidence scores, read on-chain from ConfidenceScorer. Prevents applying the same score twice.

### Constructor
```python
def __init__(self, scorer_address: str):
    self.next_id = u256(0)
    self.scorer_contract = scorer_address
```

### State Variables
- `changes: TreeMap[u256, ReputationChange]` - stores reputation changes
- `next_id: u256` - counter for change IDs
- `reputation: TreeMap[str, u256]` - agent reputation scores
- `applied_scores: TreeMap[u256, bool]` - tracks score IDs that have been applied
- `scorer_contract: str` - address of ConfidenceScorer contract

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
- `apply_reputation_change(score_id: u256) -> u256` - reads from ConfidenceScorer on-chain, returns change_id
- `initialize_reputation(agent: str, initial_score: u256)` - sets initial reputation

### Read Methods
- `get_reputation(agent: str) -> str`
- `is_score_applied(score_id: u256) -> str`
- `get_change_status(change_id: u256) -> str`
- `get_change_details(change_id: u256) -> str`
- `list_changes() -> str`
- `get_agent_changes(agent: str) -> str`

### Change Rules
- Only applies if score status is APPROVED
- INCREASE: new score >= current + 10
- DECREASE: new score <= current - 10
- NEUTRAL: change too small, rejected

### Security
- Does NOT trust caller-supplied JSON
- Reads score data directly from ConfidenceScorer on-chain using gl.get_contract_at()
- Reads agent from the on-chain score record, never from caller
- Each score_id can only be applied once via applied_scores map

---

## Contract Chaining

The v5 architecture uses on-chain chaining:

```
SourceNormalizer -> MultiSourceVerifier -> ConfidenceScorer -> ReputationGuardian
```

- ConfidenceScorer holds MultiSourceVerifier address
- ReputationGuardian holds ConfidenceScorer address
- Each downstream contract reads from upstream using gl.get_contract_at(Address(...)).view().get_..._data()
- The agent is propagated from the verification record through the entire chain

This prevents fabrication of approved scores, agent spoofing, double scoring, and double application.
