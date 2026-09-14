"""
# test_reputation_guardian.py

Test suite for ReputationGuardian contract (v5).

Run these tests manually in GenLayer Studio by calling the functions
with the given inputs and comparing the outputs.
"""

# ============================================================================
# TEST T1: Initialize reputation for an agent
# ============================================================================

def test_initialize_reputation():
    """
    Input:
      agent: "0xTestAgent"
      initial_score: 50
    Expected:
      - Status: SUCCESS
    Tx: 0x6441fcbc40594d3fded4f78d0186a50f287aa9e22d6ecdfa561336133f09a80e
    """
    pass


# ============================================================================
# TEST T2: Get reputation (initial)
# ============================================================================

def test_get_reputation_initial():
    """
    Input: agent = "0xTestAgent"
    Expected: "REPUTATION:50"
    """
    pass


# ============================================================================
# TEST T3: Apply reputation change (INCREASE path, agent from on-chain)
# ============================================================================

def test_apply_reputation_change_increase():
    """
    Input:
      score_id: 0
    Note: This method reads score data directly from ConfidenceScorer
          on-chain using gl.get_contract_at(). No JSON is passed by the caller.
          The agent is read from the score record, not from caller input.

    Expected:
      - Returns change_id = 0
    Tx: 0x5cb5e18136bbae1f71012645ae40bd237f67d917c7223047bfc0432ccfd2dd9c
    """
    pass


# ============================================================================
# TEST T4: Get reputation after change
# ============================================================================

def test_get_reputation_after_change():
    """
    Input: agent = "0xTestAgent"
    Expected: "REPUTATION:100"

    Explanation:
      - Initial reputation was 50
      - Approved score of 100 was applied
      - INCREASE triggered since 100 > 50 + 10
      - New reputation is 100
    """
    pass


# ============================================================================
# TEST T5: Apply same score_id again (should be blocked)
# ============================================================================

def test_apply_reputation_change_double():
    """
    Input:
      score_id: 0  (same as T3)
    Expected:
      - Status: ERROR
      - Error: "Score already applied"

    Explanation:
      - applied_scores map tracks score_ids that have been applied
      - This prevents double-application attacks
    Tx: 0x1cc293005fdc1971ed83222870b3ca23ac0aad7497cb0f2eb252d17bd765661e
    """
    pass


# ============================================================================
# TEST T6: Check if score is applied
# ============================================================================

def test_is_score_applied():
    """
    Input: score_id = 0
    Expected: "APPLIED"
    """
    pass


# ============================================================================
# TEST T7: Get change status
# ============================================================================

def test_get_change_status():
    """
    Input: change_id = 0
    Expected: "INCREASE:APPLIED"
    """
    pass


# ============================================================================
# TEST T8: Get change details
# ============================================================================

def test_get_change_details():
    """
    Input: change_id = 0
    Expected JSON:
      {
        "id": 0,
        "agent": "0xTestAgent",
        "score_id": 0,
        "final_score": 100,
        "change_type": "INCREASE",
        "status": "APPLIED",
        "scorer_address": "0x0eac9A014d9ab01F038E6C32d9dC4CDa23749F4a"
      }
    """
    pass


# ============================================================================
# TEST T9: List all changes
# ============================================================================

def test_list_changes():
    """
    Input: None
    Expected: "0:INCREASE:APPLIED"
    """
    pass


# ============================================================================
# TEST T10: Get agent changes
# ============================================================================

def test_get_agent_changes():
    """
    Input: agent = "0xTestAgent"
    Expected: "0"
    """
    pass


# ============================================================================
# DEPLOYED CONTRACT
# ============================================================================

DEPLOYED_ADDRESS = "0xa08c273F5288c9924d9cE7e681802D19E254bAc7"
EXPLORER_LINK = "https://explorer-studio.genlayer.com/address/0xa08c273F5288c9924d9cE7e681802D19E254bAc7"
DEPLOY_TX = "https://explorer-studio.genlayer.com/tx/0x62afb5681904dcfed46985dca59996fe4a8faf4f8a084772c53ffe713d1af400"

UPSTREAM_CONTRACT = "0x0eac9A014d9ab01F038E6C32d9dC4CDa23749F4a"


# ============================================================================
# TEST TRANSACTION LINKS
# ============================================================================

TEST_LINKS = {
    "T1_initialize_reputation":
        "https://explorer-studio.genlayer.com/tx/0x6441fcbc40594d3fded4f78d0186a50f287aa9e22d6ecdfa561336133f09a80e",
    "T3_apply_reputation_change_increase":
        "https://explorer-studio.genlayer.com/tx/0x5cb5e18136bbae1f71012645ae40bd237f67d917c7223047bfc0432ccfd2dd9c",
    "T5_apply_reputation_change_double":
        "https://explorer-studio.genlayer.com/tx/0x1cc293005fdc1971ed83222870b3ca23ac0aad7497cb0f2eb252d17bd765661e",
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
