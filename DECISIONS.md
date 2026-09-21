# DECISIONS.md

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
Without normalization, the same URL could be written in many different ways (http://, https://, trailing slash, extra spaces, query strings), leading to inconsistent verification results and trivial bypasses of uniqueness checks.

### Solution
The SourceNormalizer and the submit path in MultiSourceVerifier clean and normalize all URLs. HTTP is upgraded to HTTPS, trailing slashes and query strings are removed, and whitespace is stripped.

### Trade-off
- Normalization adds an extra step.
- But it prevents a wide range of URL-based attacks and inconsistencies.

---

## 3. Why Deterministic Scoring Instead of LLM?

### Problem
Using an LLM to calculate the final confidence score would add cost, latency, and non-determinism.

### Solution
The ConfidenceScorer uses a simple, deterministic formula:
base_score = (verified_count / total_sources) * 100
multiplier = VERIFIED: 1.0, PARTIAL: 0.7, REJECTED: 0.3
final_score = base_score * multiplier

### Trade-off
- The formula is less flexible than an LLM.
- But it is fast, cheap, and fully predictable, which is critical for a scoring system.

---

## 4. Why Contract Chaining?

### Problem
In v1, downstream contracts (ConfidenceScorer, ReputationGuardian) trusted caller-supplied JSON for verification and score data. This allowed anyone to fabricate an approved score and change an agent's reputation without a verified evidence record.

### Solution
Each downstream contract reads its input directly from the upstream contract on-chain:
- ConfidenceScorer stores the MultiSourceVerifier address and calls get_verification_data() on-chain.
- ReputationGuardian stores the ConfidenceScorer address and calls get_score_data() on-chain.

### Why This Matters
1. Only verified on-chain data can influence reputation.
2. No caller-supplied JSON can fabricate a score.
3. Every reputation change is traceable to a verified evidence record.

### Trade-off
- Contracts are now coupled through their constructors.
- But the security improvement is essential for a reputation system.

---

## 5. Why Bind Agent to On-Chain Record?

### Problem
In v2, apply_reputation_change() still accepted agent as a parameter from caller. A caller could pair a legitimate APPROVED score_id (belonging to one agent) with an arbitrary agent, and change that agent's reputation based on evidence that was never about them.

### Solution
The agent is read from the on-chain verification record and propagated through the chain:
- MultiSourceVerifier stores agent in VerificationRecord.
- ConfidenceScorer reads agent from get_verification_data() and stores it in ConfidenceRecord.
- ReputationGuardian reads agent from get_score_data() and never accepts it from caller.

### Why This Matters
1. Agent spoofing downstream is now impossible.
2. Every reputation change is tied to the correct agent automatically.

### Trade-off
- ConfidenceRecord stores an extra field (agent).
- But the security guarantee is essential.

---

## 6. Why Prevent Double-Application?

### Problem
In v3, if someone called apply_reputation_change(score_id=1) twice, the reputation would be increased twice for the same evidence.

### Solution
Added an applied_scores map that tracks which score_ids have already been applied:
assert score_id not in self.applied_scores, "Score already applied"
self.applied_scores[score_id] = True

### Why This Matters
1. Double-application attack is prevented.
2. Each score can only affect reputation once.

### Trade-off
- One extra storage map per contract.
- But the protection is essential for any scoring system.

---

## 7. Why Independent Validator Recomputation?

### Problem
In earlier versions, the validator only checked whether the leader's status was an allowed label. It did not independently recompute verified_count, total, or verified_urls. A malicious or faulty leader could return any value for these fields, and validators would accept it.

### Solution
The validator performs five independent checks:
1. Shape validation.
2. Independent recomputation of verified_count and status.
3. Invariant check: status equals compute_status(count, total).
4. Scalar comparison of count and status.
5. Set comparison of verified URLs.

All five must pass.

### Why This Matters
1. Leader cannot lie about status: invariant is checked.
2. Leader cannot lie about verified_count: scalars are compared.
3. Leader cannot lie about which URLs were verified: sets are compared.
4. Leader cannot lie about total: total consistency is enforced.

### Trade-off
- Each validator fetches every source independently, which increases cost and time.
- But this is exactly the real cost of genuine consensus, not a design flaw.

---

## 8. Why Prevent Double-Scoring?

### Problem
If calculate_score(verification_id) was called twice for the same verification, two score records would be created, and potentially applied twice downstream.

### Solution
Added a scored_verifications map that tracks which verification_ids have already been scored:
assert verification_id not in self.scored_verifications, "Verification already scored"
self.scored_verifications[verification_id] = True

### Why This Matters
1. Each verification can only produce one score.
2. Downstream scoring is deterministic per verification.

### Trade-off
- One extra storage map.
- But the protection ensures consistency.

---

## 9. Why Bind agent to gl.message.sender_address?

### Problem
submit_evidence(agent, claim, sources) still accepted agent as a free string from caller. This meant anyone could submit evidence on behalf of another agent, breaking the trust model from the very first step.

### Solution
Removed the agent parameter entirely. The agent is now derived from str(gl.message.sender_address).

### Why This Matters
1. Every evidence submission is provably tied to the real transaction sender.
2. No caller can impersonate another agent at the submission layer.
3. The chain of trust starts from an authenticated identity.

### Trade-off
- Organizations that want to submit on behalf of another agent would need a delegation mechanism (out of scope for this version).
- But for individual agents, the security guarantee is complete.

---

## 10. Why Revert on PENDING and Avoid Consuming PENDING Records?

### Problem
In the previous version, calculate_score could be called on a still-PENDING verification, and it would mark the verification as scored even though no final status existed. This permanently consumed a PENDING record that was not ready to be scored.

### Solution
calculate_score now:
1. Reads the verification.
2. Asserts status != "PENDING" (reverts if still pending).
3. Asserts the verification was not already scored.
4. Only marks scored_verifications on the successful path, as the last line of the function.

### Why This Matters
1. A PENDING verification is never consumed.
2. Callers cannot accidentally lock a verification by calling calculate_score too early.
3. The scoring step is idempotent with respect to final status.

### Trade-off
- Callers must check status first (or catch the revert).
- But this is the correct contract behavior.

---

## 11. Why Remove initialize_reputation?

### Problem
initialize_reputation(agent, initial_score) could be called by anyone for any agent that had not been initialized yet. A malicious caller could race the real owner and claim an agent first, potentially with a hostile initial score.

### Solution
Removed initialize_reputation entirely. A lazy default of 50 is provided by:
current_reputation = self.reputation.get(agent, u256(50))

### Why This Matters
1. No one can claim an agent before its owner interacts.
2. The default is uniform across all agents (50).
3. The attack surface is removed rather than mitigated.

### Trade-off
- Callers that wanted to set a custom initial score cannot do so directly.
- But the security benefit outweighs this flexibility.

---

## 12. Why Enforce Genuinely Distinct Sources?

### Problem
The previous version accepted two URLs from the same domain (or two identical URLs) as "two independent sources". This trivially defeated the multi-source threshold.

### Solution
submit_evidence now:
1. Normalizes each URL.
2. Enforces uniqueness by normalized URL.
3. Enforces uniqueness by domain.

### Why This Matters
1. Two sources from the same domain are not independent.
2. Two identical URLs are not two sources.
3. The multi-source threshold now reflects genuine independence.

### Trade-off
- Some legitimate multi-source scenarios (e.g., two pages on the same site) are blocked.
- But this is a small price for the integrity of the threshold.

---

## Summary

| Decision | Reason |
| :--- | :--- |
| Multi-source verification | Reduces single point of failure |
| URL normalization | Prevents inconsistencies and trivial bypasses |
| Deterministic scoring | Fast, cheap, predictable |
| Contract chaining | Prevents fabrication of scores |
| Agent binding to sender | Prevents submission-layer impersonation |
| Prevent double-application | Each score applies only once |
| Independent validator recomputation | Prevents leader manipulation |
| Prevent double-scoring | Each verification produces one score |
| Identity binding via sender_address | Trust starts at the tx sender |
| Revert on PENDING | PENDING records are never consumed |
| Remove initialize_reputation | Removes early-claim attack surface |
| Enforce distinct sources | Multi-source threshold reflects real independence |

---

All decisions prioritize security, transparency, and modularity over minimalism, because a reputation system must be trustworthy above all else.
