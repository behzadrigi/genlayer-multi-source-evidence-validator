# Contracts

## 1. SourceNormalizer

**Pattern:** fully deterministic — no LLM, no consensus needed.

**Purpose:** the entry gate for every source URL. Cleans and normalizes a raw URL,
extracts its domain, rejects blocked domains, checks whitelist membership, and
computes a 0-100 trust score.

**Public methods**
- `normalize_source(raw_url: str) -> u256` — normalizes, validates, and stores a
  source; returns its `evidence_id`.
- `get_source_status(evidence_id) -> str`
- `get_source_details(evidence_id) -> str` (JSON)
- `list_sources() -> str`

**Safety properties**
- A blocked domain (`localhost`, `127.0.0.1`, `example.com`, `pastebin.com`) can never
  be normalized — `normalize_source` reverts.
- An unparseable URL can never be stored — `normalize_source` reverts.
- Trust score is bounded to `[0, 100]` by construction.

---

## 2. MultiSourceVerifier

**Pattern:** non-deterministic, Equivalence-Principle consensus (`gl.vm.run_nondet_unsafe`
with a `leader_fn`/`validator_fn` pair), web-grounded.

**Purpose:** the core of the suite. Takes a claim plus at least two source URLs,
fetches every URL live via `gl.nondet.web.render`, and asks the model whether each
page's content corroborates the claim. The result (`status`, `verified_count`) is only
written to state once independent validators, each re-running the same fetch-and-judge
routine, agree on both fields.

**Public methods**
- `submit_evidence(agent, claim, sources) -> u256` — requires ≥2 comma-separated,
  URL-format-valid sources; returns `evidence_id`.
- `verify_sources(evidence_id) -> bool` — runs the consensus check; can only be called
  once per evidence item (`status` must still be `PENDING`).
- `get_verification_status(evidence_id) -> str`
- `get_verification_details(evidence_id) -> str` (JSON)
- `list_verifications() -> str`
- `get_agent_verifications(agent) -> str`

**Safety properties**
- `verify_sources` cannot be called twice on the same evidence item.
- The verification result is never taken from caller input — every validator
  independently re-fetches every source and re-runs the judgment; a validator that
  gets a different `status` or `verified_count` rejects the leader's result.
- `status` is always one of `VERIFIED` (all sources corroborate), `PARTIAL` (≥50%
  corroborate), or `REJECTED` (<50%).
- A source that fails to fetch is treated as not-corroborated rather than causing the
  whole transaction to fail.

---

## 3. ConfidenceScorer

**Pattern:** fully deterministic.

**Purpose:** converts a `MultiSourceVerifier` result into a single 0-100 confidence
number and an `APPROVED`/`REJECTED` decision, so downstream contracts (and users) get
one comparable figure instead of a raw status string.

**Formula:** `final_score = (verified_count / total_sources * 100) * status_multiplier`,
where `status_multiplier` is `1.0` for `VERIFIED`, `0.7` for `PARTIAL`, `0.3` for
anything else. `APPROVED` requires `final_score >= 50`.

**Public methods**
- `calculate_score(verification_id, verification_details) -> u256`
- `get_score(evidence_id) -> str`
- `get_score_details(evidence_id) -> str` (JSON)
- `list_scores() -> str`

**Safety properties**
- `final_score` is always clamped to `[0, 100]`.
- `status` is a pure function of `final_score`, so it can't diverge from the number
  shown alongside it.

---

## 4. ReputationGuardian

**Pattern:** fully deterministic — deliberately no LLM/consensus, since applying an
already-approved numeric score to a reputation ledger is bookkeeping, not judgment.

**Purpose:** applies an `INCREASE`/`DECREASE` to an agent's on-chain reputation once
(and only once) a `ConfidenceScorer` result is `APPROVED`.

**Public methods**
- `initialize_reputation(agent, initial_score)`
- `apply_reputation_change(agent, score_id, score_details) -> u256`
- `get_reputation(agent) -> str`
- `get_change_status(change_id) -> str`
- `get_change_details(change_id) -> str` (JSON)
- `list_changes() -> str`
- `get_agent_changes(agent) -> str`

**Safety properties**
- `apply_reputation_change` reverts outright ("Score not approved") unless
  `score_details.status == "APPROVED"` — a `REJECTED` score can never move
  reputation, confirmed by tests T3/T5 in the test reports.
- A change smaller than 10 points is classified `NEUTRAL` and is rejected rather than
  silently applied, so trivial fluctuations never get recorded as a reputation event.
- New agents default to a reputation of 50 the first time they're read or changed.
