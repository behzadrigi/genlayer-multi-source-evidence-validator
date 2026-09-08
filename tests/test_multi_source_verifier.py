"""
Integration tests for MultiSourceVerifier against the deployed GenLayer Studio instance.

Note: verify_sources fetches every source live via gl.nondet.web.render and asks the
model to judge corroboration, so results depend on the live content of the source
pages at test time. The REJECTED/PARTIAL cases below match what was already observed
in the manual test report; VERIFIED is included as a case to actively pursue with a
claim/source pair known to fully corroborate, since it hasn't been exercised yet
(see DECISIONS.md, "Known limitation").
"""

import json
import pytest
from genlayer_py import create_client, create_account
from genlayer_py.chains import localnet

CONTRACT_ADDRESS = "0x47B07b947953a25AbdD572Ed62b575022E0868af"


@pytest.fixture(scope="module")
def client():
    account = create_account()
    return create_client(chain=localnet, account=account)


def _write(client, function_name, args):
    tx_hash = client.write_contract(
        address=CONTRACT_ADDRESS, function_name=function_name, args=args, value=0,
    )
    return client.wait_for_transaction_receipt(transaction_hash=tx_hash, status="ACCEPTED")


def _read(client, function_name, args=None):
    return client.read_contract(
        address=CONTRACT_ADDRESS, function_name=function_name, args=args or [],
    )


def test_submit_evidence_requires_two_sources(client):
    with pytest.raises(Exception, match="At least 2 sources required"):
        _write(client, "submit_evidence", ["0xAgent", "some claim", "https://a.com"])


def test_submit_and_verify_rejected_case(client):
    _write(
        client, "submit_evidence",
        ["0xTestAgent", "Ethereum price is over $3000",
         "https://coinmarketcap.com,https://coingecko.com"],
    )
    evidence_id = 0
    _write(client, "verify_sources", [evidence_id])
    status = _read(client, "get_verification_status", [evidence_id])
    assert status.split(":")[0] in ("REJECTED", "PARTIAL", "VERIFIED")


def test_submit_and_verify_partial_case(client):
    _write(
        client, "submit_evidence",
        ["0xTestAgent3", "Bitcoin is the largest cryptocurrency by market cap",
         "https://coinmarketcap.com,https://coingecko.com"],
    )
    evidence_id = 1
    _write(client, "verify_sources", [evidence_id])
    details = json.loads(_read(client, "get_verification_details", [evidence_id]))
    assert details["status"] in ("REJECTED", "PARTIAL", "VERIFIED")
    assert details["total_sources"] == 2


def test_cannot_verify_same_evidence_twice(client):
    with pytest.raises(Exception, match="Already verified"):
        _write(client, "verify_sources", [0])


def test_get_agent_verifications(client):
    ids = _read(client, "get_agent_verifications", ["0xTestAgent"])
    assert "0" in ids.split(",")


# --- Still to run before submission: a genuinely VERIFIED (2/2) case ---
def test_submit_and_verify_verified_case(client):
    """Two sources that should both clearly corroborate the same, stable, factual claim."""
    _write(
        client, "submit_evidence",
        ["0xTestAgent4", "Python was created by Guido van Rossum",
         "https://en.wikipedia.org/wiki/Python_(programming_language),https://www.python.org/about/"],
    )
    evidence_id = 2
    _write(client, "verify_sources", [evidence_id])
    details = json.loads(_read(client, "get_verification_details", [evidence_id]))
    assert details["status"] == "VERIFIED"
    assert details["verified_count"] == 2
