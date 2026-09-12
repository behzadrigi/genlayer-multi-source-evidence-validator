"""
# test_reputation_guardian.py

Test suite for ReputationGuardian contract.

Run these tests manually in GenLayer Studio by calling the functions
with the given inputs and comparing the outputs.
"""

# ============================================================================
# TEST T1: Initialize reputation for an agent
# ============================================================================

def test_initialize_reputation():
    """
    Input:
      agent: "0xNewAgent2"
      initial_score: 50
    Expected:
      - Status: SUCCESS
    Tx: 0x9556e990518991e845cbfb9de8e68f5e320af0bc85f870c663a47a6e3a14f6be
    """
    pass


# ============================================================================
# TEST T2: Apply reputation change (INCREASE path, agent from on-chain)
# ============================================================================

def test_apply_reputation_change_increase():
    """
    Input:
      score_id: 1
    Note: This method reads score data directly from ConfidenceScorer
          on-chain using gl.get_contract_at(). No JSON is passed by the caller.
          The agent is read from the score record, not from caller input.

    Expected:
      - Returns change_id = 0
    Tx: 0x3e1c6a70421d56255f28a2b6f66ce19450a4c921c9f455640f47fba4b1106afc
    """
    pass


# ============================================================================
# TEST T3: Get reputation after change
# ============================================================================

def test_get_reputation_after_change():
    """
    Input: agent = "0xNewAgent"
    Expected: "REPUTATION:100"

    Explanation:
      - Initial reputation was 50
      - Approved score of 100 was applied
      - INCREASE triggered since 100 > 50 + 10
      - New reputation is 100
    """
    pass


# ============================================================================
# TEST T4: Apply same score_id again (should be blocked)
# ============================================================================

def test_apply_reputation_change_double():
    """
    Input:
      score_id: 1  (same as T2)
    Expected:
      - Status: ERROR
      - Error: "Score already applied"

    Explanation:
      - applied_scores map tracks score_ids that have been applied
      - This prevents double-application attacks
    Tx: 0x50cb7cccaed5cd7cc43064a019726f51f4f8c7f3b2800cdee7dadf8f1b1abcd3
    """
    pass


# ============================================================================
# TEST T5: Check if score is applied
# ============================================================================

def test_is_score_applied():
    """
    Input: score_id = 1
    Expected: "APPLIED"
    """
    pass


# ============================================================================
# TEST T6: Get change status
# ============================================================================

def test_get_change_status():
    """
    Input: change_id = 0
    Expected: "INCREASE:APPLIED"
    """
    pass


# ============================================================================
# TEST T7: Get change details
# ============================================================================

def test_get_change_details():
    """
    Input: change_id = 0
    Expected JSON:
      {
        "id": 0,
        "agent": "0xNewAgent",
        "score_id": 1,
        "final_score": 100,
        "change_type": "INCREASE",
        "status": "APPLIED",
        "scorer_address": "0xaAFfC3090370149b1187268475A678692D49Ef40"
      }
    """
    pass


# ============================================================================
# TEST T8: List all changes
# ============================================================================

def test_list_changes():
    """
    Input: None
    Expected: contains "0:INCREASE:APPLIED"
    """
    pass


# ============================================================================
# TEST T9: Get agent changes
# ============================================================================

def test_get_agent_changes():
    """
    Input: agent = "0xNewAgent"
    Expected: contains "0"
    """
    pass


# ============================================================================
# DEPLOYED CONTRACT
# ============================================================================

DEPLOYED_ADDRESS = "0x96e280F36f0a430F41E8140945c7b238042e1Faf"
EXPLORER_LINK = "https://explorer-studio.genlayer.com/address/0x96e280F36f0a430F41E8140945c7b238042e1Faf"
DEPLOY_TX = "https://explorer-studio.genlayer.com/tx/0xc2eaf0aadbcd0630a9f781589656991627cfd71285098fcfa67ac8f1b71a4ac0"

UPSTREAM_CONTRACT = "0xaAFfC3090370149b1187268475A678692D49Ef40"


# ============================================================================
# TEST TRANSACTION LINKS
# ============================================================================

TEST_LINKS = {
    "T1_initialize_reputation":
        "https://explorer-studio.genlayer.com/tx/0x9556e990518991e845cbfb9de8e68f5e320af0bc85f870c663a47a6e3a14f6be",
    "T2_apply_reputation_change_increase":
        "https://explorer-studio.genlayer.com/tx/0x3e1c6a70421d56255f28a2b6f66ce19450a4c921c9f455640f47fba4b1106afc",
    "T4_apply_reputation_change_double":
        "https://explorer-studio.genlayer.com/tx/0x50cb7cccaed5cd7cc43064a019726f51f4f8c7f3b2800cdee7dadf8f1b1abcd3",
}


# ============================================================================
# CHANGE RULES
# ============================================================================

CHANGE_RULES = """
- Only applies if score status is APPROVED.
- INCREASE: new_score >= current_reputation + 10
- DECREASE: new_score <= current_reputation - 10
- NEUTRAL:  change too small, rejected with error
- Each score_id can only be applied once.
"""


# ============================================================================
# KEY NOTES
# ============================================================================

NOTES = """
- This contract does NOT accept score JSON from the caller.
- It reads score data directly from ConfidenceScorer on-chain using
  gl.get_contract_at(Address(...)).view().get_score_data().
- The agent field is read from the on-chain score record, never from caller.
  This prevents agent spoofing attacks.
- The applied_scores map prevents double-application of the same score_id.
- The scorer_address field in every change record proves the source of truth.
- This design prevents any caller from fabricating an approved score,
  spoofing an agent, or applying the same score twice.
"""
