"""
# test_multi_source_verifier.py

Test suite for MultiSourceVerifier contract (v3).

Run these tests manually in GenLayer Studio by calling the functions
with the given inputs and comparing the outputs.
"""

# ============================================================================
# TEST T1: Submit evidence with 2 sources
# ============================================================================

def test_submit_evidence():
    """
    Input:
      agent: "0xTestAgent"
      claim: "Python is a programming language"
      sources: "https://www.python.org,https://www.w3schools.com/python/"
    Expected:
      - Returns evidence_id = 1
    Tx: 0x122dd0277d52deab87dff26c7338ee536667295bae3899a09818dfe76fdee2f5
    """
    pass


# ============================================================================
# TEST T2: Verify sources with independent validator recomputation
# ============================================================================

def test_verify_sources():
    """
    Input: evidence_id = 1
    Expected:
      - Returns true
      - Consensus: {"status": "VERIFIED", "total": 2, "verified_count": 2,
                    "verified_urls": "https://www.python.org,https://www.w3schools.com/python/"}
    Tx: 0xbc7a01826d30aade0aa559c4e4877e47143d918d237ddff0314a335e8af59be0

    Note: The validator in v3 independently:
      1. Fetches every source.
      2. Recomputes verified_count and status.
      3. Checks the invariant status == compute_status(count, total).
      4. Compares count and status against the leader.
      5. Compares the verified URL set against the leader.
    """
    pass


# ============================================================================
# TEST T3: Get verification status
# ============================================================================

def test_get_verification_status():
    """
    Input: evidence_id = 1
    Expected: "VERIFIED:2/2"
    """
    pass


# ============================================================================
# TEST T4: Get verification details
# ============================================================================

def test_get_verification_details():
    """
    Input: evidence_id = 1
    Expected JSON:
      {
        "id": 1,
        "agent": "0xTestAgent",
        "claim": "Python is a programming language",
        "sources": "https://www.python.org,https://www.w3schools.com/python/",
        "verified_count": 2,
        "total_sources": 2,
        "status": "VERIFIED"
      }
    """
    pass


# ============================================================================
# TEST T5: Get verification data (for downstream contracts)
# ============================================================================

def test_get_verification_data():
    """
    Input: evidence_id = 1
    Expected JSON:
      {
        "id": 1,
        "agent": "0xTestAgent",
        "claim": "Python is a programming language",
        "sources": "https://www.python.org,https://www.w3schools.com/python/",
        "verified_count": 2,
        "total_sources": 2,
        "status": "VERIFIED",
        "verified_urls": "https://www.python.org,https://www.w3schools.com/python/"
      }
    """
    pass


# ============================================================================
# TEST T6: List all verifications
# ============================================================================

def test_list_verifications():
    """
    Input: None
    Expected: "0:REJECTED,1:VERIFIED"
    """
    pass


# ============================================================================
# TEST T7: Get verifications by agent
# ============================================================================

def test_get_agent_verifications():
    """
    Input: agent = "0xTestAgent"
    Expected: "0,1"
    """
    pass


# ============================================================================
# DEPLOYED CONTRACT
# ============================================================================

DEPLOYED_ADDRESS = "0x8D9498DB50bEE3aCe284ecF438ea912F6a69846d"
EXPLORER_LINK = "https://explorer-studio.genlayer.com/address/0x8D9498DB50bEE3aCe284ecF438ea912F6a69846d"
DEPLOY_TX = "https://explorer-studio.genlayer.com/tx/0x890e3484c93f28c444b825b10e602ca16cb5d52418556e6994838261f696dace"


# ============================================================================
# TEST TRANSACTION LINKS
# ============================================================================

TEST_LINKS = {
    "T1_submit_evidence":
        "https://explorer-studio.genlayer.com/tx/0x122dd0277d52deab87dff26c7338ee536667295bae3899a09818dfe76fdee2f5",
    "T2_verify_sources":
        "https://explorer-studio.genlayer.com/tx/0xbc7a01826d30aade0aa559c4e4877e47143d918d237ddff0314a335e8af59be0",
}


# ============================================================================
# KEY NOTES
# ============================================================================

NOTES = """
- At least 2 sources are required for each evidence claim.
- The verifier uses gl.nondet.web.render to fetch real content from each URL.
- The verifier uses gl.vm.run_nondet_unsafe for leader/validator consensus.
- If a source cannot be fetched, it is treated as not corroborated (no error).
- The validator independently recomputes every consequential field:
  verified_count, total, status, and verified_urls.
- The agent field is stored here and propagated through the entire chain.
- get_verification_data is designed for downstream contracts to read on-chain.
"""
