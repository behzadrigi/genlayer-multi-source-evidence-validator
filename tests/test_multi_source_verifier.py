"""
# test_multi_source_verifier.py

Test suite for MultiSourceVerifier contract.

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
      claim: "Bitcoin is a cryptocurrency"
      sources: "https://coinmarketcap.com,https://en.wikipedia.org/wiki/Bitcoin"
    Expected:
      - Returns evidence_id = 3
    Tx: 0xbd8505989a1c724b2c49816230023e5e2e2478ee8f013e743048b257ce71b4c9
    """
    pass


# ============================================================================
# TEST T2: Verify sources with consensus (VERIFIED)
# ============================================================================

def test_verify_sources():
    """
    Input: evidence_id = 3
    Expected:
      - Returns true
      - Consensus: {"status": "VERIFIED", "total": 2, "verified_count": 2,
                    "verified_urls": "https://coinmarketcap.com,https://en.wikipedia.org/wiki/Bitcoin"}
    Tx: 0x86a8d7a47e7a95bf393036d34d9dd55315abb89bb2132bf4a87146ff60170bb9
    """
    pass


# ============================================================================
# TEST T3: Get verification data
# ============================================================================

def test_get_verification_data():
    """
    Input: evidence_id = 3
    Expected JSON:
      {
        "id": 3,
        "agent": "0xNewAgent",
        "claim": "Bitcoin is a cryptocurrency",
        "sources": "https://coinmarketcap.com,https://en.wikipedia.org/wiki/Bitcoin",
        "verified_count": 2,
        "total_sources": 2,
        "status": "VERIFIED",
        "verified_urls": "https://coinmarketcap.com,https://en.wikipedia.org/wiki/Bitcoin"
      }
    """
    pass


# ============================================================================
# TEST T4: Get verification status
# ============================================================================

def test_get_verification_status():
    """
    Input: evidence_id = 3
    Expected: "VERIFIED:2/2"
    """
    pass


# ============================================================================
# TEST T5: List all verifications
# ============================================================================

def test_list_verifications():
    """
    Input: None
    Expected: contains "3:VERIFIED"
    """
    pass


# ============================================================================
# TEST T6: Get verifications by agent
# ============================================================================

def test_get_agent_verifications():
    """
    Input: agent = "0xNewAgent"
    Expected: contains "3"
    """
    pass


# ============================================================================
# TEST T7: Get verification details
# ============================================================================

def test_get_verification_details():
    """
    Input: evidence_id = 3
    Expected JSON:
      {
        "id": 3,
        "agent": "0xNewAgent",
        "claim": "Bitcoin is a cryptocurrency",
        "sources": "https://coinmarketcap.com,https://en.wikipedia.org/wiki/Bitcoin",
        "verified_count": 2,
        "total_sources": 2,
        "status": "VERIFIED"
      }
    """
    pass


# ============================================================================
# DEPLOYED CONTRACT
# ============================================================================

DEPLOYED_ADDRESS = "0x500aBa77fc751967aB02B4deB7bd88553bD75926"
EXPLORER_LINK = "https://explorer-studio.genlayer.com/address/0x500aBa77fc751967aB02B4deB7bd88553bD75926"
DEPLOY_TX = "https://explorer-studio.genlayer.com/tx/0xf82797008b693975ea658193538d7b6d95f6222ace271d27cfe4bb71d0fa21c4"


# ============================================================================
# TEST TRANSACTION LINKS
# ============================================================================

TEST_LINKS = {
    "T1_submit_evidence":
        "https://explorer-studio.genlayer.com/tx/0xbd8505989a1c724b2c49816230023e5e2e2478ee8f013e743048b257ce71b4c9",
    "T2_verify_sources":
        "https://explorer-studio.genlayer.com/tx/0x86a8d7a47e7a95bf393036d34d9dd55315abb89bb2132bf4a87146ff60170bb9",
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
- The agent field is stored here and propagated through the entire chain.
"""
