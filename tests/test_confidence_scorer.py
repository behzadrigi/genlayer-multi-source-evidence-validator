"""
# test_confidence_scorer.py

Test suite for ConfidenceScorer contract.

Run these tests manually in GenLayer Studio by calling the functions
with the given inputs and comparing the outputs.
"""

# ============================================================================
# TEST T1: Calculate score by reading on-chain from MultiSourceVerifier
# ============================================================================

def test_calculate_score():
    """
    Input: verification_id = 3
    Note: This method reads verification data directly from MultiSourceVerifier
          on-chain using gl.get_contract_at(). No JSON is passed by the caller.

    Expected:
      - Returns score_id = 1
    Tx: 0xeb631b1096fa356aff3af572aa6a912afcce64ac4c7f87df27daa10da07d2935

    Upstream: MultiSourceVerifier at 0x500aBa77fc751967aB02B4deB7bd88553bD75926
    """
    pass


# ============================================================================
# TEST T2: Get score (APPROVED)
# ============================================================================

def test_get_score():
    """
    Input: evidence_id = 1
    Expected: "APPROVED:100"

    Explanation:
      - verification_id 3 had status VERIFIED with 2/2 sources verified
      - base_score = (2/2) * 100 = 100
      - multiplier for VERIFIED = 1.0
      - final_score = 100
      - since 100 >= 50, status is APPROVED
    """
    pass


# ============================================================================
# TEST T3: Get score details (agent read from on-chain)
# ============================================================================

def test_get_score_details():
    """
    Input: evidence_id = 1
    Expected JSON:
      {
        "id": 1,
        "verification_id": 3,
        "agent": "0xNewAgent",
        "trust_score": 100,
        "source_count": 2,
        "final_score": 100,
        "status": "APPROVED",
        "verifier_address": "0x500aBa77fc751967aB02B4deB7bd88553bD75926"
      }

    IMPORTANT: The agent field is read from the on-chain verification record,
    not from caller input. This prevents agent spoofing.
    """
    pass


# ============================================================================
# TEST T4: Get score data (used by ReputationGuardian)
# ============================================================================

def test_get_score_data():
    """
    Input: evidence_id = 1
    Expected JSON:
      {
        "id": 1,
        "verification_id": 3,
        "agent": "0xNewAgent",
        "trust_score": 100,
        "source_count": 2,
        "final_score": 100,
        "status": "APPROVED"
      }

    IMPORTANT: This method is used by ReputationGuardian to read data on-chain,
    including the agent field.
    """
    pass


# ============================================================================
# TEST T5: List all scores
# ============================================================================

def test_list_scores():
    """
    Input: None
    Expected: contains "1:APPROVED"
    """
    pass


# ============================================================================
# DEPLOYED CONTRACT
# ============================================================================

DEPLOYED_ADDRESS = "0xaAFfC3090370149b1187268475A678692D49Ef40"
EXPLORER_LINK = "https://explorer-studio.genlayer.com/address/0xaAFfC3090370149b1187268475A678692D49Ef40"
DEPLOY_TX = "https://explorer-studio.genlayer.com/tx/0x1d25fc8b35e42929405fa84efada4db97e1fad0bc3090058375a23747b4258b6"

UPSTREAM_CONTRACT = "0x500aBa77fc751967aB02B4deB7bd88553bD75926"


# ============================================================================
# TEST TRANSACTION LINKS
# ============================================================================

TEST_LINKS = {
    "T1_calculate_score":
        "https://explorer-studio.genlayer.com/tx/0xeb631b1096fa356aff3af572aa6a912afcce64ac4c7f87df27daa10da07d2935",
}


# ============================================================================
# SCORING FORMULA
# ============================================================================

SCORING_FORMULA = """
base_score = (verified_count / total_sources) * 100

multiplier:
  - VERIFIED: 1.0
  - PARTIAL:  0.7
  - REJECTED: 0.3

final_score = int(base_score * multiplier)
status = APPROVED if final_score >= 50 else REJECTED
"""


# ============================================================================
# KEY NOTES
# ============================================================================

NOTES = """
- This contract does NOT accept verification JSON from the caller.
- Instead, it reads verification data directly from MultiSourceVerifier
  on-chain using gl.get_contract_at(Address(...)).view().get_verification_data().
- The agent field is read from the on-chain verification record and stored
  in ConfidenceRecord. This prevents agent spoofing.
- The verifier_address field in every score record proves the source of truth.
- This design prevents any caller from fabricating an approved score.
"""
