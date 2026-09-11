"""
Test suite for ReputationGuardian contract (v2).

Run these tests manually in GenLayer Studio by calling the functions
with the given inputs and comparing the outputs.
"""

# ============================================================================
# TEST T1: Initialize reputation for an agent
# ============================================================================

def test_initialize_reputation():
    """
    Input:
      agent: "0xNewAgent"
      initial_score: 50
    Expected:
      - Status: SUCCESS
      - Output: null
    """
    pass


# ============================================================================
# TEST T2: Get reputation
# ============================================================================

def test_get_reputation():
    """
    Input: agent = "0xNewAgent"
    Expected: "REPUTATION:50"
    """
    pass


# ============================================================================
# TEST T3: Apply reputation change with rejected score (should fail)
# ============================================================================

def test_apply_reputation_change_rejected():
    """
    Input:
      agent: "0xNewAgent"
      score_id: 0

    Note: This method reads score data directly from ConfidenceScorer
          on-chain using gl.get_contract_at(). No JSON is passed by the caller.

    Expected:
      - Status: ERROR
      - Error: "Score not approved"

    Explanation:
      - score_id 0 in ConfidenceScorer has status REJECTED (final_score: 35)
      - since status != APPROVED, the change is rejected
    """
    pass


# ============================================================================
# TEST T4: Verify reputation unchanged after failed change
# ============================================================================

def test_verify_reputation_unchanged():
    """
    Input: agent = "0xNewAgent"
    Expected: "REPUTATION:50"

    Explanation:
      - The rejected change from T3 did not modify the reputation.
    """
    pass


# ============================================================================
# TEST T5: List all changes (should be empty)
# ============================================================================

def test_list_changes():
    """
    Input: None
    Expected: "" (empty string)

    Explanation:
      - No successful reputation changes have been recorded.
    """
    pass


# ============================================================================
# TEST T6: Get agent changes (should be empty)
# ============================================================================

def test_get_agent_changes():
    """
    Input: agent = "0xNewAgent"
    Expected: "" (empty string)
    """
    pass


# ============================================================================
# TEST T7: Get change status for non-existent change
# ============================================================================

def test_get_change_status_not_found():
    """
    Input: change_id = 0
    Expected: "NOT_FOUND"
    """
    pass


# ============================================================================
# TEST T8: Get change details for non-existent change
# ============================================================================

def test_get_change_details_not_found():
    """
    Input: change_id = 0
    Expected: "NOT_FOUND"
    """
    pass


# ============================================================================
# DEPLOYED CONTRACT (v2)
# ============================================================================

DEPLOYED_ADDRESS = "0x20d1e42064Bc02dE8421b3925448bFEdC82BF49b"
EXPLORER_LINK = "https://explorer-studio.genlayer.com/address/0x20d1e42064Bc02dE8421b3925448bFEdC82BF49b"
DEPLOY_TX = "https://explorer-studio.genlayer.com/tx/0xc16b6d48f8768f2de162629e294c132a7bdb9a398255aabe79543a5aad897567"

UPSTREAM_CONTRACT = "0xC8c2Eb37AF740bC4f327C4D0fe3D26BF3D6C401C"


# ============================================================================
# TEST TRANSACTION LINKS
# ============================================================================

TEST_LINKS = {
    "T1_initialize_reputation":
        "https://explorer-studio.genlayer.com/tx/0x622ca6cdbd832065b9595cf8bf01abe1e34e19c474cb6e49a562f05843cd4136",
    "T3_apply_reputation_change_rejected":
        "https://explorer-studio.genlayer.com/tx/0xb7232ca781f1487eb34137fee5d8da53f686d36f3975fe5a75629ffcba27814c",
}


# ============================================================================
# CHANGE RULES
# ============================================================================

CHANGE_RULES = """
- Only applies if score status is APPROVED.
- INCREASE: new_score >= current_reputation + 10
- DECREASE: new_score <= current_reputation - 10
- NEUTRAL:  change too small, rejected with error
"""


# ============================================================================
# KEY NOTES
# ============================================================================

NOTES = """
- This contract does NOT accept score JSON from the caller.
- Instead, it reads score data directly from ConfidenceScorer
  on-chain using gl.get_contract_at(Address(...)).view().get_score_data().
- The scorer_address field in every change record proves the source of truth.
- This design prevents any caller from fabricating an approved score
  and applying an illegitimate reputation change.
"""
