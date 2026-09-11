"""
Test suite for ConfidenceScorer contract (v2).

Run these tests manually in GenLayer Studio by calling the functions
with the given inputs and comparing the outputs.
"""

# ============================================================================
# TEST T1: Calculate score by reading on-chain from MultiSourceVerifier
# ============================================================================

def test_calculate_score():
    """
    Input: verification_id = 0
    Note: This method reads verification data directly from MultiSourceVerifier
          on-chain using gl.get_contract_at(). No JSON is passed by the caller.

    Expected:
      - Returns score_id = 0
      - Status: SUCCESS

    Upstream: MultiSourceVerifier at 0x500aBa77fc751967aB02B4deB7bd88553bD75926
    """
    pass


# ============================================================================
# TEST T2: Get score
# ============================================================================

def test_get_score():
    """
    Input: evidence_id = 0
    Expected: "REJECTED:35"

    Explanation:
      - verification_id 0 had status PARTIAL with 1/2 sources verified
      - base_score = (1/2) * 100 = 50
      - multiplier for PARTIAL = 0.7
      - final_score = 50 * 0.7 = 35
      - since 35 < 50, status is REJECTED
    """
    pass


# ============================================================================
# TEST T3: Get score details
# ============================================================================

def test_get_score_details():
    """
    Input: evidence_id = 0
    Expected JSON:
      {
        "id": 0,
        "verification_id": 0,
        "trust_score": 35,
        "source_count": 2,
        "final_score": 35,
        "status": "REJECTED",
        "verifier_address": "0x500aBa77fc751967aB02B4deB7bd88553bD75926"
      }

    IMPORTANT: The verifier_address field proves that this score was
    calculated from a real on-chain verification record.
    """
    pass


# ============================================================================
# TEST T4: Get score data (NEW v2 method)
# ============================================================================

def test_get_score_data():
    """
    Input: evidence_id = 0
    Expected JSON:
      {
        "id": 0,
        "verification_id": 0,
        "trust_score": 35,
        "source_count": 2,
        "final_score": 35,
        "status": "REJECTED"
      }

    IMPORTANT: This method is used by ReputationGuardian to read data on-chain.
    """
    pass


# ============================================================================
# TEST T5: List all scores
# ============================================================================

def test_list_scores():
    """
    Input: None
    Expected: "0:REJECTED"
    """
    pass


# ============================================================================
# DEPLOYED CONTRACT (v2)
# ============================================================================

DEPLOYED_ADDRESS = "0xC8c2Eb37AF740bC4f327C4D0fe3D26BF3D6C401C"
EXPLORER_LINK = "https://explorer-studio.genlayer.com/address/0xC8c2Eb37AF740bC4f327C4D0fe3D26BF3D6C401C"
DEPLOY_TX = "https://explorer-studio.genlayer.com/tx/0x10dd6110c08a58027a8a9bc2632df57ae0c09f216e59b372ff9aae19cb045da3"

UPSTREAM_CONTRACT = "0x500aBa77fc751967aB02B4deB7bd88553bD75926"


# ============================================================================
# TEST TRANSACTION LINKS
# ============================================================================

TEST_LINKS = {
    "T1_calculate_score":
        "https://explorer-studio.genlayer.com/tx/0xa52363aa4792a93293749746e6842568ee6c0625becbbb92d5f1fc06ab0ea59e",
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
- The verifier_address field in every score record proves the source of truth.
- This design prevents any caller from fabricating an approved score.
"""
