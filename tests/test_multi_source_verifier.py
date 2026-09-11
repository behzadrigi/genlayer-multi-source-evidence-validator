"""
Test suite for MultiSourceVerifier contract (v2).

Run these tests manually in GenLayer Studio by calling the functions
with the given inputs and comparing the outputs.
"""

# ============================================================================
# TEST T1: Submit evidence with 2 sources
# ============================================================================

def test_submit_evidence():
    """
    Input:
      agent: "0xNewAgent"
      claim: "Bitcoin is the largest cryptocurrency by market cap"
      sources: "https://coinmarketcap.com,https://coingecko.com"
    Expected:
      - Returns evidence_id = 0
      - Status: SUCCESS
    """
    pass


# ============================================================================
# TEST T2: Verify sources with consensus
# ============================================================================

def test_verify_sources():
    """
    Input: evidence_id = 0 (from T1)
    Expected:
      - Returns true
      - Consensus: {"status": "PARTIAL", "total": 2, "verified_count": 1,
                    "verified_urls": "https://coinmarketcap.com"}
    """
    pass


# ============================================================================
# TEST T3: Get verification data (NEW v2 method)
# ============================================================================

def test_get_verification_data():
    """
    Input: evidence_id = 0
    Expected JSON:
      {
        "id": 0,
        "agent": "0xNewAgent",
        "claim": "Bitcoin is the largest cryptocurrency by market cap",
        "sources": "https://coinmarketcap.com,https://coingecko.com",
        "verified_count": 1,
        "total_sources": 2,
        "status": "PARTIAL",
        "verified_urls": "https://coinmarketcap.com"
      }

    IMPORTANT: This method is used by ConfidenceScorer to read data on-chain.
    """
    pass


# ============================================================================
# TEST T4: Get verification status
# ============================================================================

def test_get_verification_status():
    """
    Input: evidence_id = 0
    Expected: "PARTIAL:1/2"
    """
    pass


# ============================================================================
# TEST T5: List all verifications
# ============================================================================

def test_list_verifications():
    """
    Input: None
    Expected: "0:PARTIAL"
    """
    pass


# ============================================================================
# TEST T6: Get verifications by agent
# ============================================================================

def test_get_agent_verifications():
    """
    Input: agent = "0xNewAgent"
    Expected: "0"
    """
    pass


# ============================================================================
# TEST T7: Get verification details
# ============================================================================

def test_get_verification_details():
    """
    Input: evidence_id = 0
    Expected JSON:
      {
        "id": 0,
        "agent": "0xNewAgent",
        "claim": "Bitcoin is the largest cryptocurrency by market cap",
        "sources": "https://coinmarketcap.com,https://coingecko.com",
        "verified_count": 1,
        "total_sources": 2,
        "status": "PARTIAL"
      }
    """
    pass


# ============================================================================
# DEPLOYED CONTRACT (v2)
# ============================================================================

DEPLOYED_ADDRESS = "0x500aBa77fc751967aB02B4deB7bd88553bD75926"
EXPLORER_LINK = "https://explorer-studio.genlayer.com/address/0x500aBa77fc751967aB02B4deB7bd88553bD75926"
DEPLOY_TX = "https://explorer-studio.genlayer.com/tx/0xf82797008b693975ea658193538d7b6d95f6222ace271d27cfe4bb71d0fa21c4"


# ============================================================================
# TEST TRANSACTION LINKS
# ============================================================================

TEST_LINKS = {
    "T1_submit_evidence":
        "https://explorer-studio.genlayer.com/tx/0x79fbfff7824279f18267a72c644d3b1b2293ae71ff6fb16f88b254e77465e487",
    "T2_verify_sources":
        "https://explorer-studio.genlayer.com/tx/0xaeebeb932d40d1829b24836ae3e45ae01fce3cd41355ff8751c5a71d9a02c887",
}


# ============================================================================
# KEY NOTES
# ============================================================================

NOTES = """
- At least 2 sources are required for each evidence claim.
- The verifier uses gl.nondet.web.render to fetch real content from each URL.
- The verifier uses gl.vm.run_nondet_unsafe for leader/validator consensus.
- If a source cannot be fetched, it is treated as not corroborated (no error).
- The get_verification_data method is specifically designed for downstream
  contracts to read data on-chain without trusting caller-supplied JSON.
"""
