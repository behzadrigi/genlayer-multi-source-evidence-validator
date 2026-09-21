"""
# test_reputation_guardian.py

Test suite for ReputationGuardian contract (v6).

Run these tests manually in GenLayer Studio by calling the functions
with the given inputs and comparing the outputs.
"""

# ============================================================================
# TEST T1: Get reputation for a fresh agent (lazy default of 50)
# ============================================================================

def test_get_reputation_fresh_agent():
    """
    Input: agent = "0x69d353B9178e357Ce28FD1678486A7BcCf2d65C8"
    Expected: "REPUTATION:50"

    Note: initialize_reputation was removed. The lazy default of 50 is
    provided by self.reputation.get(agent, u256(50)).
    """
    pass


# ============================================================================
# TEST T2: Apply reputation change (INCREASE path, agent from on-chain)
# ============================================================================

def test_apply_reputation_change_increase():
    """
    Input: score_id = 1
    Expected:
      - Returns change_id = 0
    Tx: 0x018599cc7cf824e4a304b23fe26b193aa1ed30c0e97563b97f25e78479cd1edd

    Note: No agent parameter. The agent is read from the on-chain score record.
    """
    pass


# ============================================================================
# TEST T3: Get reputation after change
# ============================================================================

def test_get_reputation_after_change():
    """
    Input: agent = "0x69d353B9178e357Ce28FD1678486A7BcCf2d65C8"
    Expected: "REPUTATION:100"

    Explanation:
      - Lazy default was 50
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
    Input: score_id = 1 (same as T2)
    Expected:
      - Result: ERROR
      - Error: "Score already applied"
    Tx: 0xd08a21b8cd0676a261a82a30de6ca830031cdafec2f5d39266b1357c42a85a9d
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
        "agent": "0x69d353B9178e357Ce28FD1678486A7BcCf2d65C8",
        "score_id": 1,
        "final_score": 100,
        "change_type": "INCREASE",
        "status": "APPLIED",
        "scorer_address": "0x9a9F31f2f36778cF99aB31c97AB3ace362Cf8A06"
      }
    """
    pass


# ============================================================================
# TEST T8: List all changes
# ============================================================================

def test_list_changes():
    """
    Input: None
    Expected: "0:INCREASE:APPLIED"
    """
    pass


# ============================================================================
# TEST T9: Get agent changes
# ============================================================================

def test_get_agent_changes():
    """
    Input: agent = "0x69d353B9178e357Ce28FD1678486A7BcCf2d65C8"
    Expected: "0"
    """
    pass


# ============================================================================
# DEPLOYED CONTRACT
# ============================================================================

DEPLOYED_ADDRESS = "0x4555Ac4138D751DBF52Dd75B8da6FdA1Fdcc73FE"
EXPLORER_LINK = "https://explorer-studio.genlayer.com/address/0x4555Ac4138D751DBF52Dd75B8da6FdA1Fdcc73FE"
DEPLOY_TX = "https://explorer-studio.genlayer.com/tx/0x3524889d2d9e43dd359fe32a4044cc8d2d45caf3e5155de3a12c8ee10b9a9aa1"

UPSTREAM_CONTRACT = "0x9a9F31f2f36778cF99aB31c97AB3ace362Cf8A06"


# ============================================================================
# TEST TRANSACTION LINKS
# ============================================================================

TEST_LINKS = {
    "T2_apply_reputation_change_increase":
        "https://explorer-studio.genlayer.com/tx/0x018599cc7cf824e4a304b23fe26b193aa1ed30c0e97563b97f25e78479cd1edd",
    "T4_apply_reputation_change_double":
        "https://explorer-studio.genlayer.com/tx/0xd08a21b8cd0676a261a82a30de6ca830031cdafec2f5d39266b1357c42a85a9d",
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
- It reads score directly from ConfidenceScorer on-chain.
- The agent is read from the on-chain score record, never from caller.
- apply_reputation_change REVERTS if score_id was already applied.
- initialize_reputation was removed in v6.
- A lazy default of 50 is applied on first encounter with any agent via
  self.reputation.get(agent, u256(50)).
- This design prevents any caller from claiming an agent before its owner,
  prevents agent spoofing, and prevents double-application of the same score.
"""
