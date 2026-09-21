"""
# test_multi_source_verifier.py

Test suite for MultiSourceVerifier contract (v4).

Run these tests manually in GenLayer Studio by calling the functions
with the given inputs and comparing the outputs.
"""

# ============================================================================
# TEST T1: Submit evidence (no agent parameter)
# ============================================================================

def test_submit_evidence():
    """
    Input:
      claim: "Python is a programming language"
      sources: "https://www.python.org,https://www.w3schools.com/python/"
    Expected:
      - Returns evidence_id = 0
      - agent is derived from gl.message.sender_address
    Tx: 0x077a106c7dcc2e298f0008b855231bfba38965bba2fa7beae1b2f82b21b65937
    """
    pass


# ============================================================================
# TEST T2: Get verification details (verify agent)
# ============================================================================

def test_get_verification_details():
    """
    Input: evidence_id = 0
    Expected JSON:
      {
        "id": 0,
        "agent": "0x69d353B9178e357Ce28FD1678486A7BcCf2d65C8",
        "claim": "Python is a programming language",
        "sources": "https://www.python.org,https://www.w3schools.com/python",
        "verified_count": 0,
        "total_sources": 2,
        "status": "PENDING"
      }
    Note: agent is the real transaction sender, not a caller-supplied string.
    """
    pass


# ============================================================================
# TEST T3: Duplicate source URL rejection
# ============================================================================

def test_duplicate_url_rejection():
    """
    Input:
      claim: "Test claim"
      sources: "https://www.python.org,https://www.python.org"
    Expected:
      - Result: ERROR
      - Error: "Duplicate source URL"
    Tx: 0x718acc1dcf8c219a4879d1a4d37bf6acbdbd66cf2c7bc4f6a25147793bdd0680
    """
    pass


# ============================================================================
# TEST T4: Duplicate domain rejection
# ============================================================================

def test_duplicate_domain_rejection():
    """
    Input:
      claim: "Test claim"
      sources: "https://www.python.org/about,https://www.python.org/downloads"
    Expected:
      - Result: ERROR
      - Error: "Sources must come from independent domains"
    Tx: 0x1c2306cfbbd44f1b3658d1a0d8c9ff86cf632a9aa4a61a735edac452a3ab9a59
    """
    pass


# ============================================================================
# TEST T5: Verify sources with independent validator recomputation
# ============================================================================

def test_verify_sources_verified():
    """
    Input: evidence_id = 0
    Expected:
      - Returns true
      - Consensus: {"status": "VERIFIED", "total": 2, "verified_count": 2,
                    "verified_urls": "https://www.python.org,https://www.w3schools.com/python"}
    Tx: 0xd8c7f5251bcf39b1d8477aa7e694444506b89bdd655d8752a523f8cba72c68d2
    """
    pass


# ============================================================================
# TEST T6: Submit pending evidence (for PENDING consumption test)
# ============================================================================

def test_submit_pending_evidence():
    """
    Input:
      claim: "Test pending claim"
      sources: "https://www.example.org,https://www.wikipedia.org"
    Expected:
      - Returns evidence_id = 1 with status PENDING
    Tx: 0x8dc721ab949a6267885bb71334e56ea674d2443b294f0623390807da639fce76
    """
    pass


# ============================================================================
# TEST T7: Verify pending evidence (returns REJECTED)
# ============================================================================

def test_verify_sources_rejected():
    """
    Input: evidence_id = 1
    Expected:
      - Returns true
      - Consensus: {"status": "REJECTED", "total": 2, "verified_count": 0, "verified_urls": ""}
    Tx: 0x4d2d9602fa032b055843b91b21bfd7ff5d6a21500c6932455b2bb6176168bc08
    """
    pass


# ============================================================================
# TEST T8: Get verification status
# ============================================================================

def test_get_verification_status():
    """
    Input: evidence_id = 0
    Expected: "VERIFIED:2/2"
    """
    pass


# ============================================================================
# DEPLOYED CONTRACT
# ============================================================================

DEPLOYED_ADDRESS = "0xFA4331084CE100F086bDCFcCe16028BFbd374BcF"
EXPLORER_LINK = "https://explorer-studio.genlayer.com/address/0xFA4331084CE100F086bDCFcCe16028BFbd374BcF"
DEPLOY_TX = "https://explorer-studio.genlayer.com/tx/0xd53785753a922cf5b28b2ba87457243ce63c0fc27bee9fa54867ad82400d29b0"


# ============================================================================
# TEST TRANSACTION LINKS
# ============================================================================

TEST_LINKS = {
    "T1_submit_evidence":
        "https://explorer-studio.genlayer.com/tx/0x077a106c7dcc2e298f0008b855231bfba38965bba2fa7beae1b2f82b21b65937",
    "T3_duplicate_url":
        "https://explorer-studio.genlayer.com/tx/0x718acc1dcf8c219a4879d1a4d37bf6acbdbd66cf2c7bc4f6a25147793bdd0680",
    "T4_duplicate_domain":
        "https://explorer-studio.genlayer.com/tx/0x1c2306cfbbd44f1b3658d1a0d8c9ff86cf632a9aa4a61a735edac452a3ab9a59",
    "T5_verify_verified":
        "https://explorer-studio.genlayer.com/tx/0xd8c7f5251bcf39b1d8477aa7e694444506b89bdd655d8752a523f8cba72c68d2",
    "T6_submit_pending":
        "https://explorer-studio.genlayer.com/tx/0x8dc721ab949a6267885bb71334e56ea674d2443b294f0623390807da639fce76",
    "T7_verify_rejected":
        "https://explorer-studio.genlayer.com/tx/0x4d2d9602fa032b055843b91b21bfd7ff5d6a21500c6932455b2bb6176168bc08",
}


# ============================================================================
# KEY NOTES
# ============================================================================

NOTES = """
- submit_evidence has no agent parameter. The agent is derived from
  gl.message.sender_address, so no caller can submit on behalf of another agent.
- URLs are normalized and enforced to be unique both by URL and by domain.
- At least 2 independent sources are required.
- The validator independently recomputes verified_count, total, status, and
  verified_urls, and checks the invariant status == compute_status(count, total).
- If a source cannot be fetched, it is treated as not corroborated (no error).
- The agent field is stored in VerificationRecord and propagated through the chain.
"""
